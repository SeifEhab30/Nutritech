import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import MacrosCalculator from './components/MacrosCalculator';
import MealPlanner from './components/MealPlanner';
import FoodSearch from './components/FoodSearch';
import ImageRecognition from './components/ImageRecognition';
import Chatbot from './components/Chatbot';
import Login from './components/Login';
import Register from './components/Register';
import Profile from './components/Profile';
import Home from './components/Home';
import Pricing from './components/Pricing';
import PremiumGate from './components/PremiumGate';
import Footer from './components/Footer';
import ScrollToTop from './components/ScrollToTop';
import DocumentTitle from './components/DocumentTitle';
import { getToken } from './api/authApi';
import './App.css';

// Redirect to /login when there's no token.
function RequireAuth({ children }) {
  return getToken() ? children : <Navigate to="/login" replace />;
}

function App() {
  return (
    <Router>
      <ScrollToTop />
      <DocumentTitle />
      <div className="App">
        <Navbar />
        <div className="container">
          <Routes>
            <Route path="/macros-calculator" element={<RequireAuth><MacrosCalculator /></RequireAuth>} />
            <Route path="/meal-planner" element={<RequireAuth><MealPlanner /></RequireAuth>} />
            <Route path="/food-search" element={<RequireAuth><FoodSearch /></RequireAuth>} />
            <Route path="/image-recognition" element={<RequireAuth><PremiumGate feature="Image Recognition"><ImageRecognition /></PremiumGate></RequireAuth>} />
            <Route path="/chatbot" element={<RequireAuth><PremiumGate feature="The AI Chatbot"><Chatbot /></PremiumGate></RequireAuth>} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/pricing" element={<RequireAuth><Pricing /></RequireAuth>} />
            <Route path="/profile" element={<RequireAuth><Profile /></RequireAuth>} />
            <Route path="/" element={<Home />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
