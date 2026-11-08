import React, { useState, useEffect } from 'react';
import { Link, useParams, useLocation } from 'react-router-dom';
import { api } from '../../api';
import { useSession } from '../../session';

export default function Dealer() {
  const { id } = useParams();
  const location = useLocation();
  const session = useSession();
  const [dealer, setDealer] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    setDealer(null); setError('');
    Promise.all([api(`dealer/${id}`), api(`reviews/dealer/${id}`)])
      .then(([details, feedback]) => { if (active) { setDealer(Array.isArray(details.dealer) ? details.dealer[0] : details.dealer); setReviews(feedback.reviews); } })
      .catch(err => { if (active) setError(err.message); });
    return () => { active = false; };
  }, [id]);
  return <section className="page">
    <Link className="back-link" to="/dealers">← All dealerships</Link>
    {error ? <p className="notice error" role="alert">{error}</p> : !dealer ? <p role="status">Loading dealership…</p> : <>
      {location.state?.reviewPosted && <p className="notice success" role="status">Your review has been posted. Thank you for sharing your experience.</p>}
      <div className="dealer-detail panel"><div><span className="location-tag">{dealer.state}</span><h1>{dealer.full_name}</h1><p>{dealer.address}<br />{dealer.city}, {dealer.state} {dealer.zip}</p></div><div>{session.authenticated ? <Link className="button" to={`/postreview/${id}`}>Review Dealer</Link> : <Link className="button" to="/login">Log in to write a review</Link>}</div></div>
      <div className="section-heading"><div><p className="eyebrow">REAL EXPERIENCES</p><h2>Customer reviews</h2><p>{reviews.length} review{reviews.length === 1 ? '' : 's'}</p></div></div>
      <div className="review-grid">{reviews.map(review => <article className="panel review-card" key={review.id}>
        <span className={`sentiment ${review.sentiment || 'neutral'}`}>{review.sentiment || 'neutral'}</span><blockquote>{review.review}</blockquote>
        <strong>{review.name}</strong>{review.purchase && <p className="purchase-details">{review.car_year} {review.car_make} {review.car_model}{review.purchase_date ? ` · Purchased ${review.purchase_date}` : ''}</p>}
      </article>)}</div>
      {reviews.length === 0 && <p className="panel">No reviews yet. Be the first to share your experience.</p>}
    </>}
  </section>;
}
