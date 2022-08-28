""" Handles all api routing """

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    make_response,
)
import re
import jwt
from sqlalchemy import or_
from flask_bcrypt import Bcrypt
from flask_restful import Api
from datetime import datetime
import os
import random
from src.resources.users import User, UserList
from src.resources.authentication import (
    JWTDistributor,
    ValidationEmailSender,
    TokenValidator,
    FacebookLogin,
    GoogleLogin,
)
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    set_access_cookies,
    get_jwt_identity,
    create_refresh_token,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from src.resources.notifications import Notification, NotificationList
import src.models as models
from src.database import db_session
from functools import wraps
from src.views import permission
import csv
import pandas as pd
import os

client_blueprint = Blueprint("client_blueprint", __name__)


bcrypt = Bcrypt()


@client_blueprint.route("/new_client")
@jwt_required()
@permission("client", "client_add")
def new_client():
    user_id = get_jwt_identity()
    user = (
        db_session.query(models.Users).filter(models.Users.id == user_id).one_or_none()
    )
    return render_template("add_client_data.html", user=user)


@client_blueprint.route("/add_client", methods=["GET", "POST"])
@jwt_required()
@permission("client", "client_add")
def add_client():
    try:
        user_id = get_jwt_identity()
        user = (
            db_session.query(models.Users)
            .filter(models.Users.id == user_id)
            .one_or_none()
        )
        if request.method == "POST":
            print(request.form)
            crn = request.form["crn"]
            company = request.form["company"]
            data = request.form["data"]
            note = request.form["note"]
            trading_info = request.form["trading_info"]
            capital = request.form["capital"]
            capital_profit = request.form["capital_profit"]
            status = request.form["status"]
            if status == "True":
                status = True
            else:
                status = False
            added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            add_value = models.Clients(
                crn=crn,
                company=company,
                data=data,
                note=note,
                trading_info=trading_info,
                status=status,
                capital=capital,
                capital_profit=capital_profit,
                date_created=added_at,
                date_updated=None,
            )
            db_session.add(add_value)
            db_session.flush()

    except Exception as e:
        print(e)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
    return redirect(url_for("client_blueprint.view_clients"))


@client_blueprint.route("/profit_file")
@jwt_required()
@permission("client", "client_add")
def profit_file():
    user_id = get_jwt_identity()
    user = (
        db_session.query(models.Users).filter(models.Users.id == user_id).one_or_none()
    )
    return render_template("profit_file.html", user=user)


@client_blueprint.route("/add_profit", methods=["GET", "POST"])
@jwt_required()
@permission("client", "client_add")
def add_profit():
    try:
        user_id = get_jwt_identity()
        if request.method == "POST":
            file = request.files["profit_file"]
            profit_date = (
                request.form["profit_date"]
                if request.form["profit_date"] != ""
                else None
            )
            added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(file)
            filename = file.filename
            print(filename)
            file.save(os.path.join(f"static/profit_file/{str(filename)}"))
            read_file = pd.read_excel(f"static/profit_file/{str(filename)}")
            read_file.to_csv(filename, index=None, header=True)
            with open(filename, "r") as data:
                for line in csv.DictReader(data):
                    print(line["CRN NUMBER"])
                    CRN = line["CRN NUMBER"]
                    client = (
                        db_session.query(models.Clients)
                        .filter(models.Clients.crn == CRN)
                        .one_or_none()
                    )
                    if client is not None:
                        client.capital_profit = line["PROFIT/LOSS"]
                        client.profit_date = profit_date
                        client.upload_date = added_at
                        try:
                            db_session.commit()
                        except Exception as e:
                            db_session.rollback()
                    else:
                        continue

            return redirect(url_for("client_blueprint.view_clients"))
    except Exception as e:
        print(e)
        return redirect(url_for("client_blueprint.view_clients"))


@client_blueprint.route("/view_clients")
@jwt_required()
@permission("client")
def view_clients():
    try:
        user_id = get_jwt_identity()
        user = (
            db_session.query(models.Users)
            .filter(models.Users.id == user_id)
            .one_or_none()
        )
        data = db_session.query(models.Clients).all()
        return render_template("view_clients.html", data=data, user=user)
    except Exception as e:
        raise


@client_blueprint.route("/view_data/<int:id>")
@jwt_required()
@permission("client")
def view_data(id):
    try:
        user_id = get_jwt_identity()
        user = (
            db_session.query(models.Users)
            .filter(models.Users.id == user_id)
            .one_or_none()
        )
        data = db_session.query(models.Clients).filter(models.Clients.id == id).first()
        today = datetime.now()
        return render_template("view_data.html", client=data, user=user, today=today)
    except Exception as e:
        raise


@client_blueprint.route("/edit_client/<int:id>")
@jwt_required()
@permission("client", "client_edit")
def edit_client(id):
    try:
        user_id = get_jwt_identity()
        user = (
            db_session.query(models.Users)
            .filter(models.Users.id == user_id)
            .one_or_none()
        )
        client = (
            db_session.query(models.Clients).filter(models.Clients.id == id).first()
        )
        return render_template("edit_client.html", client=client, user=user)
    except Exception as e:
        raise


@client_blueprint.route("/update_client", methods=["GET", "POST"])
@jwt_required()
@permission("client", "client_edit")
def update_client():
    try:
        if request.method == "POST":
            id = request.form["id"]
            client = (
                db_session.query(models.Clients).filter(models.Clients.id == id).first()
            )
            client.crn = request.form["crn"]
            client.company = request.form["company"]
            client.data = request.form["data"]
            client.note = request.form["note"]
            client.capital = request.form["capital"]
            client.capital_profit = request.form["capital_profit"]
            status = request.form["status"]
            if status == "True":
                status = True
            else:
                status = False
            client.status = status
            client.trading_info = request.form["trading_info"]
            client.date_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    except Exception as e:
        print(e)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
    return redirect(url_for("client_blueprint.view_clients"))


@client_blueprint.route("/delete_client/<int:id>")
@jwt_required()
@permission("client", "client_delete")
def delete_client(id):
    try:
        client = (
            db_session.query(models.Clients).filter(models.Clients.id == id).first()
        )
        db_session.delete(client)

    except Exception as e:
        print(e)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
    return redirect(url_for("client_blueprint.view_clients"))


@client_blueprint.route("/view_users")
@jwt_required()
def view_users():
    try:
        user_id = get_jwt_identity()
        user = (
            db_session.query(models.Users)
            .filter(models.Users.id == user_id)
            .one_or_none()
        )
        if user.type == "admin":
            users = db_session.query(models.Users).all()
            return render_template("view_users.html", users=users, user=user)
        else:
            flash("You Are Not Admin!!")
            return render_template("dashboard.html", user=user)
    except Exception as e:
        raise


@client_blueprint.route("/update_permission", methods=["GET", "POST"])
def update_permission():
    try:
        if request.method == "POST":
            id = request.form["id"]
            user = db_session.query(models.Users).filter(models.Users.id == id).first()
            try:
                strategy_details = request.form["strategy_details"]
                user.strategy_details = True
            except Exception as e:
                print(e)
                user.strategy_details = False
            try:
                strategy_details_add = request.form["strategy_details_add"]
                user.strategy_details_add = True
            except Exception as e:
                print(e)
                user.strategy_details_add = False
            try:
                strategy_details_edit = request.form["strategy_details_edit"]
                user.strategy_details_edit = True
            except Exception as e:
                print(e)
                user.strategy_details_edit = False
            try:
                strategy_details_delete = request.form["strategy_details_delete"]
                user.strategy_details_delete = True
            except Exception as e:
                print(e)
                user.strategy_details_delete = False

            try:
                client_details = request.form["client_details"]
                user.client_details = True
            except Exception as e:
                print(e)
                user.client_details = False
            try:
                client_details_add = request.form["client_details_add"]
                user.client_details_add = True
            except Exception as e:
                print(e)
                user.client_details_add = False
            try:
                client_details_edit = request.form["client_details_edit"]
                user.client_details_edit = True
            except Exception as e:
                print(e)
                user.client_details_edit = False
            try:
                client_details_delete = request.form["client_details_delete"]
                user.client_details_delete = True
            except Exception as e:
                print(e)
                user.client_details_delete = False
            try:
                db_session.commit()
            except Exception as e:
                db_session.rollback()
            return redirect(url_for("client_blueprint.view_users"))
    except Exception as e:
        print(e)


@client_blueprint.route("/update_password", methods=["GET", "POST"])
def update_password():
    try:
        if request.method == "POST":
            id = request.form["id"]
            user = db_session.query(models.Users).filter(models.Users.id == id).first()
            new_password = request.form["password"]
            hashed_password = bcrypt.generate_password_hash(new_password).decode(
                "utf-8"
            )
            user.password = hashed_password
    except Exception as e:
        print(e)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
    return redirect(url_for("client_blueprint.view_users"))


@client_blueprint.route("/delete_user/<int:id>")
@jwt_required()
def delete_user(id):
    try:
        user = db_session.query(models.Users).filter(models.Users.id == id).first()
        db_session.delete(user)
    except Exception as e:
        print(e)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
    return redirect(url_for("client_blueprint.view_users"))
