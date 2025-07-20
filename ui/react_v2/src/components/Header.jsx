import React from 'react';
import { NavLink } from 'react-router-dom';

function Header({ search, setSearch }) {
  return (
    <header id="main-header" className="container">
      <div id="app-title" className="header-title">FilmFinder</div>
      <nav id="main-nav">
        {/* The "to" prop for NavLink for the watchlist/favorites page should match your Route path */}
        <NavLink id="nav-link-all-films" to="/" className={({ isActive }) => isActive ? "active" : ""}>All Films</NavLink>
        <NavLink id="nav-link-watchlist" to="/favorites" className={({ isActive }) => isActive ? "active" : ""}>My Watchlist</NavLink>
      </nav>
      <input
        id="search-input"
        type="text"
        placeholder="Find by film title or category..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />
    </header>
  );
}

export default Header;