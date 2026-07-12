from flask import Flask, render_template, abort
from config import BOT_TOKEN, CHANNEL_LINK
import database

app = Flask(__name__)

@app.route('/')
def index():
    movies = database.get_all_movies()
    return render_template('index.html', movies=movies, BOT_TOKEN=BOT_TOKEN)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = database.get_movie(movie_id)  # (id, title, desc, poster_path, created_at, channel_msg_id)
    if not movie:
        abort(404)
    
    # Telegram Video ဆီတန်းသွားမယ့် Link
    telegram_msg_link = f"{CHANNEL_LINK}/{movie[5]}"  # movie[5] က channel_msg_id
    poster_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{movie[3]}"  # movie[3] က poster_path
    
    return render_template(
        'movie.html',
        movie=movie,
        poster_url=poster_url,
        telegram_link=telegram_msg_link
    )

if __name__ == '__main__':
    database.init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
