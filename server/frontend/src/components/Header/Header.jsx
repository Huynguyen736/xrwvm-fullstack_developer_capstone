import React, { useState } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { useSession } from '../../session';
import { writeApi } from '../../api';

export default function Header() {
  const session = useSession();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  async function logout() {
    try {
      await writeApi('logout/', {});
      await session.refreshSession();
      navigate('/');
    } catch (err) { setError(err.message); }
  }
  return <>
    <a className="skip-link" href="#main-content">Skip to content</a>
    <header className="site-header">
      <Link to="/" className="brand"><span className="brand-mark">BC</span><span>Best Cars<small>DEALERSHIP REVIEWS</small></span></Link>
      <nav aria-label="Main navigation">
        <NavLink to="/" end>Home</NavLink>
        <a href="/about">About Us</a>
        <a href="/contact">Contact Us</a>
      </nav>
      <div className="account">
        {session.authenticated ? <><span>Welcome, <strong>{session.userName}</strong></span><button className="button secondary" onClick={logout}>Log out</button></> : <><NavLink to="/login">Log in</NavLink><Link className="button" to="/register">Sign up</Link></>}
      </div>
    </header>
    {error && <p className="notice error" role="alert">{error}</p>}
  </>;
}
