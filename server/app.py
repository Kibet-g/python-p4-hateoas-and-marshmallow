#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Newsletter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

ma = Marshmallow(app)
api = Api(app)

# Define the Marshmallow schema
class NewsletterSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Newsletter
        load_instance = True

    id = ma.auto_field()
    title = ma.auto_field()
    body = ma.auto_field()
    published_at = ma.auto_field()
    edited_at = ma.auto_field()

    url = ma.Hyperlinks(
        {
            "self": ma.URLFor("newsletterbyid", values=dict(id="<id>")),
            "collection": ma.URLFor("newsletters"),
        }
    )

# Instantiate single and multiple schemas
newsletter_schema = NewsletterSchema()
newsletters_schema = NewsletterSchema(many=True)

# Define API resources
class Index(Resource):
    def get(self):
        response_dict = {"index": "Welcome to the Newsletter RESTful API"}
        return make_response(response_dict, 200)

api.add_resource(Index, '/')

class Newsletters(Resource):
    def get(self):
        newsletters = Newsletter.query.all()
        return make_response(newsletters_schema.dump(newsletters), 200)

    def post(self):
        data = request.get_json()
        new_newsletter = Newsletter(
            title=data['title'],
            body=data['body'],
        )
        db.session.add(new_newsletter)
        db.session.commit()

        return make_response(newsletter_schema.dump(new_newsletter), 201)

api.add_resource(Newsletters, '/newsletters')

class NewsletterByID(Resource):
    def get(self, id):
        newsletter = Newsletter.query.get_or_404(id)
        return make_response(newsletter_schema.dump(newsletter), 200)

    def patch(self, id):
        newsletter = Newsletter.query.get_or_404(id)
        data = request.get_json()

        for key, value in data.items():
            setattr(newsletter, key, value)

        db.session.commit()
        return make_response(newsletter_schema.dump(newsletter), 200)

    def delete(self, id):
        newsletter = Newsletter.query.get_or_404(id)
        db.session.delete(newsletter)
        db.session.commit()

        return make_response({"message": "record successfully deleted"}, 200)

api.add_resource(NewsletterByID, '/newsletters/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
