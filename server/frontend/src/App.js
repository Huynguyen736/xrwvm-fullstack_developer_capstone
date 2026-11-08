import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import LoginPanel from './components/Login/Login';
import Register from './components/Register/Register';
import Dealers from './components/Dealers/Dealers';
import Dealer from './components/Dealers/Dealer';
import PostReview from './components/Dealers/PostReview';
import Header from './components/Header/Header';
import { SessionProvider } from './session';

export default function App() {
  return <SessionProvider>
    <Header />
    <main id="main-content">
      <Routes>
        <Route path="/" element={<Dealers />} />
        <Route path="/dealers" element={<Dealers />} />
        <Route path="/login" element={<LoginPanel />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dealer/:id" element={<Dealer />} />
        <Route path="/postreview/:id" element={<PostReview />} />
        <Route path="*" element={<div className="page"><h1>Page not found</h1><Link to="/">Browse dealers</Link></div>} />
      </Routes>
    </main>
    <footer>Best Cars · Dealership reviews across the United States <span>IBM Full Stack Developer Capstone</span></footer>
  </SessionProvider>;
}
