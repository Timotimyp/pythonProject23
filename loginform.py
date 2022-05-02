from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask import redirect, Flask, render_template, request, url_for, make_response, logging
from data import db_session, news_api
from data.profils import Profile
from data.search_history import History
from data.bookmark import Bookmarks
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, LoginManager, login_user, logout_user
import os

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class Buttons(FlaskForm):
    submit = SubmitField("Закладки")
    submit1 = SubmitField("История")
    submit2 = SubmitField("Ссылка")
    submit3 = SubmitField("Выйти")


class Back(FlaskForm):
    submit = SubmitField("Назад")



@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Profile).get(user_id)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Profile).filter(Profile.login == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(f'/success/{form.username.data}')
        else:
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
    return render_template("login.html", form=form)


@app.route('/success/<login>', methods=['GET', 'POST'])
@login_required
def success(login):
    form = Buttons()
    if form.is_submitted():
        if form.submit.data:
            return redirect(f"/bookmarks/{login}")
        if form.submit1.data:
            return redirect(f"/history/{login}")
        if form.submit2.data:
            return redirect("https://t.me/film_etc_helper_bot")
        if form.submit3.data:
            return redirect("/logout")
    return render_template('button.html', form=form)


@app.route('/unsuccess', methods=['GET', 'POST'])
@login_required
def unsuccess():
    return render_template('404.html')


def check_profils(login, password):
    db_sess = db_session.create_session()
    if login in [prof.login for prof in db_sess.query(Profile).all()]:
        if check_password_hash(db_sess.query(Profile).filter(Profile.login == login).first().hashed_password, password):
            return True
        return False
    return False


@app.route("/bookmarks/<login>", methods=['GET', 'POST'])
@login_required
def bookmarks(login):
    form = Back()
    if form.is_submitted():
        return redirect(f"/success/{login}")
    news = return_bookmarks(login)
    return render_template("bookmarks.html", news=news, form=form)


def return_bookmarks(login):
    db_sess = db_session.create_session()
    user = db_sess.query(Profile).filter(Profile.login == login).first()
    chat_id = int(user.chat_id)
    return [prof.request for prof in db_sess.query(Bookmarks).filter(Bookmarks.chat_id == chat_id).all()]


@app.route("/history/<login>", methods=['GET', 'POST'])
@login_required
def history(login):
    form = Back()
    if form.is_submitted():
        return redirect(f"/success/{login}")
    news = return_history(login)
    return render_template("history.html", news=news, form=form)


def return_history(login):
    db_sess = db_session.create_session()
    user = db_sess.query(Profile).filter(Profile.login == login).first()
    chat_id = int(user.chat_id)
    return [prof.request for prof in db_sess.query(History).filter(History.chat_id == chat_id).all()]


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/users.db")
    app.register_blueprint(news_api.blueprint)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
