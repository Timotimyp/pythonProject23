import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin



class Profile(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'profile'

    chat_id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, nullable=False, unique=True)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    genres = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)

    def get_id(self):
        return (self.chat_id)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)