import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api, writeApi } from '../../api';
import { useSession } from '../../session';

export default function PostReview() {
  const { id } = useParams();
  const navigate = useNavigate();
  const session = useSession();
  const [dealer, setDealer] = useState(null);
  const [cars, setCars] = useState([]);
  const [make, setMake] = useState('');
  const [model, setModel] = useState('');
  const [purchase, setPurchase] = useState(true);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    let active = true;
    Promise.all([api(`dealer/${id}`), api('get_cars')]).then(([details, inventory]) => {
      if (active) { setDealer(Array.isArray(details.dealer) ? details.dealer[0] : details.dealer); setCars(inventory.CarModels); }
    }).catch(err => { if (active) setError(err.message); });
    return () => { active = false; };
  }, [id]);
  async function submit(event) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setBusy(true); setError('');
    try {
      await writeApi('add_review', {
        dealership: Number(id), review: data.get('review'), purchase,
        ...(purchase ? { purchase_date: data.get('purchase_date'), car_make: make, car_model: model, car_year: Number(data.get('car_year')) } : {}),
      });
      navigate(`/dealer/${id}`, { state: { reviewPosted: true } });
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  if (!session.loading && !session.authenticated) return <section className="form-page"><h1>Share your experience</h1><p>Please <Link to="/login">log in</Link> to write a review.</p></section>;
  return <section className="form-page review-form"><Link className="back-link" to={`/dealer/${id}`}>← Back to dealership</Link><p className="eyebrow">YOUR EXPERIENCE MATTERS</p><h1>Post a review</h1><p>{dealer?.full_name || 'Loading dealership…'}</p>
    <form onSubmit={submit} className="panel form-stack">
      {error && <p className="notice error" role="alert">{error}</p>}
      <label htmlFor="review">Your review<textarea id="review" name="review" rows="4" maxLength="5000" placeholder="Tell other drivers about your experience…" required /></label>
      <label className="checkbox-label" htmlFor="purchase"><input id="purchase" type="checkbox" checked={purchase} onChange={event => setPurchase(event.target.checked)} />I purchased a vehicle from this dealership</label>
      {purchase && <><div className="form-row"><label htmlFor="car-make">Car Make<select id="car-make" value={make} onChange={event => { setMake(event.target.value); setModel(''); }} required><option value="">Choose a make</option>{[...new Set(cars.map(car => car.CarMake))].sort().map(name => <option value={name} key={name}>{name}</option>)}</select></label>
        <label htmlFor="car-model">Car Model<select id="car-model" value={model} onChange={event => setModel(event.target.value)} required><option value="">Choose a model</option>{[...new Set(cars.filter(car => car.CarMake === make).map(car => car.CarModel))].sort().map(name => <option value={name} key={name}>{name}</option>)}</select></label></div>
        <div className="form-row"><label htmlFor="car-year">Car Year<input id="car-year" name="car_year" type="number" min="2015" max={new Date().getFullYear() + 1} required /></label><label htmlFor="purchase-date">Purchase Date<input id="purchase-date" name="purchase_date" type="date" max={new Date().toISOString().slice(0, 10)} required /></label></div></>}
      <div className="card-actions"><button className="button" type="submit" disabled={busy || !dealer}>{busy ? 'Posting review…' : 'Post Review'}</button><Link className="button secondary" to={`/dealer/${id}`}>Cancel</Link></div>
    </form>
  </section>;
}
