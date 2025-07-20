import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function MovieDetails({ movies }) {
  const { movieId } = useParams();
  const navigate = useNavigate();
  const movie = movies.find((m) => m.id === movieId);

  if (!movie) {
    return <p id="movie-not-found-message">Film not found.</p>;
  }

  return (
    <div id={`movie-details-card-${movie.id}`} className="details-card">
      <button id="back-button" className="back-button" onClick={() => navigate(-1)}>← Return</button>

      <div className="details-content">
        <div className="details-image-wrapper">
          <img src={movie.image} alt={movie.title} />
        </div>

        <div className="details-text">
          <h1 id="movie-details-title">{movie.title}</h1>
          <div className="sub-info">
            <span id="movie-details-year">{movie.year}</span>   •   <span id="movie-details-category">{movie.genre}</span>
          </div>

          <h3>Synopsis</h3>
          <p id="movie-details-description">{movie.description}</p>

          <div className="info-grid">
            <div>
              <h5>RELEASE DATE</h5>
              <p><strong data-testid="grid-release-year">{movie.year}</strong></p>
            </div>
            <div>
              <h5>CATEGORY</h5>
              <p><strong data-testid="grid-category">{movie.genre}</strong></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MovieDetails;