from main import db
from models.CommonAuth import CommonAuthMethods


class AdminModel(db.Model, CommonAuthMethods):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    phone = db.Column(db.String())
    email = db.Column(db.String())
    password = db.Column(db.String())

    companies = db.relationship('CompaniesModel', backref='admin')