from flask_login import  UserMixin
from sqlalchemy import Date 
from __init__ import *  

# таблица с услугами
class Service_list(db.Model):
    tablename = 'service_list'
    table_args = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    price = db.Column(db.Integer)
    partner_price = db.Column(db.Integer)
    img_url = db.Column(db.String)

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description, 'price': self.price, 'partner_price': self.partner_price, 'img_url': self.img_url}

# таблица с администраторами
class Admin_list(db.Model):
    tablename = 'admin_list'
    table_args = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String)

    def to_dict(self):
        return {'id': self.id, 'login': self.login}
    
# таблица с партнерами
class Partner_list(db.Model):
    tablename = 'partner_list'
    table_args = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String)

    def to_dict(self):
        return {'id': self.id, 'login': self.login}

# таблица с статусами
class Status(db.Model):
    tablename = 'status'
    table_args = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

# таблица с пользователями
class User(UserMixin, db.Model):
    tablename = 'user'
    table_args = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telegram = db.Column(db.String(120), unique=True, nullable=False)
    hash_password = db.Column(db.String(60), nullable=False)

    def to_dict(self):
        return {'login': self.login, 'telegram': self.telegram}

# таблица с записями
class Reservation(db.Model):
    tablename = 'reservation'
    table_args = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.String(5000), unique=True, nullable=False)
    check_sum = db.Column(db.Integer)
    status_id = db.Column(db.Integer, nullable=False)
    date = db.Column(Date, unique=True, nullable=False)

    def to_dict(self):
        return {'id': self.id, 'user_id': self.user_id, 'comments': self.comments, 'check_sum': self.check_sum, 'status_id': self.status_id, 'date': self.date}

# таблица с датами
class Free_date(db.Model):
    tablename = 'free_date'
    table_args = {'schema': 'public'}
    id = db.Column(db.Integer, primary_key=True)
    free_date = db.Column(Date, unique=True, nullable=False)

    def to_dict(self):
        return {'id': self.id, 'free_date': self.free_date}