from main import db
from models.CommonMethods import CommonMethods


class BranchesModel(db.Model, CommonMethods):
    __tablename__ = 'branches'
    id = db.Column(db.Integer, primary_key=True)
    branch_name = db.Column(db.String())
    phone = db.Column(db.String())
    email = db.Column(db.String())

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    ambulances = db.relationship('AmbulancesModel', backref='branch')

    @classmethod
    def fetch_by_branch_name(cls, branch_name):
        return cls.query.filter_by(branch_name=branch_name).first()

    # check whether constituency exists
    @classmethod
    def check_constituency(cls, branch_name):
        record = cls.query.filter_by(branch_name=branch_name).first()
        return record

    # update branch by id
    @classmethod
    def update_branch_by_id(cls, id, branch_name=None, phone=None, email=None):
        record = cls.query.filter_by(id=id).first()
        if branch_name:
            record.branch_name = branch_name
        if phone:
            record.phone = phone
        if email:
            record.email = email
        db.session.commit()
        return True

    # delete branch
    @classmethod
    def delete_branch_by_id(cls, id):
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        return True
