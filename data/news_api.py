import flask
from . import db_session
from .profils import Profile
from .search_history import History
from .bookmark import Bookmarks
from flask import request as req
from flask import jsonify

blueprint = flask.Blueprint(
    'news_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/chat_id_for_registration')
def get_chat_id():
    db_sess = db_session.create_session()
    return {
        'chat_id': [prof.chat_id for prof in db_sess.query(Profile).all()],
    }


@blueprint.route('/api/logins_for_registration')
def post_login():
    db_sess = db_session.create_session()
    return {
        'logins': [prof.login for prof in db_sess.query(Profile).all()],
    }


@blueprint.route('/api/create_new_profile', methods=['POST'])
def create_profile():
    if not req.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in req.json for key in
                 ['chat_id', 'login', 'password']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    prof = Profile()
    prof.chat_id = req.json['chat_id']
    prof.login = req.json['login']
    prof.set_password(req.json['password'])
    db_sess.add(prof)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/create_history_post', methods=['POST'])
def write_history():
    if not req.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in req.json for key in
                 ['chat_id', 'request', 'subject']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    hist = History()
    hist.chat_id = req.json['chat_id']
    hist.request = req.json['request']
    hist.subject = req.json['subject']
    db_sess.add(hist)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/get_history/<int:chat_id>', methods=['GET'])
def get_history(chat_id):
    db_sess = db_session.create_session()
    history = [hist.request for hist in db_sess.query(History).filter(History.chat_id == int(chat_id)).all()]
    if not history:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'error': 'No error',
            'history': history
        }
    )


@blueprint.route('/api/get_genres/<int:chat_id>', methods=['GET'])
def get_genre(chat_id):
    db_sess = db_session.create_session()
    prof = db_sess.query(Profile).filter(Profile.chat_id == int(chat_id)).first()
    genres = prof.genres
    return jsonify(
        {
            'error': 'No error',
            'genres': genres
        }
    )


@blueprint.route('/api/new_genres/<int:chat_id>', methods=['POST'])
def new_genres(chat_id):
    if not req.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in req.json for key in
                 ['gen']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()

    prof = db_sess.query(Profile).filter(Profile.chat_id == chat_id).first()
    print(prof)
    prof.genres = req.json['gen']
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/add_bookmark/<int:chat_id>', methods=['POST'])
def new_bookmark(chat_id):
    if not req.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in req.json for key in
                 ['request']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()

    bm = Bookmarks()
    bm.chat_id = int(chat_id)
    bm.request = req.json['request']
    db_sess.add(bm)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/get_last_film/<int:chat_id>', methods=['GET'])
def get_last_film(chat_id):
    db_sess = db_session.create_session()
    prof = db_sess.query(History).filter(History.chat_id == int(chat_id), History.subject == 'film').all()
    if prof:
        return jsonify(
        {
            'film': prof[-1].request
        }
    )
    else:
        return jsonify(
        {
            'film': None
        }
    )