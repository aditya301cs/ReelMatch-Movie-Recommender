import streamlit as st
import pickle
import os
import requests
import concurrent.futures
import gdown
from streamlit.components.v1 import html

# Page config
st.set_page_config(
    page_title="ReelMatch: Movie Recommender",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Constants
DATA_FILE = 'movie_data.pkl'
DATA_URL = 'https://drive.google.com/uc?id=1vR9uPEw8cQGx23_uGOCfN0BxGVGGttYY'
TMDB_API_KEY = "3b3778403271ce6f2c2b9377fa3dc77b"
OMDB_API_KEY = "4a3b711b"

# CSS Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
        color: #ffffff;
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 100%);
    }

    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #e50914 0%, #ff6b6b 50%, #e50914 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 0 0 30px rgba(229, 9, 20, 0.5);
    }

    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #cccccc;
        margin-bottom: 2rem;
        font-weight: 300;
    }

    .glow-bar {
        height: 4px;
        background: linear-gradient(90deg, transparent, #e50914, #ff6b6b, #e50914, transparent);
        margin: 0 auto 3rem auto;
        width: 60%;
        border-radius: 2px;
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 0.7; transform: scaleY(1); }
        50% { opacity: 1; transform: scaleY(1.5); }
    }

    .carousel-container {
        margin: 2rem 0;
        overflow: hidden;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.7);
    }

    .section-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #e50914;
        margin: 2rem 0 1rem 0;
        text-align: center;
    }

    .movie-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }

    .movie-card {
        background: linear-gradient(145deg, #1f1f1f, #2a2a2a);
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.8);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 1px solid rgba(229, 9, 20, 0.1);
        position: relative;
        overflow: hidden;
    }

    .movie-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #e50914, #ff6b6b, #e50914);
        transform: scaleX(0);
        transition: transform 0.4s ease;
    }

    .movie-card:hover::before {
        transform: scaleX(1);
    }

    .movie-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 40px rgba(229, 9, 20, 0.3);
        border-color: rgba(229, 9, 20, 0.5);
    }

    .poster-container {
        position: relative;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 1rem;
    }

    .poster-image {
        width: 100%;
        height: 320px;
        object-fit: cover;
        transition: transform 0.4s ease;
    }

    .movie-card:hover .poster-image {
        transform: scale(1.05);
    }

    .poster-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(transparent, rgba(0, 0, 0, 0.9));
        color: white;
        padding: 1.5rem 1rem 1rem 1rem;
        transform: translateY(100%);
        transition: transform 0.4s ease;
        font-size: 0.85rem;
        line-height: 1.4;
    }

    .poster-container:hover .poster-overlay {
        transform: translateY(0);
    }

    .movie-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.5rem;
        text-align: center;
        line-height: 1.3;
    }

    .movie-ratings {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }

    .rating-item {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        color: #ffd700;
        font-weight: 500;
    }

    .action-buttons {
        display: flex;
        gap: 0.5rem;
    }

    .btn-trailer, .btn-info {
        flex: 1;
        padding: 0.7rem;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        text-decoration: none;
        text-align: center;
        transition: all 0.3s ease;
        font-size: 0.9rem;
    }

    .btn-trailer {
        background: linear-gradient(135deg, #e50914, #ff1744);
        color: white;
    }

    .btn-trailer:hover {
        background: linear-gradient(135deg, #ff1744, #e50914);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(229, 9, 20, 0.4);
    }

    .btn-info {
        background: linear-gradient(135deg, #333333, #555555);
        color: white;
    }

    .btn-info:hover {
        background: linear-gradient(135deg, #555555, #333333);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }

    .loading-spinner {
        text-align: center;
        padding: 3rem;
        font-size: 1.2rem;
        color: #e50914;
    }

    .error-message {
        background: linear-gradient(135deg, #ff4757, #ff3742);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }

    .success-message {
        background: linear-gradient(135deg, #2ed573, #1dd1a1);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }

    .footer {
        text-align: center;
        padding: 3rem 0 1rem 0;
        color: #666666;
        font-size: 0.9rem;
        border-top: 1px solid #333333;
        margin-top: 3rem;
    }

    .stSelectbox > div > div > select {
        background-color: #2a2a2a;
        color: white;
        border: 1px solid #e50914;
        border-radius: 10px;
        padding: 0.5rem;
        font-size: 1rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #e50914, #ff1744);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #ff1744, #e50914);
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(229, 9, 20, 0.4);
    }
    </style>
""", unsafe_allow_html=True)


def download_data_file():
    """Download the movie data file if it doesn't exist"""
    if os.path.exists(DATA_FILE):
        return True

    st.info("🔄 Downloading movie database... This may take a moment.")

    try:
        with st.spinner("Downloading movie data..."):
            gdown.download(DATA_URL, DATA_FILE, quiet=False)
        st.success("✅ Movie database downloaded successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Failed to download movie database: {str(e)}")
        st.info("Please check your internet connection or contact support.")
        return False


@st.cache_data(show_spinner=False, ttl=3600)
def load_movie_data():
    """Load movie data with error handling"""
    try:
        if not download_data_file():
            return None, None

        with open(DATA_FILE, 'rb') as f:
            movies, cosine_sim = pickle.load(f)

        return movies, cosine_sim
    except Exception as e:
        st.error(f"❌ Error loading movie data: {str(e)}")
        return None, None


@st.cache_data(show_spinner=False, ttl=1800)
def fetch_movie_details(movie_id):
    """Fetch detailed movie information from APIs"""
    default_response = (
        "https://via.placeholder.com/300x450?text=No+Poster",
        "#", "N/A", "N/A", "N/A",
        "Movie information unavailable.", "#"
    )

    try:
        # Get basic movie info from TMDB
        tmdb_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {"api_key": TMDB_API_KEY, "language": "en-US"}

        response = requests.get(tmdb_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Extract movie details
        poster_path = data.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else default_response[0]

        movie_url = f"https://www.themoviedb.org/movie/{movie_id}"
        tmdb_rating = round(data.get("vote_average", 0), 1)
        release_date = data.get("release_date", "")
        year = release_date[:4] if release_date else "N/A"
        overview = data.get("overview", "No description available.")
        imdb_id = data.get("imdb_id")

        # Get IMDb rating
        imdb_rating = "N/A"
        if imdb_id:
            try:
                omdb_url = f"http://www.omdbapi.com/"
                omdb_params = {"i": imdb_id, "apikey": OMDB_API_KEY}
                omdb_response = requests.get(omdb_url, params=omdb_params, timeout=3)
                omdb_data = omdb_response.json()
                imdb_rating = omdb_data.get("imdbRating", "N/A")
            except:
                pass

        # Get trailer URL
        trailer_url = "#"
        try:
            videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
            videos_response = requests.get(videos_url, params={"api_key": TMDB_API_KEY}, timeout=3)
            videos_data = videos_response.json()

            for video in videos_data.get("results", []):
                if video.get("site") == "YouTube" and video.get("type") == "Trailer":
                    trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
                    break
        except:
            pass

        return poster_url, movie_url, tmdb_rating, imdb_rating, year, overview, trailer_url

    except Exception as e:
        return default_response


@st.cache_data(show_spinner=False)
def get_movie_recommendations(title, movies, cosine_sim):
    """Get movie recommendations based on similarity"""
    try:
        movie_index = movies[movies['title'] == title].index[0]
    except:
        return [], []

    # Get similarity scores
    similarity_scores = list(enumerate(cosine_sim[movie_index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    # Get top 10 similar movies (excluding the input movie itself)
    top_movies = similarity_scores[1:11]
    movie_indices = [i[0] for i in top_movies]

    # Get movie titles and IDs
    recommended_titles = movies['title'].iloc[movie_indices].values
    recommended_ids = movies['movie_id'].iloc[movie_indices].values

    # Fetch detailed information for all recommended movies
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        movie_details = list(executor.map(fetch_movie_details, recommended_ids))

    return recommended_titles, movie_details


def create_movie_carousel():
    """Create an animated movie poster carousel"""
    popular_movie_ids = [
        278, 238, 155, 680, 13, 807, 120, 122, 550, 89,
        389, 424, 11, 27205, 46738, 872585, 11036, 359724,
        980489, 76, 9919, 244786, 603, 637, 324857
    ]

    with st.spinner("Loading movie carousel..."):
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            poster_urls = [fetch_movie_details(movie_id)[0] for movie_id in popular_movie_ids[:15]]

    carousel_html = f"""
    <div class="carousel-container">
        <div style="
            display: flex; 
            gap: 15px; 
            width: max-content; 
            animation: scroll 50s linear infinite;
            padding: 20px 0;
        ">
            {''.join([
        f'<img src="{url}" style="width: 160px; height: 240px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.5);">'
        for url in poster_urls
    ])}
        </div>
    </div>

    <style>
    @keyframes scroll {{
        0% {{ transform: translateX(100vw); }}
        100% {{ transform: translateX(-100%); }}
    }}
    </style>
    """

    html(carousel_html, height=280)


def display_movie_grid(titles, details):
    """Display movies in a responsive grid layout"""
    st.markdown('<div class="movie-grid">', unsafe_allow_html=True)

    for i in range(0, len(titles), 5):
        cols = st.columns(5)
        for j, col in enumerate(cols):
            if i + j < len(titles):
                idx = i + j
                poster_url, movie_url, tmdb_rating, imdb_rating, year, overview, trailer_url = details[idx]

                with col:
                    st.markdown(f"""
                    <div class="movie-card">
                        <div class="poster-container">
                            <img src="{poster_url}" class="poster-image" alt="{titles[idx]}">
                            <div class="poster-overlay">
                                <strong>{year}</strong><br>
                                {overview[:100]}{'...' if len(overview) > 100 else ''}
                            </div>
                        </div>

                        <div class="movie-title">{titles[idx]}</div>

                        <div class="movie-ratings">
                            <div class="rating-item">
                                <span>⭐</span>
                                <span>{tmdb_rating}</span>
                            </div>
                            <div class="rating-item">
                                <span>🎬</span>
                                <span>{imdb_rating}</span>
                            </div>
                        </div>

                        <div class="action-buttons">
                            <a href="{trailer_url}" target="_blank" class="btn-trailer">
                                ▶ Trailer
                            </a>
                            <a href="{movie_url}" target="_blank" class="btn-info">
                                ℹ Info
                            </a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def main():
    """Main application function"""
    # Header
    st.markdown('<h1 class="main-header">🍿 ReelMatch</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Discover your next favorite movie with AI-powered recommendations</p>',
                unsafe_allow_html=True)
    st.markdown('<div class="glow-bar"></div>', unsafe_allow_html=True)

    # Load movie data
    movies, cosine_sim = load_movie_data()

    if movies is None or cosine_sim is None:
        st.error("❌ Unable to load movie database. Please refresh the page or try again later.")
        st.stop()

    # Movie carousel
    st.markdown('<h2 class="section-title">🎬 Featured Movies</h2>', unsafe_allow_html=True)
    create_movie_carousel()

    # Recommendation section
    st.markdown('<h2 class="section-title">🔍 Get Personalized Recommendations</h2>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_movie = st.selectbox(
            "Choose a movie you enjoyed:",
            options=sorted(movies['title'].values),
            index=0,
            help="Select a movie you liked to get similar recommendations"
        )

        recommend_button = st.button("🚀 Get Recommendations", use_container_width=True)

    # Display recommendations
    if recommend_button:
        with st.spinner("🎯 Finding your perfect movie matches..."):
            recommended_titles, movie_details = get_movie_recommendations(
                selected_movie, movies, cosine_sim
            )

        if recommended_titles:
            st.markdown(f'<h2 class="section-title">✨ Movies Similar to "{selected_movie}"</h2>',
                        unsafe_allow_html=True)
            display_movie_grid(recommended_titles, movie_details)
        else:
            st.error("❌ Sorry, we couldn't find recommendations for that movie. Please try another selection.")

    # Footer
    st.markdown("""
    <div class="footer">
        <p>🍿 <strong>ReelMatch</strong> - Your AI-powered movie discovery companion</p>
        <p>Powered by TMDB & IMDb | © 2025 | Made with ❤️ and Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()