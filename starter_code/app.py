#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import datetime # -- Additional import statment for DateTime data type
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

  

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

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(250), nullable = True)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.Text, default='')
    shows_list = db.relationship('Show',back_populates="venue")

    # TODO: Additional challenges
    created_on = db.Column(db.DateTime(), nullable = False)

    def __init__(self,name,city,state,address,phone,image_link,facebook_link,website,seeking_talent,seeking_description,genres):
      self.name = name
      self.city = city
      self.state = state
      self.address = address
      self.phone = phone
      self.image_link = image_link
      self.facebook_link = facebook_link
      self.website = website
      self.seeking_talent = seeking_talent
      self.seeking_description = seeking_description
      self.genres = genres
      self.created_on = datetime.now()


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.Text)
    venues_list = db.relationship("Show",back_populates='artist')
    

    # # TODO: Additional challenges
    available_time = db.Column(db.String(100))
    created_on = db.Column(db.DateTime())

    def __init__(self,name,city,state,phone,image_link,facebook_link,website,seeking_venue,seeking_description,genres, available_time):
      self.name = name
      self.city = city
      self.state = state
      self.phone = phone
      self.image_link = image_link
      self.facebook_link = facebook_link
      self.website = website
      self.seeking_venue = seeking_venue
      self.seeking_description = seeking_description
      self.genres = genres
      self.available_time = available_time
      self.created_on = datetime.now()

#  >>>> googled the error in the picture you've upload and the only answer i found is this https://stackoverflow.com/questions/51256373/flask-migrate-db-upgrade-fails-with-relation-does-not-exist
#  >>>> just moved the Show class below the two tables, it worked fine for me and i hope everything works for you as well.
class Show(db.Model):# table was  implemented as an association model (show = db.Table()) and has been removed and add again as Association Object with proper class assignement using flask migrate
  __tablename__ = 'Show'

  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),primary_key=True)
  start_time = db.Column(db.DateTime(), nullable = False)
  artist = db.relationship("Artist",back_populates='venues_list')
  venue = db.relationship("Venue",back_populates='shows_list')

  def __init__(self,start_time):
    self.start_time = start_time    

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  recent_artist = Artist.query.order_by(Artist.created_on).limit(10).all()
  recent_venues = Venue.query.order_by(Venue.created_on).limit(10).all()
  return render_template('pages/home.html',artists = recent_artist, venues = recent_venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = Venue.query.all()

  cities = sorted(set([(venue.city.capitalize(),venue.state) for venue in data]))
  cities = list(dict(city=c,state=s,
                venues=[dict(id=v.id,name=v.name) for v in data if v.city.capitalize() == c]) 
              for c,s in cities) # nested list comprehension 
  # 
  return render_template('pages/venues.html', areas=cities)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = Venue.query.filter(Venue.name.ilike('%'+request.form.get('search_term')+'%')).all()
  response = dict(count = len(data),data=[dict(id=ele.id,name=ele.name) for ele in data])

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = db.session.query(Artist.name,Artist.image_link,
                          Show.artist_id,Show.start_time)\
                            .join(Show.artist,Show.venue)\
                            .filter(Venue.id == venue_id).all()
  past_shows = []
  upcoming_shows = []
  for infos in data:
    event = dict(artist_id= infos[2],artist_name=infos[0],artist_image_link=infos[1],start_time=infos[3])
    if event['start_time'] > datetime.now():
      event['start_time'] = event['start_time'].strftime("%d %b, %Y at %H:%M")
      upcoming_shows.append(event)
    else:
      event['start_time'] = event['start_time'].strftime("%d %b, %Y at %H:%M")
      past_shows.append(event)

  venue = Venue.query.get(venue_id).__dict__
  venue['genres'] = venue['genres'].split(',')
  venue['past_shows'] = past_shows
  venue['past_shows_count'] = len(past_shows)
  venue['upcoming_shows'] = upcoming_shows
  venue['upcoming_shows_count'] = len(upcoming_shows)
  
  return render_template('pages/show_venue.html', venue=venue)

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
  try:
    data = request.form
    genres = ','.join(data.getlist('genres'))
    seeking = True if data["seeking_talent"] == 'Yes' else False
    venue = Venue(data['name'],data['city'].capitalize(),data['state'],
                  data['address'],data['phone'],data['image_link'],
                  data['facebook_link'],data['website'],seeking,
                  data['seeking_description'],genres)
    db.session.add(venue)
    db.session.commit()
      # on successful db insert, flash success
    flash('Venue ' + data['name'] + ' was successfully listed!','success')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')
  except Exception as e:
    print(e)
    flash('Server encountered an error while processing the data','danger')
    return redirect(url_for('create_venue_form'))


@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  print(venue_id)
  try:
    venue = Venue.query.get(venue_id)
    name = venue.name
    db.session.delete(venue)
    db.session.commit()
    flash('Successfully deleted '+name+' venue' ,'success')
    return redirect(url_for('venues'))
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('Problem occured while deleting '+name,'danger')
    return redirect(url_for('venues'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('venues'))



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = [dict(id=a.id,name=a.name) for a in artists]
 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = Artist.query.filter(Artist.name.ilike('%'+request.form.get('search_term')+'%')).all()
  response = dict(count = len(data),data=[dict(id=ele.id,name=ele.name) for ele in data])

 
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  from sqlalchemy import func
  # shows the venue page with the given venue_id
  
  data = db.session.query(Venue.name,Venue.image_link,
                          Show.venue_id,Show.start_time)\
                            .join(Show.artist,Show.venue)\
                            .filter(Artist.id == artist_id).all()
  
  past_shows = []
  upcoming_shows = []
  for infos in data:
    event = dict(venue_id= infos[2],venue_name=infos[0],venue_image_link=infos[1],start_time=infos[3])
    if event['start_time'] > datetime.now():
      event['start_time'] = event['start_time'].strftime("%d %B, %Y at %H:%M")
      upcoming_shows.append(event)
    else:
      event['start_time'] = event['start_time'].strftime("%d %B, %Y at %H:%M")
      past_shows.append(event)
  
  artist = Artist.query.get(artist_id).__dict__
  artist['genres'] = artist['genres'].split(',')
  artist['past_shows'] = past_shows
  artist['past_shows_count'] = len(past_shows)
  artist['upcoming_shows'] = upcoming_shows
  artist['upcoming_shows_count'] = len(upcoming_shows)
  # TODO: replace with real venue data from the venues table, using venue_id
 
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id).__dict__
  artist['genres'] = artist['genres'].split(',')
  print(artist)
 
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  data = request.form
  artist = Artist.query.get(artist_id)

  artist.name = data['name']
  artist.city = data['city'].capitalize()
  artist.state= data['state']
  artist.phone= data['phone']
  artist.image_link = data['image_link']
  artist.facebook_link = data['facebook_link']
  artist.website = data['website']
  artist.seeking_venue = True if data['seeking_venue'] == 'Yes' else False
  artist.seeking_description = data['seeking_description']
  artist.genres = ','.join(request.form.getlist('genres'))
  artist.available_time = data['available_from']

  try:
    db.session.commit()
    flash('Information updated successfully','success')
    return redirect(url_for('show_artist', artist_id=artist_id))
  except Exception as f:
    db.session.rollback()
    print(f)
    flash('An error has occured in the server while processing changes','danger')
    return redirect(url_for('show_artist', artist_id=artist_id))
    

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id).__dict__
  venue['genres'] = venue['genres'].split(',')
 
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  data = request.form
  venue = Venue.query.get(venue_id)

  venue.name = data['name']
  venue.city = data['city'].capitalize()
  venue.state= data['state']
  venue.phone= data['phone']
  venue.address = data['address']
  venue.image_link = data['image_link']
  venue.facebook_link = data['facebook_link']
  venue.website = data['website']
  venue.seeking_talent = True if data['seeking_talent'] == 'Yes' else False
  venue.seeking_description = data['seeking_description']
  venue.genres = ','.join(request.form.getlist('genres'))

  try:
    db.session.commit()
    flash('Information updated successfully','success')
    return redirect(url_for('show_venue', venue_id=venue_id))
  except Exception as f:
    db.session.rollback()
    print(f)
    flash('An error has occured in the server while processing changes','danger')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    data = request.form
    genres = ','.join(data.getlist('genres'))
    seeking = True if data["seeking_venue"].capitalize() == 'Yes' else False
    available = data['available_from'] +' - '+ data['available_to']
    artist = Artist(data['name'],data['city'].capitalize(),data['state'],
                  data['phone'],data['image_link'],
                  data['facebook_link'],data['website'],seeking,
                  data['seeking_description'],genres,available)

    db.session.add(artist)
    db.session.commit()
      # on successful db insert, flash success
    flash('Artist ' + data['name'] + ' was successfully listed!','success')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')
  except Exception as e:
    print('ERROR!: ',e)
    flash('Server encountered an error while processing the data','danger')
    return redirect(url_for('create_venue_form'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = db.session.query(Venue.id, Venue.name,
                          Artist.id, Artist.name, Artist.image_link,
                          Show.start_time)\
                            .join(Show.artist, Show.venue)\
                            .order_by(Show.start_time).all()
  
  shows = [dict(venue_id=s[0],venue_name=s[1],artist_id=s[2],artist_name=s[3],artist_image_link=s[4],start_time=s[5].strftime("%d %b, %Y at %H:%M")) for s in data]
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
 
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  data = request.form
  venue = Venue.query.get(int(data['venue_id']))
  artist = Artist.query.get(int(data['artist_id']))
  try:
    start_time = datetime.strptime(data['start_time'],'%Y-%m-%dT%H:%M')
    show = Show(start_time) # create istance of the Association model with the given start_time column value.
    venue.shows_list.append(show) #append that instance to the relational attribute of the Venue class (venue.shows_list), it will add the id of venue to the Object(show.venue_id)
    show.artist = artist # then assign artist object to the relational attribute (show.artist ), it will update the attribute (show.artist_id) automaticly.
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!','success')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')
  except Exception as s:
    db.session.rollback()
    print(s)
    flash('Due to server error we could not add the show','danger')
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
    app.run(host='0.0.0.0')

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
