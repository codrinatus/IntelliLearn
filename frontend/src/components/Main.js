import React from "react";
import {Link, useNavigate} from "react-router-dom";


function Main() {

    const isAdmin = localStorage.getItem('isAdmin') === 'true';
    const navigate = useNavigate();

    const handleIntroIconClick = () => {
        navigate('/account');
    };


    return (
        <div className="main">
            <div className="intro-container">
                <div className="intro-content">
                    <h1 className="intro-title">IntelliLearn</h1>
                    <p className="intro-description">Choose the subject</p>
                </div>
                <div className="intro-icon" onClick={handleIntroIconClick} style={{ cursor: 'pointer' }}>
                    <i className="bi-person"></i>
                </div>
            </div>

            <div className="level-boxes">
                <div className="level-container">
                    <div className="level-content">
                        <h2 className="level-name">Data Structures</h2>
                    </div>
                    <Link className="level-link" to="/quiz/SD">
                        <span>Start</span> <i className="bi bi-arrow-right"></i>
                    </Link>
                </div>
                <div className="level-container">
                    <div className="level-content">
                        <h2 className="level-name">Machine Learning</h2>
                    </div>
                    <Link className="level-link" to="/quiz/ML">
                        <span>Start</span> <i className="bi bi-arrow-right"></i>
                    </Link>
                </div>
                <div className="level-container">
                    <div className="level-content">
                        <h2 className="level-name">Cloud Computing</h2>
                    </div>
                    <Link className="level-link" to="/quiz/CC">
                        <span>Start</span> <i className="bi bi-arrow-right"></i>
                    </Link>
                </div>
                <div className="level-container">
                    <div className="level-content">
                        <h2 className="level-name">Object Oriented Pr.</h2>
                    </div>
                    <Link className="level-link" to="/quiz/OOP">
                        <span>Start</span> <i className="bi bi-arrow-right"></i>
                    </Link>
                </div>
                <div className="level-container">
                    <div className="level-content">
                        <h2 className="level-name">ACSO</h2>

                    </div>
                    <Link className="level-link" to="/quiz/ACSO">
                        <span>Start</span> <i className="bi bi-arrow-right"></i>
                    </Link>
                </div>
                <div className="level-container">
                    <div className="level-content">
                        <h2 className="level-name">AI</h2>

                    </div>
                    <Link className="level-link" to="/quiz/AI">
                        <span>Start</span> <i className="bi bi-arrow-right"></i>
                    </Link>
                </div>
            </div>

            {isAdmin && (
                <button className="admin-button" onClick={() => navigate('/admin')}>
                    Admin Controls
                </button>
            )}
        </div>
    );
}

export default Main;
