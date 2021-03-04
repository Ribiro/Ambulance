from main import db


class CommonMethods:
    def insert_record(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def fetch_all(cls):
        return cls.query.all()

    @classmethod
    def fetch_by_id(cls, id):
        return cls.query.filter_by(id=id).first()