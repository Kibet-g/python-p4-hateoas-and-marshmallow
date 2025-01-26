#!/usr/bin/env python3

from faker import Faker
from app import app
from models import db, Newsletter

fake = Faker()

with app.app_context():
    Newsletter.query.delete()

    newsletters = [
        Newsletter(
            title=fake.text(max_nb_chars=20),
            body=fake.paragraph(nb_sentences=5),
        )
        for _ in range(50)
    ]

    db.session.add_all(newsletters)
    db.session.commit()
