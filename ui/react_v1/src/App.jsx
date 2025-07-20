import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import Favorites from './pages/Favorites';
import MovieDetails from './pages/MovieDetails';
import moviesData from './data';

function App() {
  const [favorites, setFavorites] = useState([]);
  const [search, setSearch] = useState("");
  const [sortOrder, setSortOrder] = useState(""); // Default: no sort

  const toggleFavorite = (id) => {
    setFavorites((prev) =>
      prev.includes(id) ? prev.filter(fid => fid !== id) : [...prev, id]
    );
  };

  return (
    <>
      <Header search={search} setSearch={setSearch} />
      <main>
        <Routes>
          <Route
            path="/"
            element={
              <Home
                movies={moviesData}
                search={search}
                favorites={favorites}
                toggleFavorite={toggleFavorite}
                sortOrder={sortOrder}
                setSortOrder={setSortOrder}
              />
            }
          />
          <Route
            path="/favorites"
            element={
              <Favorites
                movies={moviesData}
                favorites={favorites}
                toggleFavorite={toggleFavorite}
                sortOrder={sortOrder}
                setSortOrder={setSortOrder}
              />
            }
          />
          <Route path="/movies/:movieId" element={<MovieDetails movies={moviesData} />} />
        </Routes>
      </main>
    </>
  );
}

export default App;