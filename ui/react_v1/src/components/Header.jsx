import React from 'react';
import { NavLink } from 'react-router-dom';

function Header({ search, setSearch }) {
  return (
    <header>
      <div className="header-title">MovieApp</div>
      <nav>
        <NavLink to="/" className={({ isActive }) => isActive ? "active" : ""}>All Movies</NavLink>
        <NavLink to="/favorites" className={({ isActive }) => isActive ? "active" : ""}>Favorites</NavLink>
      </nav>
      <input
        type="text"
        placeholder="Search movies by title or genre..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />
    </header>
  );
}

export default Header;

