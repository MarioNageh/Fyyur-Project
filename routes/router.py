import copy
import sys

from flask import Blueprint, render_template, flash, redirect, url_for, request
from models.model import Venue, Artist, db, Show

from forms import ArtistForm, ShowForm, VenueForm
import datetime

router = Blueprint('router', __name__)


@router.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@router.route('/venues')
def venues():
    venues = Venue.query.order_by(Venue.city).all()
    retunner = []
    current_city = None
    city_obj = {
        'city': '',
        'state': '',
        'venues': []
    }
    i = 0
    for ven in venues:
        ven_object = {
            "id": ven.id,
            "name": ven.name,
            "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.datetime.today(), ven.shows)))
        }
        if current_city is None:
            city_obj['city'] = ven.city
            city_obj['state'] = ven.state
            city_obj['venues'] = []
            city_obj['venues'].append(ven_object)
        elif current_city == ven.city:
            city_obj['venues'].append(ven_object)
        else:
            appended = copy.deepcopy(city_obj)
            retunner.append(appended)
            city_obj['city'] = ven.city
            city_obj['state'] = ven.state
            city_obj['venues'] = []
            city_obj['venues'].append(ven_object)
        current_city = ven.city
    appended = copy.deepcopy(city_obj)
    retunner.append(appended)

    return render_template('pages/venues.html', areas=retunner)


@router.route('/venues/search', methods=['POST'])
def search_venues():

    searchString = request.form.get('search_term')
    # here we will use Like Opreator spe ilike to Case Sentative
    filterdList = Venue.query.filter(Venue.name.ilike(f'%{searchString}%')).all()

    response = {
        "count": len(filterdList),
        "data": [{
            'id': x.id,
            'name': x.name,
            'num_upcoming_shows': len(list(filter(lambda y: y.start_time > datetime.datetime.today(), x.shows)))
        } for x in filterdList]
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@router.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    return render_template('pages/show_venue.html', venue=Venue.query.get(venue_id).get_show_oject())


@router.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@router.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        venues = Venue()
        venues.name = request.form['name']
        venues.city = request.form['city']
        venues.state = request.form['state']
        venues.address = request.form['address']
        venues.phone = request.form['phone']
        venues.facebook_link = request.form['facebook_link']
        venues.image_link = request.form['image_link']
        # Convert List To String Speated By ,
        venues.genres = ','.join(request.form.getlist('genres'))
        db.session.add(venues)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        if error:
            flash('Error ' + request.form['name'] + ' Error While Insert')
        else:
            flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


@router.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        # shows=
        Show.query.filter(Show.ven_id == venue_id).delete()
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash("Error While deleting")
        else:
            flash("Successful opreation")

    return redirect(url_for('router.index'))


@router.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    ven = Venue.query.get(venue_id)
    form = VenueForm(
        name=ven.name,
        city=ven.city,
        state=ven.state,
        address=ven.address,
        phone=ven.phone,
        genres=ven.genres.split(','),
        image_link=ven.image_link,
        facebook_link=ven.facebook_link
    )
    return render_template('forms/edit_venue.html', form=form, venue=ven)


@router.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    try:
        venues = Venue.query.get(venue_id)
        venues.name = request.form['name']
        venues.city = request.form['city']
        venues.state = request.form['state']
        venues.address = request.form['address']
        venues.phone = request.form['phone']
        venues.facebook_link = request.form['facebook_link']
        venues.image_link = request.form['image_link']
        venues.genres = ','.join(request.form.getlist('genres'))
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        if error:
            flash('Error ' + request.form['name'] + ' Error While Updating')
        else:
            flash('Venue ' + request.form['name'] + ' was successfully Updated!')
    return redirect(url_for('router.show_venue', venue_id=venue_id))


# Artist
#  ----------------------------------------------------------------

@router.route('/artists')
def artists():
    return render_template('pages/artists.html', artists=Artist.query.all())


@router.route('/artists/search', methods=['POST'])
def search_artists():
    searchString = request.form.get('search_term')
    response = Artist.query.filter(Artist.name.ilike(f'%{searchString}%')).all()
    responses = {
        "count": len(response),
        "data": [{
            "id": x.id,
            "name": x.name,
            "num_upcoming_shows": len(list(filter(lambda y: y.start_time > datetime.datetime.today(), x.shows))),
        } for x in response]
    }
    return render_template('pages/search_artists.html', results=responses,
                           search_term=request.form.get('search_term', ''))


@router.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    return render_template('pages/show_artist.html', artist=Artist.query.get(artist_id).get_show_ojb())


@router.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(
        name=artist.name,
        genres=artist.genres.split(','),
        city=artist.city,
        state=artist.state,
        phone=artist.phone,
        website=artist.website,
        facebook_link=artist.facebook_link,
        image_link=artist.image_link,
        seeking_description=artist.seeking_description
    )
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@router.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@router.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    try:
        artist = Artist()
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.facebook_link = request.form['facebook_link']
        artist.image_link = request.form['image_link']
        # Convert List To String Speated By ,
        artist.genres = ','.join(request.form.getlist('genres'))
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('Artist ' + request.form['name'] + ' was Error In Inserting')
        else:
            flash("Artist " + request.form['name'] + ' Was Inserted Succ!')
    return render_template('pages/home.html')


@router.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.facebook_link = request.form['facebook_link']
        artist.image_link = request.form['image_link']
        # Convert List To String Speated By ,
        artist.genres = ','.join(request.form.getlist('genres'))
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('Artist ' + request.form['name'] + ' was Error In Inserting')
        else:
            flash("Artist " + request.form['name'] + ' Was Updated Succ!')
    return redirect(url_for('router.show_artist', artist_id=artist_id))


#  Shows
#  ----------------------------------------------------------------

@router.route('/shows')
def shows():
    data = [{
        "venue_id": x.venue.id,
        "venue_name": x.venue.name,
        "artist_id": x.artist.id,
        "artist_name": x.artist.name,
        "artist_image_link": x.artist.image_link,
        "start_time": str(x.start_time)
    } for x in Show.query.filter(Show.start_time > datetime.datetime.today()).all()]
    return render_template('pages/shows.html', shows=data)


@router.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@router.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        shows = Show()
        shows.artist_id = request.form['artist_id']
        shows.ven_id = request.form['venue_id']
        shows.start_time = request.form['start_time']
        db.session.add(shows)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        if error:
            flash('Error In Add New Show')
        else:
            flash('Show was successfully listed!')
    return render_template('pages/home.html')




