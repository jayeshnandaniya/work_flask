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
    send_from_directory,
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
import csv

view_blueprint = Blueprint("view_blueprint", __name__)
api_blueprint = Blueprint("api_blueprint", __name__)

api = Api(api_blueprint)
bcrypt = Bcrypt()


# def permission(user_agent):
#     def inner_decorator(f):
#         def decorated_function(*args, **kwargs):
#
#             id = get_jwt_identity()
#             print(id)
#             user = (
#                 db_session.query(models.Users)
#                 .filter(models.Users.id == id)
#                 .one_or_none()
#             )
#             if user.strategy_details == True:
#                 return f(*args, **kwargs)
#             else:
#                 return redirect(url_for("view_blueprint.dashboard"))
#
#         return decorated_function
#
#     return decorated_function


def permission(arg1, arg2=None):
    def inner_function(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            id = get_jwt_identity()
            user = (
                db_session.query(models.Users)
                .filter(models.Users.id == id)
                .one_or_none()
            )
            if arg1 == "strategy":
                if arg2 == "strategy_add":
                    if (
                        user.strategy_details == True
                        and user.strategy_details_add == True
                    ):
                        return function(*args, **kwargs)
                    else:
                        flash("You Don't Have Rights For This Action !!")
                        return redirect(url_for("view_blueprint.dashboard"))
                elif arg2 == "strategy_edit":
                    if (
                        user.strategy_details == True
                        and user.strategy_details_edit == True
                    ):
                        return function(*args, **kwargs)
                    else:
                        flash("You Don't Have Rights For This Action !!")
                        return redirect(url_for("view_blueprint.dashboard"))
                elif arg2 == "strategy_delete":
                    if (
                        user.strategy_details == True
                        and user.strategy_details_delete == True
                    ):
                        return function(*args, **kwargs)
                    else:
                        flash("You Don't Have Rights For This Action !!")
                        return redirect(url_for("view_blueprint.dashboard"))
                elif arg2 == None:
                    if user.strategy_details == True:
                        return function(*args, **kwargs)
                    else:
                        flash("You Don't Have Rights For This Action !!")
                        return redirect(url_for("view_blueprint.dashboard"))
            if arg1 == "client":
                if arg2 == "client_add":
                    if user.client_details == True and user.client_details_add == True:
                        return function(*args, **kwargs)
                    else:
                        flash("You Don't Have Rights For This Action !!")
                        return redirect(url_for("view_blueprint.dashboard"))
                elif arg2 == "client_edit":
                    if user.client_details == True and user.client_details_edit == True:
                        return function(*args, **kwargs)
                    else:
                        flash("You Don't Have Rights For This Action !!")
                        return redirect(url_for("view_blueprint.dashboard"))
                elif arg2 == "client_delete":
                    if (
                        user.client_details == True
                        and user.client_details_delete == True
                    ):
                        return function(*args, **kwargs)
                    else:
                        flash("You Don't Have Rights For This Action !!")
                        return redirect(url_for("view_blueprint.dashboard"))
                elif arg2 == None:
                    if user.client_details == True:
                        return function(*args, **kwargs)
                    else:
                        flash("You Don't Have Rights For This Action !!")
                        return redirect(url_for("view_blueprint.dashboard"))

        return wrapper

    return inner_function


@view_blueprint.route("/admin")
def admin():
    return render_template("add_admin.html")


@view_blueprint.route("/add_admin", methods=["GET", "POST"])
def add_admin():
    if request.method == "POST":
        email_regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
        username = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        try:
            if re.search(email_regex, email):
                user = (
                    db_session.query(models.Users)
                    .filter(models.Users.email == email)
                    .one_or_none()
                )
                if user is None:
                    hashed_password = bcrypt.generate_password_hash(password).decode(
                        "utf-8"
                    )
                    created_at = datetime.now()
                    user = models.Users(
                        username=username,
                        email=email,
                        password=hashed_password,
                        created_at=created_at,
                        type="admin",
                        strategy_details=True,
                        strategy_details_add=True,
                        strategy_details_edit=True,
                        strategy_details_delete=True,
                        client_details=True,
                        client_details_add=True,
                        client_details_edit=True,
                        client_details_delete=True,
                    )
                    db_session.add(user)
                    db_session.flush()
                else:
                    flash("Email already exists.")
                    return redirect(url_for("view_blueprint.admin"))
            else:
                flash("Failed to register.")
                return redirect(url_for("view_blueprint.admin"))
        except Exception as e:
            print(e)
            flash("Failed to register.")
            return redirect(url_for("view_blueprint.admin"))

        try:
            db_session.commit()
            flash("You are successfully registered.")
            return redirect(url_for("view_blueprint.login"))

        except Exception as e:
            print(e)
            db_session.rollback()
            flash("Failed to register.")
            return redirect(url_for("view_blueprint.admin"))

    else:
        return render_template("add_user.html")


@view_blueprint.route("/logout")
@jwt_required()
def logout():
    try:
        resp = redirect(url_for("view_blueprint.login"))
        resp.delete_cookie("session")
        unset_jwt_cookies(resp)
        return resp
    except Exception as e:
        print(e)
        return render_template("dashboard.html")


@view_blueprint.route("/", methods=["GET", "POST"])
@view_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        print(email)
        password = request.form["password"]
        try:
            user = (
                db_session.query(models.Users)
                .filter(
                    or_(
                        models.Users.email == email,
                    )
                )
                .first()
            )
            if user and bcrypt.check_password_hash(user.password, password):
                access_token = create_access_token(identity=user.id)
                refresh_token = create_refresh_token(identity=user.id)

                resp = redirect(url_for("view_blueprint.dashboard"))
                set_access_cookies(resp, access_token)

                # access cookie and verify jwt token
                set_refresh_cookies(resp, refresh_token)

                return resp
            else:
                flash("Please check your email or password.")
                return redirect(url_for("view_blueprint.login"))

        except Exception as e:
            print(e)
            flash("Failed to login. Please login again.")
            return redirect(url_for("view_blueprint.login"))
    else:
        return render_template("login.html")


@view_blueprint.route("/dashboard")
@jwt_required()
def dashboard():
    total = db_session.query(models.Reports).count()
    print(total)
    id = get_jwt_identity()
    profitable = (
        db_session.query(models.Reports)
        .filter(models.Reports.profitable == True)
        .count()
    )
    user = db_session.query(models.Users).filter(models.Users.id == id).one_or_none()
    clients = db_session.query(models.Clients).count()
    print(profitable)
    return render_template(
        "dashboard.html", total=total, profitable=profitable, user=user, clients=clients
    )


@view_blueprint.route("/new_user")
@jwt_required()
def new_user():
    id = get_jwt_identity()
    user = db_session.query(models.Users).filter(models.Users.id == id).one_or_none()
    if user.type == "admin":
        return render_template("add_user.html", user=user)
    else:
        flash("You Are Not Admin!!")
        return render_template("dashboard.html", user=user)


@view_blueprint.route("/add_user", methods=["GET", "POST"])
@jwt_required()
def add_user():
    user_id = get_jwt_identity()
    user = (
        db_session.query(models.Users).filter(models.Users.id == user_id).one_or_none()
    )
    if user.type == "admin":
        if request.method == "POST":
            print(request.form)
            email_regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
            username = request.form["username"]
            email = request.form["user_email"]
            password = request.form["InputPassword"]

            try:
                strategy_details = request.form["strategy_details"]
                strategy_details = True
            except Exception as e:
                print(e)
                strategy_details = False
            try:
                strategy_details_add = request.form["strategy_details_add"]
                strategy_details_add = True
            except Exception as e:
                print(e)
                strategy_details_add = False
            try:
                strategy_details_edit = request.form["strategy_details_edit"]
                strategy_details_edit = True
            except Exception as e:
                print(e)
                strategy_details_edit = False
            try:
                strategy_details_delete = request.form["strategy_details_delete"]
                strategy_details_delete = True
            except Exception as e:
                print(e)
                strategy_details_delete = False

            try:
                client_details = request.form["client_details"]
                client_details = True
            except Exception as e:
                print(e)
                client_details = False
            try:
                client_details_add = request.form["client_details_add"]
                client_details_add = True
            except Exception as e:
                print(e)
                client_details_add = False
            try:
                client_details_edit = request.form["client_details_edit"]
                client_details_edit = True
            except Exception as e:
                print(e)
                client_details_edit = False
            try:
                client_details_delete = request.form["client_details_delete"]
                client_details_delete = True
            except Exception as e:
                print(e)
                client_details_delete = False

            try:
                if re.search(email_regex, email):
                    user = (
                        db_session.query(models.Users)
                        .filter(models.Users.email == email)
                        .one_or_none()
                    )
                    if user is None:
                        hashed_password = bcrypt.generate_password_hash(
                            password
                        ).decode("utf-8")
                        created_at = datetime.now()
                        user = models.Users(
                            username=username,
                            email=email,
                            password=hashed_password,
                            created_at=created_at,
                            type="user",
                            strategy_details=strategy_details,
                            strategy_details_add=strategy_details_add,
                            strategy_details_edit=strategy_details_edit,
                            strategy_details_delete=strategy_details_delete,
                            client_details=client_details,
                            client_details_add=client_details_add,
                            client_details_edit=client_details_edit,
                            client_details_delete=client_details_delete,
                        )
                        db_session.add(user)
                        db_session.flush()
                    else:
                        flash("Email already exists.")
                        return redirect(url_for("view_blueprint.add_user"))
                else:
                    flash("Failed to register.")
                    return redirect(url_for("view_blueprint.add_user"))
            except Exception as e:
                print(e)
                flash("Failed to register.")
                return redirect(url_for("view_blueprint.add_user"))

            try:
                db_session.commit()
                flash("You are successfully registered.", "success")
                return redirect(url_for("view_blueprint.new_user"))

            except Exception as e:
                print(e)
                db_session.rollback()
                flash("Failed to register.")
                return redirect(url_for("view_blueprint.add_user"))

        else:
            return render_template("add_user.html", user=user)
    else:
        flash("You Are Not Admin!!")
        return render_template("dashboard.html", user=user)


@view_blueprint.route("/add_data")
@jwt_required()
@permission("strategy", "strategy_add")
def index():
    id = get_jwt_identity()
    user = db_session.query(models.Users).filter(models.Users.id == id).one_or_none()
    result = (db_session.query(models.Reports)).all()
    data = []
    for i in result:
        data.append(str(i.account_number))
    return render_template("index.html", user=user, data=data)


@view_blueprint.route("/account_check", methods=["POST"])
def account_check():
    try:
        if request.method == "POST":
            account_number = request.form["account_number"]
            if account_number == "":
                resp = jsonify("Account Number is required field.")
                resp.status_code = 200
                return resp
            else:
                print(account_number)
                result = (
                    db_session.query(models.Reports)
                    .filter(models.Reports.account_number == account_number)
                    .one_or_none()
                )

                if result is not None:
                    resp = jsonify("Account Number Already Exists")
                    resp.status_code = 200
                    return resp
                else:
                    resp = jsonify("Account Number Valid")
                    resp.status_code = 200
                    return resp
    except Exception as e:
        print(e)


@view_blueprint.route("/add", methods=["GET", "POST"])
@jwt_required()
@permission("strategy", "strategy_add")
def add():
    """
    Serve main page. index.html should include the react bundle.js
    Maybe later we'll play around with Server Side Rendering
    """
    user_id = get_jwt_identity()
    user = (
        db_session.query(models.Users).filter(models.Users.id == user_id).one_or_none()
    )
    try:
        if request.method == "POST":
            account_number = request.form["account_number"]
            account_name = request.form["account_name"]
            password = request.form["password"]
            capital = request.form["capital"]
            profitable_category = request.form["profitable_category"]
            result = (
                db_session.query(models.Reports)
                .filter(models.Reports.account_number == account_number)
                .one_or_none()
            )
            if result is not None:
                flash("Account number already exists", "warning")
                return render_template("index.html", user=user)
            strategy_name = request.form["strategy_name"]

            broker_name = request.form["broker_name"]
            server = request.form["server"]
            investor = request.form["investor"]
            profitable = request.form["profitable"]
            if profitable == "True":
                profitable = True
            else:
                profitable = False
            location = request.form["location"]
            type = request.form["type"]
            max_lot = request.form["max_lot"]
            max_m2m = request.form["max_m2m"] if request.form["max_m2m"] != "" else None
            working_live = request.form["working_live"]
            live_streaming = request.form["live_streaming"]
            telegram_channel = request.form["telegram_channel"]
            note = request.form["note"]
            script = request.form["script"]
            timestamp = request.form["timestamp"]
            added_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            strategy_date = (
                request.form["strategy_date"]
                if request.form["strategy_date"] != ""
                else None
            )
            length = len(request.files)
            ls1 = []
            for obj in request.files:
                print(obj)
                try:
                    image = request.files[obj]
                    print(image)
                    if image.filename == "":
                        pass
                    else:
                        ls = image.filename.split(".")
                        print(ls)
                        image_url = f"{str(random.getrandbits(64))}.{str(ls[-1])}"
                        ls1.append(image_url)
                        image.save(f"static/setting_img/{str(image_url)}")
                except Exception as e:
                    print(e)
                    continue
            print(ls1)

            add_value = models.Reports(
                date_created=added_at,
                strategy_name=strategy_name,
                account_number=account_number,
                account_name=account_name,
                capital=capital,
                password=password,
                broker_name=broker_name,
                server=server,
                investor=investor,
                profitable=profitable,
                location=location,
                type=type,
                max_lot=max_lot,
                max_m2m=max_m2m,
                working_live=working_live,
                live_streaming=live_streaming,
                telegram_channel=telegram_channel,
                note=note,
                script=script,
                timestamp=timestamp,
                strategy_date=strategy_date,
                setting_img=ls1,
                profitable_category=profitable_category,
            )
            try:
                db_session.add(add_value)
                db_session.flush()
                db_session.commit()
            except Exception as e:
                db_session.rollback()
            return render_template("add_files.html", id=add_value.id, user=user)
        else:
            flash("You have no rights for this action!!", "warning")
            return render_template("index.html", user=user)
    except Exception as e:
        print(e)
        return redirect(url_for("view_blueprint.index"))


@view_blueprint.route("/new_files/<int:id>")
@jwt_required()
@permission("strategy")
def new_files(id):
    user_id = get_jwt_identity()
    user = (
        db_session.query(models.Users).filter(models.Users.id == user_id).one_or_none()
    )
    return render_template("add_files.html", id=id, user=user)


@view_blueprint.route("/add_files", methods=["GET", "POST"])
@jwt_required()
@permission("strategy")
def add_files():
    if request.method == "POST":
        strategy_id = request.form["id"]
        try:
            for i, obj in enumerate(request.files):
                try:
                    if (i + 1) % 2 == 0:
                        continue
                    file = request.files[obj]
                    image = request.files[obj.replace("pdf_file", "img_file")]
                    if image.filename == "" and file.filename == "":
                        pass
                    else:

                        ls = image.filename.split(".")
                        ls1 = file.filename.split(".")

                        image_name = f"{str(random.getrandbits(64))}.{str(ls[-1])}"
                        file_name = f"{str(random.getrandbits(64))}.{str(ls1[-1])}"

                        add_value = models.Files(
                            strategy_id=strategy_id,
                            image_url=image_name,
                            doc_url=file_name,
                        )
                        image.save(f"static/images/{str(image_name)}")
                        file.save(f"static/back_test_reports/{str(file_name)}")
                        db_session.add(add_value)
                        try:
                            db_session.commit()
                        except Exception as e:
                            db_session.rollback()

                except Exception as e:
                    print(e)
                    continue

        except Exception as e:
            print(e)

        return redirect(url_for("view_blueprint.view_reports"))


@view_blueprint.route("/view_reports")
@jwt_required()
@permission("strategy")
def view_reports():
    id = get_jwt_identity()
    user = db_session.query(models.Users).filter(models.Users.id == id).one_or_none()
    result = (db_session.query(models.Reports)).all()
    return render_template("view.html", results=result, user=user)


@view_blueprint.route("/view_details/<id>")
@jwt_required()
@permission("strategy")
def view_details(id):
    user_id = get_jwt_identity()
    user = (
        db_session.query(models.Users).filter(models.Users.id == user_id).one_or_none()
    )
    details = (
        db_session.query(models.Reports).filter(models.Reports.id == id).one_or_none()
    )
    files = db_session.query(models.Files).filter(models.Files.strategy_id == id).all()
    today = datetime.now()
    return render_template(
        "view_details.html", details=details, files=files, today=today, user=user
    )


@view_blueprint.route("/view_profitable/<id>")
@jwt_required()
@permission("strategy")
def profitable(id):

    print(id)
    user_id = get_jwt_identity()
    user = (
        db_session.query(models.Users).filter(models.Users.id == user_id).one_or_none()
    )
    if id == "True":

        result = (
            db_session.query(models.Reports).filter(models.Reports.profitable == True)
        ).all()
        return render_template("view.html", results=result, user=user)
    else:
        result = (
            db_session.query(models.Reports).filter(models.Reports.profitable == False)
        ).all()
        return render_template("view.html", results=result, user=user)


@view_blueprint.route("/update_reports/<int:id>")
@jwt_required()
@permission("strategy", "strategy_edit")
def edit_reports(id):
    try:
        user_id = get_jwt_identity()
        user = (
            db_session.query(models.Users)
            .filter(models.Users.id == user_id)
            .one_or_none()
        )
        details = (
            db_session.query(models.Reports).filter(models.Reports.id == id).first()
        )
        print(details.profitable)
        return render_template("edit_reports.html", details=details, user=user)
    except Exception as e:
        print(e)
        return redirect(url_for("view_blueprint.view_reports"))


@view_blueprint.route("/update", methods=["GET", "POST"])
@jwt_required()
@permission("strategy", "strategy_edit")
def update():
    try:
        if request.method == "POST":
            id = request.form["id"]
            details = (
                db_session.query(models.Reports)
                .filter(models.Reports.id == int(id))
                .one_or_none()
            )
            details.strategy_name = request.form["strategy_name"]
            details.account_number = request.form["account_number"]
            details.account_name = request.form["account_name"]
            details.password = request.form["password"]
            details.capital = request.form["capital"]
            details.broker_name = request.form["broker_name"]
            details.server = request.form["server"]
            details.investor = request.form["investor"]
            profitable = request.form["profitable"]
            if profitable == "True":
                profitable = True
            else:
                profitable = False
            details.profitable = profitable
            details.profitable_category = request.form["profitable_category"]
            details.location = request.form["location"]
            details.type = request.form["type"]
            details.max_lot = request.form["max_lot"]
            details.max_m2m = (
                request.form["max_m2m"] if request.form["max_m2m"] != "" else None
            )
            details.working_live = request.form["working_live"]
            details.live_streaming = request.form["live_streaming"]
            details.telegram_channel = request.form["telegram_channel"]
            details.note = request.form["note"]
            details.script = request.form["script"]
            details.timestamp = request.form["timestamp"]
            strategy_date = (
                request.form["strategy_date"]
                if request.form["strategy_date"] != ""
                else None
            )
            details.strategy_date = strategy_date
            length = len(request.files)
            ls1 = []
            for obj in request.files:
                print(obj)
                try:
                    image = request.files[obj]
                    print(image)
                    if image.filename == "":
                        pass
                    else:
                        ls = image.filename.split(".")
                        print(ls)
                        image_url = f"{str(random.getrandbits(64))}.{str(ls[-1])}"
                        ls1.append(image_url)
                        details.data_folder = image_url
                        image.save(f"static/data_folder/{str(image_url)}")
                except Exception as e:
                    print(e)
                    continue
            print(ls1)

    except Exception as e:
        print(e)
        return redirect(url_for("view_blueprint.edit_reports", id=id))
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()

    return redirect(url_for("view_blueprint.view_reports"))


@view_blueprint.route("/edit_files/<int:id>")
@jwt_required()
@permission("strategy", "strategy_edit")
def edit_files(id):
    try:
        user_id = get_jwt_identity()
        user = (
            db_session.query(models.Users)
            .filter(models.Users.id == user_id)
            .one_or_none()
        )
        files = db_session.query(models.Files).filter(models.Files.id == id).first()
        return render_template("edit_files.html", file=files, user=user)
    except Exception as e:
        print(e)


@view_blueprint.route("/update_files", methods=["GET", "POST"])
@jwt_required()
@permission("strategy", "strategy_edit")
def update_files():
    try:
        strategy_id = request.form["strategy_id"]
        if request.method == "POST":
            id = request.form["id"]
            file = (
                db_session.query(models.Files)
                .filter(models.Files.id == int(id))
                .one_or_none()
            )
            if request.files["image"].filename == "":
                print("Hello")
            else:
                print(request.files["image"].filename)
                print(os.path.join("static/images", file.image_url))
                os.remove(os.path.join("static/images", file.image_url))
                ls = request.files["image"].filename.split(".")
                file.image_url = f"{str(random.getrandbits(64))}.{str(ls[-1])}"
                request.files["image"].save(f"static/images/{str(file.image_url)}")

            if request.files["document"].filename == "":
                pass
            else:
                os.remove(os.path.join("static/back_test_reports", file.doc_url))
                ls = request.files["document"].filename.split(".")
                file.doc_url = f"{str(random.getrandbits(64))}.{str(ls[-1])}"
                request.files["document"].save(
                    f"static/back_test_reports/{str(file.doc_url)}"
                )

    except Exception as e:
        print(e)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
    return redirect(url_for("view_blueprint.view_details", id=strategy_id))


@view_blueprint.route("/new_setting_img/<int:id>")
@jwt_required()
@permission("strategy", "strategy_add")
def new_setting_img(id):
    try:
        user_id = get_jwt_identity()
        user = (
            db_session.query(models.Users)
            .filter(models.Users.id == user_id)
            .one_or_none()
        )
        print(id)
        return render_template("add_setting_images.html", id=id, user=user)
    except Exception as e:
        print(e)


@view_blueprint.route("/add_setting_img", methods=["POST"])
@jwt_required()
@permission("strategy", "strategy_add")
def add_setting_img():
    try:
        id = request.form["id"]
        print(id)
        details = (
            db_session.query(models.Reports).filter(models.Reports.id == id).first()
        )
        setting_images = details.setting_img
        for obj in request.files:
            print(obj)
            try:
                image = request.files[obj]
                print(image)
                ls = image.filename.split(".")
                print(ls)
                image_url = f"{str(random.getrandbits(64))}.{str(ls[-1])}"
                setting_images.append(image_url)
                image.save(f"static/setting_img/{str(image_url)}")
            except Exception as e:
                print(e)
                continue

    except Exception as e:
        print(e)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
    return redirect(url_for("view_blueprint.view_details", id=id))


@view_blueprint.route("/edit_setting_img/<int:id>/<int:img_index>")
@jwt_required()
@permission("strategy", "strategy_edit")
def edit_setting_img(id, img_index):
    try:
        user_id = get_jwt_identity()
        user = (
            db_session.query(models.Users)
            .filter(models.Users.id == user_id)
            .one_or_none()
        )
        images = (
            db_session.query(models.Reports)
            .filter(models.Reports.id == id)
            .one_or_none()
        )
        print(images.setting_img[img_index - 1])
        img = images.setting_img[img_index - 1]
        return render_template(
            "edit_image.html", images=img, id=id, img_index=img_index - 1, user=user
        )
    except Exception as e:
        print(e)


@view_blueprint.route("/update_setting_img", methods=["GET", "POST"])
@jwt_required()
@permission("strategy", "strategy_edit")
def update_setting_img():
    try:
        id = request.form["id"]
        img_index = request.form["img_index"]
        image = request.files["image"]
        ls1 = []
        index = int(img_index)
        print(index)
        if image.filename == "":
            pass
        else:
            images = (
                db_session.query(models.Reports)
                .filter(models.Reports.id == id)
                .one_or_none()
            )
            os.remove(os.path.join("static/setting_img", images.setting_img[index]))
            images.setting_img.pop(int(img_index))
            ls = image.filename.split(".")
            image_name = f"{str(random.getrandbits(64))}.{str(ls[-1])}"
            images.setting_img.append(image_name)
            image.save(f"static/setting_img/{str(image_name)}")

    except Exception as e:
        print(e)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
    return redirect(url_for("view_blueprint.view_details", id=id))


@view_blueprint.route("/delete_setting_img/<int:id>/<int:img_index>")
@jwt_required()
@permission("strategy", "strategy_delete")
def delete_setting_img(id, img_index):
    try:
        img_index = img_index - 1
        print(img_index)
        details = (
            db_session.query(models.Reports)
            .filter(models.Reports.id == id)
            .one_or_none()
        )
        print(details.setting_img)
        os.remove(os.path.join("static/setting_img", details.setting_img[img_index]))
        details.setting_img.pop(img_index)
        temp_list = details.setting_img
        details.setting_img = None
        try:
            db_session.commit()
        except Exception as e:
            db_session.rollback()
        db_session.refresh(details)
        details.setting_img = temp_list

    except Exception as e:
        print(e)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
    return redirect(url_for("view_blueprint.view_details", id=id))


@view_blueprint.route("/delete_files/<int:id>/<int:strategy_id>")
@jwt_required()
@permission("strategy", "strategy_delete")
def delete_files(id, strategy_id):
    try:
        files = db_session.query(models.Files).filter(models.Files.id == id).first()
        os.remove(os.path.join("static/images", files.image_url))
        os.remove(os.path.join("static/back_test_reports", files.doc_url))
        db_session.delete(files)

    except Exception as e:
        print(e)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
    return redirect(url_for("view_blueprint.view_details", id=strategy_id))


@view_blueprint.route("/delete/<int:id>")
@jwt_required()
@permission("strategy", "strategy_delete")
def delete(id):
    try:
        details = (
            db_session.query(models.Reports).filter(models.Reports.id == id).first()
        )
        files = (
            db_session.query(models.Files).filter(models.Files.strategy_id == id).all()
        )

        for file in files:
            os.remove(os.path.join("static/images", file.image_url))
            os.remove(os.path.join("static/back_test_reports", file.doc_url))

        db_session.delete(details)
        try:
            db_session.commit()
        except Exception as e:
            db_session.rollback()
        return redirect(url_for("view_blueprint.view_reports"))

    except Exception as e:
        print(e)


@view_blueprint.route("/download", methods=["GET", "POST"])
@jwt_required()
@permission("strategy")
def download():
    filename = request.form["filename"]
    strategy_id = request.form["strategy_id"]
    password = request.form["password"]

    if password != "1515sr71":
        flash("wrong password")
        return redirect(url_for("view_blueprint.view_details", id=int(strategy_id)))

    uploads = os.path.join("static", "data_folder")
    return send_from_directory(directory=uploads, filename=filename)


@view_blueprint.route("/import_csv", methods=["GET", "POST"])
@jwt_required()
@permission("strategy")
def import_csv():
    for obj in request.files:
        try:
            csvfile = request.files[obj]
            if csvfile.filename == "":
                pass
            else:
                ls = csvfile.filename.split(".")
                csvfile_url = f"2137608364786662850.{str(ls[-1])}"
                csvfile.save(f"static/imported_csv/{str(csvfile_url)}")
        except Exception as e:
            print(e)

    try:
        with open(f"static/imported_csv/{str(csvfile_url)}", "r") as file:
            csvreader = csv.DictReader(file)
            for row in csvreader:
                try:
                    row = {k.lower(): v for k, v in row.items()}

                    try:
                        cr_date = datetime.strptime(row["sdate"], "%d-%m-%Y")
                        cr_date = datetime.strftime(cr_date, "%Y-%m-%d")
                    except Exception as e:
                        cr_date = None

                    add_value = models.Reports(
                        date_created=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        strategy_name=row["eaname"],
                        account_number=int(row["accno"]),
                        broker_name=row["broker"],
                        profitable=False,
                        server=row["server"],
                        location=row["location"],
                        type=row["type"],
                        note=row["note"],
                        script=row["script"],
                        timestamp=row["tf"],
                        strategy_date=cr_date,
                        account_name=row["accname"],
                        password=row["pass"],
                        setting_img=[],
                        capital=row["capital"],
                    )
                except Exception as e:
                    print(e)
                    continue
                try:
                    db_session.add(add_value)
                    db_session.flush()
                    db_session.commit()
                except Exception as e:
                    print(e)
                    db_session.rollback()
    except Exception as e:
        print(e)

    return redirect(url_for("view_blueprint.view_reports"))


api.add_resource(JWTDistributor, "/api/v1/auth")
api.add_resource(FacebookLogin, "/api/v1/auth/facebook")
api.add_resource(GoogleLogin, "/api/v1/auth/google")
api.add_resource(ValidationEmailSender, "/api/v1/validate")
api.add_resource(TokenValidator, "/api/v1/validate/<token>")

api.add_resource(UserList, "/api/v1/users")
api.add_resource(User, "/api/v1/users/<user_id>")

api.add_resource(NotificationList, "/api/v1/notifications")
api.add_resource(Notification, "/api/v1/notifications/<notification_id>")
