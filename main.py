from enum import unique
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,FloatField,URLField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api_key='98e1a4d4f62b6756e8cc514c113448cb'
movie_db_image_url='https://image.tmdb.org/t/p/w500'
app.config['SECRET_KEY'] = 'Api Key'
Bootstrap(app)

class Movies(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    year=db.Column(db.Integer,nullable=False)
    description =db.Column(db.String(500), nullable=False)
    rating=db.Column(db.Float,nullable=True)
    ranking=db.Column(db.Integer,nullable=True)
    review=db.Column(db.String(1000),nullable=True)
    img_url=db.Column(db.String(1000),nullable=False)

    def __repr__(self):
        return f"<Book {self.title}>"
db.create_all()

class EditForm(FlaskForm):
    rating=StringField('Rating')
    review=StringField('Review')

    submit=SubmitField('Submit')

class MovieAddForm(FlaskForm):
    title=StringField('Title',validators=[DataRequired()])  
    submit=SubmitField('Add')

@app.route("/")
def home():
    all_movies=Movies.query.order_by(Movies.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking=len(all_movies)-i
    db.session.commit()

    
    return render_template("index.html",movies=all_movies)

@app.route("/edit",methods=['GET','POST'])
def edit():
    form=EditForm()
    movie_id=request.args.get('id')
    movie=Movies.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating=request.form['rating']
        movie.review=request.form['review']

        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html",movie=movie,form=form)    

@app.route("/delete")
def delete():
    movie_id=request.args.get('id')
    movie_to_delete=Movies.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add",methods=['GET','POST'])
def addmovie():
    form=MovieAddForm()
    if form.validate_on_submit():
        movie_title=request.form['title']
        response=requests.get(f'https://api.themoviedb.org/3/search/movie',params={'api_key':api_key,'query':movie_title})
        data=response.json()['results']
        return render_template("select.html",options=data)
    return render_template("add.html",form=form)

@app.route("/select")
def select():
    movie_id=request.args.get('id')
    if movie_id:
        response=requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}',params={'api_key':api_key})
        data=response.json()
        new_movie=Movies(
            title=data['title'],
            year=data['release_date'].split('-')[0],
            description=data['overview'],
            img_url=f"{movie_db_image_url}{data['poster_path']}",

        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html")
# db.session.add(new_movies)
# db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
