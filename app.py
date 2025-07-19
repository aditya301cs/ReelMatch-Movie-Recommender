import streamlit as st
import pickle
import os
import requests
import concurrent.futures
from streamlit.components.v1 import html

# Page config
st.set_page_config(page_title="ReelMatch: Movie Recommender", page_icon="🍿", layout="wide")

# Load data
# with open('movie_data.pkl', 'rb') as f:
#     movies, cosine_sim = pickle.load(f)

# --------------------- Check for Data File ---------------------
DATA_FILE = 'movie_data.pkl'
DATA_URL = 'https://drive.google.com/file/d/1vR9uPEw8cQGx23_uGOCfN0BxGVGGttYY/view?usp=sharing'  # Optional: Add a public file URL here if hosting externally

# st.write("📂 Current directory files:", os.listdir())
#
# if not os.path.exists(DATA_FILE):
#     if DATA_URL:
#         st.warning("🔄 Downloading movie_data.pkl from external source...")
#         try:
#             r = requests.get(DATA_URL, timeout=10)
#             with open(DATA_FILE, 'wb') as f:
#                 f.write(r.content)
#             st.success("✅ movie_data.pkl downloaded successfully.")
#         except:
#             st.error("❌ Failed to download movie_data.pkl. Please check the URL.")
#             st.stop()
#     else:
#         st.error("❌ `movie_data.pkl` not found. Upload it to the same folder or repo.")
#         st.stop()

# --------------------- Load Movie Data ---------------------
with open(DATA_FILE, 'rb') as f:
    movies, cosine_sim = pickle.load(f)


API_KEY = "3b3778403271ce6f2c2b9377fa3dc77b"

@st.cache_data(show_spinner=False)
def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()
        poster_path = data.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w300{poster_path}" if poster_path else "https://via.placeholder.com/300x450?text=No+Poster"
        tmdb_url = f"https://www.themoviedb.org/movie/{movie_id}"
        rating_tmdb = data.get("vote_average", "N/A")
        imdb_id = data.get("imdb_id")
        year = data.get("release_date", "N/A")[:4] if data.get("release_date") else "N/A"
        overview = data.get("overview", "No description available.").replace('"', '&quot;')

        rating_imdb = "N/A"
        if imdb_id:
            try:
                omdb_url = f"http://www.omdbapi.com/?i={imdb_id}&apikey=4a3b711b"
                omdb_res = requests.get(omdb_url, timeout=5).json()
                rating_imdb = omdb_res.get("imdbRating", "N/A")
            except:
                pass

        trailer_url = "#"
        vids_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"
        vids_res = requests.get(vids_url, timeout=5).json()
        for vid in vids_res.get("results", []):
            if vid["site"] == "YouTube" and vid["type"] == "Trailer":
                trailer_url = f"https://www.youtube.com/watch?v={vid['key']}"
                break

        return poster_url, tmdb_url, rating_tmdb, rating_imdb, year, overview, trailer_url
    except:
        return "https://via.placeholder.com/300x450?text=Error", "#", "N/A", "N/A", "N/A", "Error retrieving info.", "#"

@st.cache_data(show_spinner=False)
def get_recommendations(title):
    try:
        idx = movies[movies['title'] == title].index[0]
    except:
        return [], []
    sim_scores = sorted(list(enumerate(cosine_sim[idx])), key=lambda x: x[1], reverse=True)[1:11]
    movie_indices = [i[0] for i in sim_scores]
    titles = movies['title'].iloc[movie_indices].values
    ids = movies['movie_id'].iloc[movie_indices].values
    with concurrent.futures.ThreadPoolExecutor() as executor:
        details = list(executor.map(fetch_movie_details, ids))
    return titles, details

# --------------------- CSS Styling ---------------------
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        background-color: #0d0d0d;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    .main-title {
        text-align: center;
        font-size: 48px;
        font-weight: bold;
        color: #E50914;
        margin-bottom: 0;
    }
    .subtitle-bar {
        height: 4px;
        background: linear-gradient(to right, #E50914, #ff0066, #E50914);
        width: 320px;
        margin: 0 auto 30px auto;
        border-radius: 2px;
        animation: glow 2s ease-in-out infinite alternate;
    }
    @keyframes glow {
        from { box-shadow: 0 0 5px #E50914; }
        to { box-shadow: 0 0 20px #ff0066; }
    }
    .movie-card {
        position: relative;
        background-color: #1c1c1c;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.7);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .movie-card:hover {
        transform: scale(1.03);
        box-shadow: 0 0 12px #e50914;
    }
    .poster-wrapper {
        position: relative;
    }
    .overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(0, 0, 0, 0.6);
        color: #fff;
        padding: 10px;
        opacity: 0;
        transform: translateY(100%);
        transition: all 0.4s ease-in-out;
        font-size: 12px;
        border-bottom-left-radius: 8px;
        border-bottom-right-radius: 8px;
        pointer-events: none;
        backdrop-filter: blur(6px);
    }
    .poster-wrapper:hover .overlay {
        opacity: 1;
        transform: translateY(0);
    }
    .movie-caption {
        text-align: center;
        font-weight: 500;
        color: #ccc;
        margin: 4px 0 0 0;
    }
    .rating {
        text-align: center;
        font-size: 14px;
        color: #ffcc00;
    }
    .trailer-button button {
        width: 100%;
        margin-top: 5px;
        background-color: #E50914;
        color: white;
        border: none;
        padding: 8px;
        border-radius: 4px;
        font-weight: bold;
        transition: box-shadow 0.3s ease-in-out;
    }
    .trailer-button button:hover {
        box-shadow: 0 0 12px #E50914, 0 0 20px #ff0066;
        cursor: pointer;
    }
    .footer {
        text-align: center;
        color: #888;
        font-size: 13px;
        padding: 25px 0 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------- Header ---------------------
st.markdown('<div class="main-title">🍿ReelMatch: Find Your Perfect Movie Night</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-bar"></div>', unsafe_allow_html=True)

# --------------------- Auto-Scrolling Carousel ---------------------
carousel_ids = [278, 238, 155, 680, 13, 807, 120, 122, 550, 89,
                389, 424, 11, 27205, 46738, 872585, 11036, 359724, 980489, 76,
                9919, 11036, 244786]
poster_urls = [fetch_movie_details(mid)[0] for mid in carousel_ids]

carousel_html = f"""
<div style="width: 100%; overflow: hidden; background-color: #000;">
    <div style="display: flex; gap: 15px; width: max-content; animation: scroll 40s linear infinite;">
        {''.join([f'<img src="{url}" style="width: 150px; height: 225px; border-radius: 8px;">' for url in poster_urls])}
    </div>
</div>

<style>
@keyframes scroll {{
    0% {{ transform: translateX(100%); }}
    100% {{ transform: translateX(-100%); }}
}}
</style>
"""
html(carousel_html, height=250)

# --------------------- Recommendation System ---------------------
st.markdown("### 🔍 Select a Movie to Get Recommendations")
selected_movie = st.selectbox("Choose a movie you like:", movies['title'].values)

if st.button("Show Recommendations"):
    with st.spinner("🔍 Fetching your movie matches..."):
        titles, details = get_recommendations(selected_movie)
        st.subheader("✨ Top 10 Recommended Movies for You")

    cols = st.columns(5)
    for i in range(5):
        poster, tmdb_link, tmdb_rating, imdb_rating, year, overview, trailer = details[i]
        with cols[i]:
            st.markdown(f"""<div class='movie-card'>
                <div class='poster-wrapper'>
                    <a href='{tmdb_link}' target='_blank'>
                        <img src='{poster}' style='width:100%; height:450px; object-fit: cover; border-radius:8px;'>
                        <div class='overlay'>{year} – {overview}</div>
                    </a>
                </div>
                <div class='movie-caption'>{titles[i]}</div>
                <div class='rating'>⭐ TMDB: {tmdb_rating} | IMDb: {imdb_rating}</div>
                <div class='trailer-button'><a href='{trailer}' target='_blank'><button>▶ Watch Trailer</button></a></div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    cols2 = st.columns(5)
    for i in range(5, 10):
        poster, tmdb_link, tmdb_rating, imdb_rating, year, overview, trailer = details[i]
        with cols2[i - 5]:
            st.markdown(f"""<div class='movie-card'>
                <div class='poster-wrapper'>
                    <a href='{tmdb_link}' target='_blank'>
                        <img src='{poster}' style='width:100%; height:450px; object-fit: cover; border-radius:8px;'>
                        <div class='overlay'>{year} – {overview}</div>
                    </a>
                </div>
                <div class='movie-caption'>{titles[i]}</div>
                <div class='rating'>⭐ TMDB: {tmdb_rating} | IMDb: {imdb_rating}</div>
                <div class='trailer-button'><a href='{trailer}' target='_blank'><button>▶ Watch Trailer</button></a></div>
            </div>""", unsafe_allow_html=True)

# --------------------- Footer ---------------------
st.markdown('<div class="footer">🍿 ReelMatch & Chill – Your next binge starts here. © 2025</div>', unsafe_allow_html=True)