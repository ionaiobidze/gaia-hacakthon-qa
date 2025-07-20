import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function MovieDetails({ movies }) {
  const { movieId } = useParams();
  const navigate = useNavigate();
  const movie = movies.find((m) => m.id === movieId);

  if (!movie) return <p>Movie not found</p>;

  return (
    <div className="details-card">
      <button className="back-button" onClick={() => navigate(-1)}>← Back</button>

      <div className="details-content">
        <div className="details-image-wrapper">
          <img src={movie.image} alt={movie.title} />
        </div>

        <div className="details-text">
          <h1>{movie.title}</h1>
          <div className="sub-info">
            <span>{movie.year}</span> &nbsp; &nbsp; <span>{movie.genre}</span>
          </div>

          <h3>Plot Summary</h3>
          <p>{movie.description}</p>

          <div className="info-grid">
            <div>
              <h5>RELEASE YEAR</h5>
              <p><strong>{movie.year}</strong></p>
            </div>
            <div>
              <h5>GENRE</h5>
              <p><strong>{movie.genre}</strong></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MovieDetails;

