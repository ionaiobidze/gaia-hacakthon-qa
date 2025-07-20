import React from 'react';
import { Link } from 'react-router-dom';

function MovieCard({ movie, isFavorite, toggleFavorite }) {
  return (
    <div id={`movie-card-${movie.id}`} className="film-card"> {/* Using new "film-card" class for styling */}
      <Link id={`movie-image-link-${movie.id}`} to={`/movies/${movie.id}`}>
        <div className="image-wrapper">
          <img src={movie.image} alt={movie.title} />
          <div className="film-card-overlay">
            <button
              id={`watchlist-toggle-${movie.id}`}
              className="watchlist-button"
              onClick={(e) => {
                e.preventDefault(); // Prevent navigation when clicking the button
                toggleFavorite(movie.id);
              }}
              aria-label={isFavorite ? 'Remove from watchlist' : 'Add to watchlist'}
            >
              {isFavorite ? "✓" : "+"}
            </button>
          </div>
        </div>
      </Link>
      <div className="film-card-content">
        <Link id={`movie-title-link-${movie.id}`} to={`/movies/${movie.id}`}>
          <h3 data-testid={`movie-title-${movie.id}`}>{movie.title}</h3>
        </Link>
        <div className="film-meta">
          <span data-testid={`movie-category-${movie.id}`}>{movie.genre}</span> • <span data-testid={`movie-year-${movie.id}`}>{movie.year}</span>
        </div>
      </div>
    </div>
  );
}

export default MovieCard;