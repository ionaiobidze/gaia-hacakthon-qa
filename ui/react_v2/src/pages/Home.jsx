import React from 'react';
import MovieCard from '../components/MovieCard';

function Home({ movies, search, favorites, toggleFavorite, sortOrder, setSortOrder }) {
  const filtered = movies.filter(movie =>
    movie.title.toLowerCase().includes(search.toLowerCase()) ||
    movie.genre.toLowerCase().includes(search.toLowerCase())
  );

  const sortedMovies = [...filtered].sort((a, b) => {
    if (sortOrder === 'title') {
      return a.title.localeCompare(b.title);
    }
    if (sortOrder === 'year') {
      return b.year - a.year;
    }
    return 0;
  });

  return (
    <div id="home-page-container">
      <div id="sort-controls" className="sort-controls">
        <span>Arrange by:</span>
        <button id="sort-by-title-button" onClick={() => setSortOrder('title')} className={sortOrder === 'title' ? 'active' : ''}>Alphabetical</button>
        <button id="sort-by-year-button" onClick={() => setSortOrder('year')} className={sortOrder === 'year' ? 'active' : ''}>Release Date</button>
        {sortOrder && <button id="clear-sort-button" onClick={() => setSortOrder('')}>Reset</button>}
      </div>
      <div id="movie-list-container" className="film-list"> {/* Using new "film-list" class for styling */}
        {sortedMovies.map(movie => (
          <MovieCard
            key={movie.id}
            movie={movie}
            isFavorite={favorites.includes(movie.id)}
            toggleFavorite={toggleFavorite}
          />
        ))}
      </div>
    </div>
  );
}

export default Home;