import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { writeApi } from '../../api';
import { useSession } from '../../session';

export default function Register() {
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const session = useSession();
  const navigate = useNavigate();
  async function submit(event) {
    event.preventDefault();
    setBusy(true); setError('');
    const form = new FormData(event.currentTarget);
    try {
      await writeApi('register', Object.fromEntries(form.entries()));
      await session.refreshSession();
      navigate('/dealers');
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  return <section className="form-page"><p className="eyebrow">JOIN THE CONVERSATION</p><h1>Create your account</h1><p>Help other drivers find a dealership they can trust.</p><form onSubmit={submit} className="panel form-stack">
    {error && <p className="notice error" role="alert">{error}</p>}
    <label htmlFor="register-user">Username<input id="register-user" name="userName" autoComplete="username" maxLength="150" required /></label>
    <div className="form-row"><label htmlFor="first-name">First Name<input id="first-name" name="firstName" autoComplete="given-name" required /></label><label htmlFor="last-name">Last Name<input id="last-name" name="lastName" autoComplete="family-name" required /></label></div>
    <label htmlFor="email">Email<input id="email" name="email" type="email" autoComplete="email" required /></label>
    <label htmlFor="register-password">Password<input id="register-password" name="password" type="password" minLength="8" autoComplete="new-password" aria-describedby="password-hint" required /></label>
    <small id="password-hint">Use at least 8 characters and avoid common passwords.</small>
    <button className="button" type="submit" disabled={busy}>{busy ? 'Creating account…' : 'Register'}</button>
    <p>Already have an account? <Link to="/login">Log in</Link></p>
  </form></section>;
}
