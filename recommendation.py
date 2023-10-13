import cohere
from cohere.responses.classify import Example
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify

# Define your client ID, client secret, and redirect URI
client_id = "MY_ID"
client_secret = "MY_SECRET_ID"
redirect_uri = "https://accounts.spotify.com/en/login?flow_ctx=ff6d1333-3803-4bf3-bb39-203f1eede22c:1697002799"

# Create a SpotifyOAuth instance
sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

# Get the access token
access_token_info = sp_oauth.get_cached_token()

# Check if the access token is valid and get a new one if needed
if not access_token_info:
    auth_url = sp_oauth.get_authorize_url()
    print(f"Visit this URL to authorize the application: {auth_url}")
    response = input("Enter the URL you were redirected to: ")
    code = sp_oauth.parse_response_code(response)
    access_token_info = sp_oauth.get_access_token(code)

# Create a Spotify instance using the access token
sp = Spotify(auth_manager=sp_oauth)

# Search for tracks
results = sp.search(q='track:dancing', type='track')
print(results)





def recommend_songs(user_response):
    co = cohere.Client('COHERE_ID')
    classifications = co.classify(
        model='embed-english-v2.0',
        inputs=["I did not fail the test today", "I failed my math test today","4/10"],
        examples=[
            Example("I had lots of fun at the park", "positive"), 
            Example("My friend came over to play Minecraft", "positive"),
            Example("I passed my exam", "positive"),
            Example("I am feeling optimistic", "positive"),
            Example("I got a lot of work done today", "positive"),
            Example("I am grateful for the opportunities I have", "positive"),
            Example("10/10", "positive"),
            Example("I am happy", "positive"),
            Example("I feel energized", "positive"),
            Example("I have had a long day", "negative"),
            Example("I am apprehensive", "negative"),
            Example("No one came to my thanksgiving dinner", "negative"),
            Example("My day was good", "negative"),
            Example("My day was very bad", "negative"),
            Example("I am not happy", "negative"),
            Example("I have lots of work that I still have to do", "negative"),
            Example("I am very stressed", "negative"),
            Example("I am not feeling very well", "negative"),
            Example("I am worried", "negative"),
            Example("I am sad", "negative"),
            Example("I did not complete my goals for today", "negative"),
            Example("1/10", "negative")])
    print('The confidence levels of the labels are: {}'.format(
        classifications.classifications
    ))
    
    response = co.chat(
        message="hello"
    )
    print(response)
    
#recommend_songs("")
