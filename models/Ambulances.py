from main import db
from models.CommonMethods import CommonMethods


class AmbulancesModel(db.Model, CommonMethods):
    __tablename__ = 'ambulances'
    id = db.Column(db.Integer, primary_key=True)
    ambulance_type = db.Column(db.String())
    ambulance_plates = db.Column(db.String())
    ambulance_image = db.Column(db.String(), nullable=False, unique=True)
    driver_name = db.Column(db.String())
    phone = db.Column(db.String())
    email = db.Column(db.String())
    status = db.Column(db.String(), default='un_booked')

    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))

    @classmethod
    def check_plates(cls, ambulance_plates):
        record = cls.query.filter_by(ambulance_plates=ambulance_plates).first()
        return record

    # update ambulance by id
    @classmethod
    def update_ambulance_by_id(cls, id, driver_name=None, phone=None, email=None):
        record = cls.query.filter_by(id=id).first()
        if driver_name:
            record.branch_name = driver_name
        if phone:
            record.phone = phone
        if email:
            record.email = email
        db.session.commit()
        return True

    # delete ambulance
    @classmethod
    def delete_ambulance_by_id(cls, id):
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        return True

    @classmethod
    def check_driver(cls, driver_name):
        record = cls.query.filter_by(driver_name=driver_name).first()
        if record:
            return True
        else:
            return False

    @classmethod
    def check_phone(cls, phone):
        record = cls.query.filter_by(phone=phone).first()
        if record:
            return True
        else:
            return False

    @classmethod
    def fetch_by_driver_name(cls, driver_name):
        return cls.query.filter_by(driver_name=driver_name).first()

    # update ambulance status
    @classmethod
    def update_status(cls, id, status=None):
        record = cls.query.filter_by(id=id).first()
        if status:
            record.status = status
        db.session.commit()
        return True