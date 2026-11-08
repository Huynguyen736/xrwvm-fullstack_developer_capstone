import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { writeApi } from '../../api';
import { useSession } from '../../session';

export default function LoginPanel() {
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const session = useSession();
  const navigate = useNavigate();
  async function submit(event) {
    event.preventDefault();
    setBusy(true); setError('');
    const form = new FormData(event.currentTarget);
    try {
      await writeApi('login', { userName: form.get('userName'), password: form.get('password') });
      await session.refreshSession();
      navigate('/dealers');
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  return <section className="form-page"><p className="eyebrow">YOUR NEXT JOURNEY</p><h1>Welcome back</h1><p>Log in to share your dealership experience.</p><form onSubmit={submit} className="panel form-stack">
    {error && <p className="notice error" role="alert">{error}</p>}
    <label htmlFor="login-user">Username<input id="login-user" name="userName" autoComplete="username" required /></label>
    <label htmlFor="login-password">Password<input id="login-password" name="password" type="password" autoComplete="current-password" required /></label>
    <button className="button" type="submit" disabled={busy}>{busy ? 'Logging in…' : 'Log in'}</button>
    <p>New here? <Link to="/register">Create an account</Link></p>
  </form></section>;
}
