from flask import Flask, redirect, request, jsonify, session
import requests
import urllib.parse
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = '1203120938120481048'

CLIENT_ID = 'MY_ID'
CLIENT_SECRET = 'MY_SECRET_ID'
REDIRECT_URI = 'http://localhost:8080/callback'

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

@app.route('/')
def index():
    return "Welcome to MusicMan <a href='/login'>Login with Spotify</a>"

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email user-top-read'
    
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }
    
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        
        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()
        
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
        
        return redirect('/recommendations')

@app.route('/recommendations')
def get_recommendations():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    # Set up request headers
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    seed_artists = get_top_artists()

    # Define request parameters
    params = {
        'seed_artists': ','.join(seed_artists),
        'limit': 10,
        'market': 'ES',
        ### WHEN IMPLEMENTING COHERE USE MAX/MIN DANCEABILITY AND MAYBE ACOUSTICNESS.
        'min_danceability': 0.5
    }

    # Make the request to the Spotify API
    response = requests.get('https://api.spotify.com/v1/recommendations', headers=headers, params=params)
    
    if response.status_code == 200:
        recommendations = response.json()

        # Extract and format the track names and artists
        track_info = [{'track_name': track['name'], 'artist_name': track['artists'][0]['name']} for track in recommendations['tracks']]
        
        return jsonify(track_info)
    else:
        return jsonify({'error': 'Unable to fetch recommendations'}), response.status_code

@app.route('/top_artists')
def get_top_artists():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    params = {
        'limit': 3,
    }
    
    # Make the request to the Spotify API
    response = requests.get('https://api.spotify.com/v1/me/top/artists', headers=headers, params=params)
    
    if response.status_code == 200:
        top_artists = response.json()

        # Extract the artist IDs from the user's top artists
        seed_artists = [artist['id'] for artist in top_artists['items']]
        
        return seed_artists
    else:
        return jsonify({'error': 'Unable to fetch top artists'}), response.status_code

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        
        response = request.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()
        
        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']
        
        return redirect('/recommendations')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
