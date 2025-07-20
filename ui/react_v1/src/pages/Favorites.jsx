import React from 'react';
import MovieCard from '../components/MovieCard';

function Favorites({ movies, favorites, toggleFavorite, sortOrder, setSortOrder }) {
  const favMovies = movies.filter(movie => favorites.includes(movie.id));

  const sortedFavMovies = [...favMovies].sort((a, b) => {
    if (sortOrder === 'title') {
      return a.title.localeCompare(b.title); // Sort by name (A-Z)
    }
    if (sortOrder === 'year') {
      return b.year - a.year; // Sort by release year (newest first)
    }
    return 0; // No sort
  });

  return (
    <div>
      <div className="sort-controls">
        <span>Sort by:</span>
        <button onClick={() => setSortOrder('title')} className={sortOrder === 'title' ? 'active' : ''}>Name</button>
        <button onClick={() => setSortOrder('year')} className={sortOrder === 'year' ? 'active' : ''}>Release Year</button>
        {sortOrder && <button onClick={() => setSortOrder('')}>Clear Sort</button>}
      </div>
      <div className="movie-list">
        {sortedFavMovies.map(movie => (
          <MovieCard
            key={movie.id}
            movie={movie}
            isFavorite={true}
            toggleFavorite={toggleFavorite}
          />
        ))}
      </div>
    </div>
  );
}

export default Favorites;