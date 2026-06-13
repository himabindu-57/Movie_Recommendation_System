import streamlit as st
import bz2
import pickle
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- NETWORK SETUP ---
# 1. Set up a requests session to reuse the TCP connection
session = requests.Session()

# 2. Set up a retry strategy to handle dropped connections gracefully
retry_strategy = Retry(
    total=3,
    backoff_factor=0.5,  # Wait 0.5s, 1s, 2s between retries
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)


# --- FUNCTIONS ---
def fetch_poster(movie_id):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=a5e43c60312cd4e34e93e6eddd68b707&language=en-US'

        # Use session.get instead of requests.get
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Safely check if the poster path exists
        if data.get('poster_path'):
            return "https://image.tmdb.org/t/p/w500" + data['poster_path']
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster"

    except requests.exceptions.RequestException as e:
        # Catch network/connection errors and print them to the console
        print(f"Failed to fetch poster for movie_id {movie_id}: {e}")
        return "https://via.placeholder.com/500x750?text=No+Poster"


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for k in movies_list:
        movie_id = movies.iloc[k[0]].movie_id

        # appending recommended movies
        recommended_movies.append(movies.iloc[k[0]].title)

        # fetch movie posters from API
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters


# --- LOAD DATA ---
try:
    movies_dict = pickle.load(open('movies.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    # Load the compressed file
    with bz2.BZ2File('similarity.pbz2', 'rb') as f:
        similarity = pickle.load(f)
except FileNotFoundError:
    st.error(
        "Error: 'movies.pkl' or 'similarity.pkl' not found. Please ensure they are in the same directory as this script.")
    st.stop()

# --- STREAMLIT UI ---
st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    'What kind of movie do you like to watch?',
    movies['title'].tolist()
)

if st.button('Recommend'):
    # Show a loading spinner while fetching from the API
    with st.spinner('Fetching recommendations...'):
        names, posters = recommend(selected_movie_name)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0])

    with col2:
        st.text(names[1])
        st.image(posters[1])

    with col3:
        st.text(names[2])
        st.image(posters[2])

    with col4:
        st.text(names[3])
        st.image(posters[3])

    with col5:
        st.text(names[4])
        st.image(posters[4])