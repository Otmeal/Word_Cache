from main_app import db


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    parts_of_speech = db.relationship("PartOfSpeech", backref="word", lazy="subquery")


class PartOfSpeech(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    form = db.Column(db.String(20))
    pos = db.Column(db.String(20))
    counting = db.Column(db.String(20))

    word_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    prons_set = db.relationship("Pronunciations", backref="pos", lazy="subquery")
    definition_sets = db.relationship("DefinitionSet", backref="pos", lazy="subquery")


class Pronunciations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uk_pron = db.Column(db.String(30))
    us_pron = db.Column(db.String(30))
    pos_id = db.Column(db.Integer, db.ForeignKey("part_of_speech.id"))


class DefinitionSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    sense = db.Column(db.String(20))

    pos_id = db.Column(db.Integer, db.ForeignKey("part_of_speech.id"))
    definition_units = db.relationship(
        "DefinitionUnit", backref="definition_set", lazy="subquery"
    )


class DefinitionUnit(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    phrase_title = db.Column(db.String(30))
    counting = db.Column(db.String(20))
    variant_name = db.Column(db.String(20))
    label = db.Column(db.String(20))
    english_definition = db.Column(db.String(150))
    chinese_definition = db.Column(db.String(50))

    definition_set_id = db.Column(db.Integer, db.ForeignKey("definition_set.id"))
