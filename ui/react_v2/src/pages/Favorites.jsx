import React from 'react';
import MovieCard from '../components/MovieCard';

function Favorites({ movies, favorites, toggleFavorite, sortOrder, setSortOrder }) {
  const favMovies = movies.filter(movie => favorites.includes(movie.id));

  const sortedFavMovies = [...favMovies].sort((a, b) => {
    if (sortOrder === 'title') {
      return a.title.localeCompare(b.title);
    }
    if (sortOrder === 'year') {
      return b.year - a.year;
    }
    return 0;
  });

  return (
    <div id="favorites-page-container">
      <div id="sort-controls-favorites" className="sort-controls">
        <span>Arrange by:</span>
        <button id="sort-by-title-button-fav" onClick={() => setSortOrder('title')} className={sortOrder === 'title' ? 'active' : ''}>Alphabetical</button>
        <button id="sort-by-year-button-fav" onClick={() => setSortOrder('year')} className={sortOrder === 'year' ? 'active' : ''}>Release Date</button>
        {sortOrder && <button id="clear-sort-button-fav" onClick={() => setSortOrder('')}>Reset</button>}
      </div>
      <div id="movie-list-container-fav" className="film-list"> {/* Using new "film-list" class */}
        {sortedFavMovies.length > 0 ? (
          sortedFavMovies.map(movie => (
            <MovieCard
              key={movie.id}
              movie={movie}
              isFavorite={true}
              toggleFavorite={toggleFavorite}
            />
          ))
        ) : (
          <p id="no-favorites-message">Your watchlist is empty. Add some films!</p>
        )}
      </div>
    </div>
  );
}

export default Favorites;