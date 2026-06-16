import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getToken } from '../api/authApi';
import './Home.css';

const MacrosCalculatorIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 7.001l.266-.15a6.002 6.002 0 005.467-9.401L18 4.002l-3.268 5.94M3 6l3 1m0 0l3.001-5.001L12 9" />
    </svg>
);

const MealPlannerIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
    </svg>
);

const ImageRecognitionIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
);

const ChatbotIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
);

const FEATURES = [
    {
        Icon: MacrosCalculatorIcon,
        title: 'Macros Calculator',
        desc: 'Get your personalized daily calories and macronutrient targets from your body metrics and goals.',
        to: '/macros-calculator',
        cta: 'Calculate now',
    },
    {
        Icon: MealPlannerIcon,
        title: 'Meal Planner',
        desc: 'Generate a full day of meals that hits your targets, with one-tap food swaps and regeneration.',
        to: '/meal-planner',
        cta: 'Plan your day',
    },
    {
        Icon: ImageRecognitionIcon,
        title: 'Image Recognition',
        desc: 'Snap a photo of your meal and get instant nutritional insight powered by computer vision.',
        to: '/image-recognition',
        cta: 'Scan your food',
    },
    {
        Icon: ChatbotIcon,
        title: 'AI Chatbot',
        desc: 'Ask anything about nutrition and get instant, friendly answers from our AI assistant.',
        to: '/chatbot',
        cta: 'Ask a question',
    },
];

const STEPS = [
    { n: 1, title: 'Build your profile', desc: 'Tell us your age, body metrics, activity, and goal — it takes a minute.' },
    { n: 2, title: 'Get your numbers', desc: 'We calculate your daily calories and macro split tailored to your goal.' },
    { n: 3, title: 'Plan, scan & chat', desc: 'Generate meal plans, scan food with your camera, and ask the AI anything.' },
];

const Home = () => {
    const [loggedIn, setLoggedIn] = useState(!!getToken());

    useEffect(() => {
        const onLogin = () => setLoggedIn(true);
        window.addEventListener('login', onLogin);
        setLoggedIn(!!getToken());
        return () => window.removeEventListener('login', onLogin);
    }, []);

    const scrollToFeatures = (e) => {
        e.preventDefault();
        document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
    };

    return (
        <div className="home-page">
            {/* ---- Hero (immersive, sits on the global green background) ---- */}
            <header className="hero">
                <div className="hero-inner">
                    <span className="hero-badge">AI-Powered Nutrition</span>
                    <h1>Eat smarter with <span>NutriTech</span></h1>
                    <p>
                        Your all-in-one partner to calculate macros, plan meals,
                        scan food, and get instant AI guidance — built around your goals.
                    </p>
                    <div className="hero-cta">
                        {!loggedIn && (
                            <Link to="/register" className="btn btn-primary">Get Started — it's free</Link>
                        )}
                        <a href="#features" onClick={scrollToFeatures} className="btn btn-ghost">Explore features</a>
                    </div>
                    <div className="hero-stats">
                        <div className="stat"><strong>250+</strong><span>curated foods</span></div>
                        <div className="stat"><strong>9</strong><span>goal profiles</span></div>
                        <div className="stat"><strong>AI</strong><span>chat &amp; vision</span></div>
                    </div>
                </div>
            </header>

            {/* ---- How it works (solid light) ---- */}
            <section className="how section-light">
                <div className="section-head">
                    <h2>How it works</h2>
                    <p>From zero to a personalized plan in three simple steps.</p>
                </div>
                <div className="steps">
                    {STEPS.map((s) => (
                        <div key={s.n} className="step">
                            <span className="step-num">{s.n}</span>
                            <h3>{s.title}</h3>
                            <p>{s.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* ---- Features (solid light) ---- */}
            <section id="features" className="features section-muted">
                <div className="section-head">
                    <h2>Everything you need</h2>
                    <p>Four tools that work together to keep you on track.</p>
                </div>
                <div className="features-grid">
                    {FEATURES.map(({ Icon, title, desc, to, cta }) => (
                        <div key={title} className="feature-card">
                            <div className="feature-icon"><Icon /></div>
                            <h3>{title}</h3>
                            <p className="feature-desc">{desc}</p>
                            <Link to={to} className="feature-link">{cta} →</Link>
                        </div>
                    ))}
                </div>
            </section>

            {/* ---- Closing CTA band (immersive, glass on green) — sign-up prompt, hidden when logged in ---- */}
            {!loggedIn && (
                <section className="cta-band">
                    <div className="cta-card">
                        <h2>Ready to reach your goals?</h2>
                        <p>Create your free account and get your first personalized plan in minutes.</p>
                        <Link to="/register" className="btn btn-primary">Get Started</Link>
                    </div>
                </section>
            )}

        </div>
    );
};

export default Home;
