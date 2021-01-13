from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.orm import backref
from sqlalchemy.sql import func
from datetime import datetime

db = SQLAlchemy()


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # Here Will Do Inner Join With All Shows
    # backref=backref("Venue", cascade="all, delete-orphan")
    shows = db.relationship('Show', backref='Venue', order_by='Show.start_time')
    # Here Will get The Artis from Shows then we need secondary [Many To Many]
    artist = db.relationship('Artist', secondary='shows')
    genres = db.Column(db.String())
    website = db.Column(db.String())
    seeking_description = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        if len(self.shows) > 0:
            print(self.shows)
        return f'< {self.id} -> {self.name} -> {self.city}  ----> '

    # Here We Will Overide The to_dict to get It From Query Dircet
    def get_show_oject(self):
        past_shows = db.session.query(Artist, Show).join(Show).join(Venue). \
            filter(
            Show.ven_id == self.id,
            Show.artist_id == Artist.id,
            Show.start_time < datetime.now()
        ). \
            all()
        upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue). \
            filter(
            Show.ven_id == self.id,
            Show.artist_id == Artist.id,
            Show.start_time > datetime.now()
        ). \
            all()

        pastShows = [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows]
        upcomingShows = [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows]
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'genres': self.genres.split(',') if self.genres is not None else '',
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'website': self.website,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'past_shows': pastShows,
            'upcoming_shows': upcomingShows,
            'past_shows_count': len(pastShows),
            'upcoming_shows_count': len(upcomingShows),
        }


class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)

    shows = db.relationship("Show", backref='Artist', order_by='Show.start_time')
    venue = db.relationship('Venue', secondary='shows')
    genres = db.Column(db.String())

    def __repr__(self):
        return f' The Artist name is {self.name}'

    # self.genres.split(',') if self.genres is not None else '',
    def get_show_ojb(self):
        pastVenesData = db.session.query(Venue, Show).join(Show).join(Artist). \
            filter(
            Show.artist_id == self.id,
            Show.ven_id == Venue.id,
            Show.start_time < datetime.now()
        ). \
            all()
        upcomingVeneData = db.session.query(Venue, Show).join(Show).join(Artist). \
            filter(
            Show.artist_id == self.id,
            Show.ven_id == Venue.id,
            Show.start_time > datetime.now()
        ). \
            all()
        pastVene = [{
            'venue_id': show.venue.id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        } for
            artist, show in pastVenesData
        ]
        upcomingVene = [{
            'venue_id': show.venue.id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        } for
            artist, show in upcomingVeneData
        ]
        return {
            "id": self.id,
            "name": self.name,
            "genres": self.genres.split(',') if self.genres is not None else '',
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "website": self.website,
            "facebook_link": self.facebook_link,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description,
            "image_link": self.image_link,
            "past_shows": pastVene,
            "upcoming_shows": upcomingVene,
            "past_shows_count": len(pastVene),
            "upcoming_shows_count": len(upcomingVene),
        }


class Show(db.Model):
    # Juncation Table
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    ven_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'), nullable=False)
    # start_time = db.Column(db.DateTime(timezone=True), nullable=False, default=func.now())
    start_time = db.Column(db.DateTime, nullable=False, default=func.now())

    artist = db.relationship('Artist')
    venue = db.relationship('Venue')

    def __repr__(self):
        return f'<Ven {self.id} -> {self.artist.name} -> {self.venue.name} -> {self.start_time}'

    def getArtist(self):
        return {
            'artist_id': self.artist_id,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'artist_name': self.artist.name,
            'artist_image_link': self.artist.image_link
        }

    def getVenu(self):
        return {
            'venue_id': self.venue.id,
            'venue_name': self.venue.name,
            'venue_image_link': self.venue.image_link,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        }

# ----------------------------------------------------------------------------#
# End - - Models.
# ----------------------------------------------------------------------------#
