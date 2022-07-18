from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    links = db.relationship('Link', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.id)


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pattern = db.Column(db.String(120))

    def __repr__(self):
        return '<Link {}>'.format(self.link)