from main import db
from models.CommonMethods import CommonMethods


class CompaniesModel(db.Model, CommonMethods):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String())
    phone = db.Column(db.String())
    email = db.Column(db.String())

    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))

    branches = db.relationship('BranchesModel', backref='company')

    @classmethod
    def check_company(cls, company_name):
        record = cls.query.filter_by(company_name=company_name).first()
        return record

    # update company by id
    @classmethod
    def update_company_by_id(cls, id, company_name=None, phone=None, email=None):
        record = cls.query.filter_by(id=id).first()
        if company_name:
            record.company_name = company_name
        if phone:
            record.phone = phone
        if email:
            record.email = email
        db.session.commit()
        return True

    # delete company
    @classmethod
    def delete_company_by_id(cls, id):
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        return True
