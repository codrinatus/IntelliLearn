import React from "react";
import ReactDOM from "react-dom/client";
import './index.css';
import './assets/css/Style.css';
import './assets/css/Login.css'
import './assets/css/Main.css'
import './assets/css/Quiz.css'
import './assets/css/Result.css'
import './assets/css/GeneratedQuestions.css'
import './assets/css/Account.css'
import {BrowserRouter as Router} from "react-router-dom";


import App from "./components/App";


const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
    <Router>
        <App/>
    </Router>
);
