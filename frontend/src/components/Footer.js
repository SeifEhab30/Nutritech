import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
    return (
        <footer className="footer">
            <div className="footer-inner">
                <Link to="/" className="footer-brand">NutriTech</Link>
                <nav className="footer-nav">
                    <Link to="/">Home</Link>
                    <Link to="/macros-calculator">Macros Calculator</Link>
                    <Link to="/meal-planner">Meal Planner</Link>
                    <Link to="/image-recognition">Image Recognition</Link>
                    <Link to="/chatbot">Chatbot</Link>
                </nav>
            </div>
            <p className="footer-copy">&copy; 2026 NutriTech. All rights reserved.</p>
        </footer>
    );
};

export default Footer;
