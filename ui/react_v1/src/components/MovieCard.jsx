import React from 'react';
import { Link } from 'react-router-dom';

function MovieCard({ movie, isFavorite, toggleFavorite }) {
  return (
    <div className="movie-card">
      <Link to={`/movies/${movie.id}`}>
        <div className="image-wrapper">
          <img src={movie.image} alt={movie.title} />
        </div>
      </Link>
      <div className="movie-card-content">
        <Link to={`/movies/${movie.id}`}><h3>{movie.title}</h3></Link>
        <div className="movie-meta">
          <span>{movie.genre}</span> • <span>{movie.year}</span>
        </div>
      </div>
      <button onClick={() => toggleFavorite(movie.id)}>
        {isFavorite ? "★" : "☆"}
      </button>
    </div>
  );
}

export default MovieCard;

