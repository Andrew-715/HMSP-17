from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

movie_ns = api.namespace('movie')
director_ns = api.namespace('director')
genre_ns = api.namespace('genre')

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

movie_schema = MovieSchema(many=True)


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director = request.args.get(Movie.director)

        if director is None:
            movies = Movie.query.all()
            return movie_schema.dump(movies), 200
        else:
            movies = Movie.query.filter(Movie.director == Movie.director_id)
            return movie_schema.dump(movies), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return '', 201

@movie_ns.route('/<int:mid>/')
class MovieView(Resource):
    def get(self, mid:int):
        try:
            movie = Movie.query.get(mid)
            return movie_schema.dump(movie), 200
        except Exception:
            return '', 404

    def put(self, mid:int):
        movie = Movie.query.get(mid)
        req_json = request.json
        movie.title = req_json.get('title')
        movie.description = req_json.get('description')
        movie.trailer = req_json.get('trailer')
        movie.year = req_json.get('year')
        movie.rating = req_json.get('rating')
        movie.genre_id = req_json.get('genre_id')
        movie.director_id = req_json.get('director_id')
        with db.session.begin():
            db.session.add(movie)
            db.session.commit()
        return '', 204

    def delete(self, mid:int):
        movie = Movie.query.get(mid)
        with db.session.begin():
            db.session.delete(movie)
            db.session.commit()
        return '', 204

@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return '', 201

    def put(self, did:int):
        director = Director.query.get(did)
        req_json = request.json
        director.name = req_json.get('name')
        with db.session.begin():
            db.session.add(director)
            db.session.commit()
        return '', 204

    def delete(self, did:int):
        director = Director.query.get(did)
        with db.session.begin():
            db.session.delete(director)
            db.session.commit()
        return '', 204


@genre_ns.route('/<int:gid>')
class GenreView(Resource):
    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return '', 201

    def put(self, gid:int):
        genre = Genre.query.get(gid)
        req_json = request.json
        genre.name = req_json.get('name')
        with db.session.begin():
            db.session.add(genre)
            db.session.commit()
        return '', 204

    def delete(self, gid:int):
        genre = Genre.query.get(gid)
        with db.session.begin():
            db.session.delete(genre)
            db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
