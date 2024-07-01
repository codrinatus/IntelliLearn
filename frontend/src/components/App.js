import React, {useState} from 'react';
import Login from './Login';
import Register from './Register.js';
import Main from './Main.js'
import Quiz from './Quiz.js'
import Result from './Result.js'
import Admin from './Admin.js'
import Account from './Account.js'
import GeneratedQuestions from './GeneratedQuestions'
import {BrowserRouter as Router, Route, Routes, Navigate} from 'react-router-dom';
const App = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isAdmin, setIsAdmin] = useState(false);

    const handleLoginSuccess = () => {
        setIsLoggedIn(true);
    };

    const handleAdminVerification = () => {
        setIsAdmin(true);
    }

    return (
        <div className="app-container">
            <div className="quiz-container">
                    <Routes>
                        <Route path="/" element={isLoggedIn ? <Navigate to="/main"/> : <Navigate to="/login"/>}/>
                        <Route path="/login" element={<Login onLoginSuccess={handleLoginSuccess} onAdminVerification={handleAdminVerification}/>}/>
                        <Route path="/register" element={<Register/>}/>
                        <Route path="/main" element={isLoggedIn ? <Main/> : <Navigate to="/login"/>}/>
                        <Route path="/quiz/:level" element={isLoggedIn ? <Quiz /> : <Navigate to="/login" />} />
                        <Route path="/result" element={isLoggedIn ? <Result /> : <Navigate to="/login" />} />
                        <Route path="/admin" element={(isLoggedIn && isAdmin) ? <Admin /> : <Navigate to="/main" />} />
                        <Route path="/generatedquestions" element={(isLoggedIn && isAdmin) ? <GeneratedQuestions /> : <Navigate to="/main" />} />
                        <Route path="/account" element={isLoggedIn ? <Account /> : <Navigate to="/login" />} />
                    </Routes>
            </div>
        </div>
    )
        ;
};

export default App;
