#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from distutils.log import error
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy.orm import relationship
from models import db, Venue, Artist, Show


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  endtimes = Venue.query.order_by(Venue.state, Venue.city).all()
  data = []
  endtimes = Venue.query.distinct(Venue.city, Venue.state).all()
  for result in endtimes:
        home_city = {
            "city": result.city,
            "state": result.state
        }
  venues_query = Venue.query.filter_by(city=result.city, state=result.state).all()
  home_venues = []
  for venue in venues_query:
            home_venues.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==1).filter(Show.start_time>datetime.now()).all())
            })
        
  home_city["venues"] = home_venues
  data.append(home_city)
  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()

  data = []
  for venue in venues:
        venue_search = {}
        venue_search['id'] = venue.id
        venue_search['name'] = venue.name
        venue_search['num_upcoming_shows'] = len(venue.shows)
        data.append( venue_search)

  response = {}
  response['count'] = len(data)
  response['data'] = data

  return render_template('pages/search_venues.html',results=response,search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)

  upcoming_shows = []
  past_shows = []


  endtime = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
 
  for show in  endtime:
    past_shows.append({
      "artist_id": show.artist_id,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  for show in endtime:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")    
    })

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  try:
    form = VenueForm(request.form)
    venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data)
    
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash("Venue was not successfully listed.")
  finally:
    db.session.close()

  return redirect(url_for("index"))

  
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash(f'Venue {venue_id} was successfully deleted.')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(f'An error occurred. Venue {venue_id} could not be deleted.')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')
  
        

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = db.session.query(Artist.id, Artist.name).all()
  
  # TODO: replace with real data returned from querying the database
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  endtime = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  response = {}
  response['count'] = len(endtime)
  response['data'] = endtime
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist_endtime = db.session.query(Artist).get(artist_id)

  past_shows = []
  upcoming_shows = []

  endtime_artists = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  

  for show in endtime_artists:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  for show in endtime_artists:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })


  data = {
    "id": artist_endtime.id,
    "name": artist_endtime.name,
    "genres": artist_endtime.genres,
    "city": artist_endtime.city,
    "state": artist_endtime.state,
    "phone": artist_endtime.phone,
    "website": artist_endtime.website,
    "facebook_link": artist_endtime.facebook_link,
    "seeking_venue": artist_endtime.seeking_venue,
    "seeking_description": artist_endtime.seeking_description,
    "image_link": artist_endtime.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  
  
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  return render_template('pages/show_artist.html', artist=data)
  

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm()  
  artist = Artist.query.get(artist_id)

  if artist: 
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    tmp_genres = request.form.getlist('genres')
    artist.genres = ','.join(tmp_genres)
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_description = request.form['seeking_description']
    db.session.add(artist)
    db.session.commit()
          # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash("Artist was not successfully listed.")
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.genres.data = venue.genres.split(",")
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    tmp_genres = request.form.getlist('genres')
    venue.genres = ','.join(tmp_genres)  
    venue.facebook_link = request.form['facebook_link']
    db.session.add(venue)
    db.session.commit()
          # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  except: 
    db.session.rollback()
    print(sys.exc_info())
    flash("Artist was not successfully listed.")
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  artist = Artist()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try: 
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    tmp_genres = request.form.getlist('genres')
    artist.genres = ','.join(tmp_genres)
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_description = request.form['seeking_description']
    db.session.add(artist)
    db.session.commit()
    
    # on successful db insert, flash success
    flash("Artist " + request.form["name"] + " was successfully listed!")
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
   
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.all()

    data = []
    for show in shows:
        data.append({
            'venue_id': show.venue.id,
            'venue_name': show.venue.name,
            'start_time': show.start_time.isoformat()
        })
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  show = Show()
  
  try:
    show.artist_id = request.form['artist_id']
    show.venue_id = request.form['venue_id']
    show.start_time = request.form['start_time']
    db.session.add(show)
    db.session.commit()
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash("Artist was not successfully listed.")
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
