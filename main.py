
import sqlite3
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
DB_PATH = './posts.db'
PORT    = 8000

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db' 
db = SQLAlchemy(app)

global storage
storage = None



class Posts(db.Model):
    pid = db.Column(db.Integer, primary_key = True)
    post_id = db.Column(db.Integer(),unique=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(100))
    token = db.Column(db.String(100),default='')

    def __init__(self, post_id, title, content, token = ''):
        self.post_id = post_id
        self.title = title
        self.content = content
        self.token = token 


class PostsTotal(db.Model):
    pid = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(100))
    value = db.Column(db.Integer())

    def __init__(self, type, value):
        self.type = type
        self.value = value


class Storage:
    def __init__(self, db):
        self.db = db
        self.edges = {}
        self.edges['private'], self.edges['public'] = self._get_posts_edges()
        print(self.edges)

    def _get_posts_edges(self):
        try:
            pub = PostsTotal.query.filter(PostsTotal.type == 'public').first().value
            priv = PostsTotal.query.filter(PostsTotal.type == 'private').first().value
        except:
            priv, pub = 1, 1 
            public_obj = PostsTotal(type = 'public', value = 1)
            priavte_obj = PostsTotal(type = 'private', value = 1)
            self.db.session.add(public_obj)
            self.db.session.add(priavte_obj)
            self.db.session.commit()
        return priv, pub

    def _inc_posts_edge(self, edge_id):
        assert edge_id in ['private', 'public']

        edge = PostsTotal.query.filter(PostsTotal.type == edge_id).first()

        edge.value += 1
        self.db.session.commit()
        self.edges[edge_id] += 1

    def store_public_post(self, title, content):
        self._store_post(self.edges['public'] ,title, content)
        self._inc_posts_edge('public')

        return self.edges['public']  - 1

    def store_private_post(self, title, content,token):
        self._store_post(-self.edges['private'] ,title, content, token)
        self._inc_posts_edge('private')
        return -(self.edges['private'] - 1)

    def _store_post(self, post_id, title, content,token = ''):

        post_obj = Posts(post_id = post_id, title= title, content= content, token = token)
        self.db.session.add(post_obj)
        self.db.session.commit()

    def get_public_post(self, post_id):
        return self._get_post(post_id)

    def _get_post(self, post_id):

        post = Posts.query.filter(Posts.post_id == post_id).first()

        if post is None:
            return None

        return {'title': post.title, 'content': post.content}

    def get_private_post(self, post_id, token):
        post = Posts.query.filter(Posts.post_id == post_id).first()

        if post.token != token:
            return None

        return self._get_post(post_id)

@app.route('/get', methods=['GET'])
def get_post():
    global storage
    result_json = dict()

    if request.is_json:
        print request.json
        try:
            post_id = request.json['post_id']
            if post_id > 0:
                res = storage.get_public_post(post_id)

            elif post_id < 0:
                token = request.json['token']
                res = storage.get_private_post(post_id, token)

            else:
                result_json['status']   = 'error'
                result_json['data']     = 'Are you dumb or wut?'
                return result_json

            if res is None:
                result_json['status']   = 'error'
                result_json['data']     = 'No posts with such post_id or your token is incorrect'
            else:
                result_json['status']   = 'success'
                result_json['data']     = res

        except KeyError:
            result_json['status']   = 'error'
            result_json['data']     = 'Missing fields in JSON'

        except Exception as e:
            raise e
            result_json['status'] = 'error'
            result_json['data']   = 'An error occured on server side'

    else:
        result_json['status']   = 'error'
        result_json['data']     = 'Request isn\'t in JSON format'

    print result_json
    return jsonify(result_json)


@app.route('/store', methods = ['POST'])
def store_post():
    global storage
    result_json = dict()

    if request.is_json:
        try:
            title   = request.json['title']
            content = request.json['content']
            public  = request.json['public']

            if public:
                post_id = storage.store_public_post(title, content)

            else:
                token = request.json['token']
                post_id = storage.store_private_post(title, content, token)

            result_json['status'] = 'success'
            result_json['data']   = {'post_id': post_id}

        except KeyError as e:
            result_json['status']   = 'error'
            result_json['data']     = 'Missing fields in JSON'

        except Exception as e:
            raise e
            result_json['status'] = 'error'
            result_json['data']   = 'An error occured on server side'

    else:
        result_json['status']   = 'error'
        result_json['data']     = 'Request isn\'t in JSON format'

    print result_json
    return jsonify(result_json)


if __name__ == '__main__':
    db.create_all()

    global storage
    storage = Storage(db)

    app.run(host='0.0.0.0', port=PORT, debug=True)

