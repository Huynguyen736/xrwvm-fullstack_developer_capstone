import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../../api';
import { useSession } from '../../session';

export default function Dealers() {
  const session = useSession();
  const [params, setParams] = useSearchParams();
  const state = params.get('state') || 'All';
  const [states, setStates] = useState([]);
  const [dealers, setDealers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  useEffect(() => {
    api('get_dealers/').then(data => setStates([...new Set(data.dealers.map(dealer => dealer.state))].sort())).catch(err => setError(err.message));
  }, []);
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError('');
    api(state === 'All' ? 'get_dealers/' : `get_dealers/${encodeURIComponent(state)}`)
      .then(data => { if (active) setDealers(data.dealers); })
      .catch(err => { if (active) setError(err.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [state]);
  return <>
    <section className="hero">
      <div><p className="eyebrow">A BETTER WAY TO FIND YOUR NEXT DEALER</p><h1>Great cars start<br />with trusted dealers.</h1><p>Explore dealerships, read honest experiences, and share your own. Your next journey starts here.</p><a className="button light" href="#dealers">Explore dealerships <span aria-hidden="true">↗</span></a></div>
      <img src="/static/cars.jpeg" alt="Cars available at a dealership" />
    </section>
    <section className="page" id="dealers">
      <div className="section-heading"><div><p className="eyebrow">FIND YOUR LOCAL EXPERT</p><h2>Our dealerships</h2><p>{loading ? 'Finding dealerships…' : `${dealers.length} dealership${dealers.length === 1 ? '' : 's'}${state === 'All' ? ' across the United States' : ` in ${state}`}`}</p></div>
        <label className="state-filter" htmlFor="state-filter">Filter by state<select id="state-filter" value={state} onChange={event => setParams(event.target.value === 'All' ? {} : { state: event.target.value })}><option value="All">All states</option>{states.map(value => <option key={value} value={value}>{value}</option>)}</select></label>
      </div>
      {error && <p className="notice error" role="alert">{error}</p>}
      {loading ? <p role="status">Loading dealerships…</p> : <div className="dealer-grid">{dealers.map(dealer => <article className="dealer-card" key={dealer.id}>
        <div className="dealer-card-top"><span className="location-tag">{dealer.state}</span><span className="dealer-number">#{String(dealer.id).padStart(3, '0')}</span></div>
        <h3><Link to={`/dealer/${dealer.id}`}>{dealer.full_name}</Link></h3>
        <p className="dealer-city">{dealer.city}, {dealer.state}</p><p>{dealer.address}<br />{dealer.city}, {dealer.state} {dealer.zip}</p>
        <div className="card-actions"><Link className="button secondary" to={`/dealer/${dealer.id}`}>View Details</Link>{session.authenticated && <Link className="button" to={`/postreview/${dealer.id}`}>Review Dealer</Link>}</div>
      </article>)}</div>}
      {!loading && !error && dealers.length === 0 && <p>No dealerships were found in this state.</p>}
    </section>
  </>;
}
