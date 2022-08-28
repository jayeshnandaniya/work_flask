"""
Database schema definition
"""

from enum import Enum

import sqlalchemy
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()


class MutableList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value


class Users(Base):
    __tablename__ = "users"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    username = sqlalchemy.Column(sqlalchemy.String(256))
    email = sqlalchemy.Column(sqlalchemy.String(256))
    password = sqlalchemy.Column(sqlalchemy.String(200))
    created_at = sqlalchemy.Column(sqlalchemy.DateTime(), nullable=True)
    type = sqlalchemy.Column(sqlalchemy.String(256))
    strategy_details = sqlalchemy.Column(sqlalchemy.Boolean, default="False")
    strategy_details_add = sqlalchemy.Column(sqlalchemy.Boolean, default="False")
    strategy_details_edit = sqlalchemy.Column(sqlalchemy.Boolean, default="False")
    strategy_details_delete = sqlalchemy.Column(sqlalchemy.Boolean, default="False")
    client_details = sqlalchemy.Column(sqlalchemy.Boolean, default="False")
    client_details_add = sqlalchemy.Column(sqlalchemy.Boolean, default="False")
    client_details_edit = sqlalchemy.Column(sqlalchemy.Boolean, default="False")
    client_details_delete = sqlalchemy.Column(sqlalchemy.Boolean, default="False")


class Reports(Base):
    __tablename__ = "reports"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    strategy_name = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    account_number = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    broker_name = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    server = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    investor = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    profitable = sqlalchemy.Column(sqlalchemy.Boolean, default="False")
    location = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    type = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    max_lot = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    max_m2m = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    working_live = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    live_streaming = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    telegram_channel = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    note = sqlalchemy.Column(sqlalchemy.String(2000), nullable=True)
    script = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    timestamp = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    date_created = sqlalchemy.Column(sqlalchemy.DateTime(), nullable=True)
    strategy_date = sqlalchemy.Column(sqlalchemy.DateTime(), nullable=True)
    setting_img = sqlalchemy.Column(
        MutableList.as_mutable(ARRAY(sqlalchemy.String(256))), nullable=True
    )
    data_folder = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    account_name = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    capital = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    profitable_category = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)


class Files(Base):
    __tablename__ = "files"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    strategy_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey(Reports.id, ondelete="CASCADE")
    )
    image_url = sqlalchemy.Column(sqlalchemy.String(256))
    doc_url = sqlalchemy.Column(sqlalchemy.String(256))


class Clients(Base):
    __tablename__ = "clients"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    crn = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    company = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    data = sqlalchemy.Column(sqlalchemy.String(10000), nullable=True)
    note = sqlalchemy.Column(sqlalchemy.String(2000), nullable=True)
    date_created = sqlalchemy.Column(sqlalchemy.DateTime(), nullable=True)
    date_updated = sqlalchemy.Column(sqlalchemy.DateTime(), nullable=True)
    trading_info = sqlalchemy.Column(sqlalchemy.String(10000), nullable=True)
    status = sqlalchemy.Column(sqlalchemy.Boolean, default="False")
    capital = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    capital_profit = sqlalchemy.Column(sqlalchemy.String(1000), nullable=True)
    profit_date = sqlalchemy.Column(sqlalchemy.DateTime(), nullable=True)
    upload_date = sqlalchemy.Column(sqlalchemy.DateTime(), nullable=True)
