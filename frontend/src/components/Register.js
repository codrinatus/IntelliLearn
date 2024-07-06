import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';


const Register = ({ toggleForm }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [registrationMessage, setRegistrationMessage] = useState('');
    const navigate = useNavigate()

    const handleRegister = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            if (response.ok) {
                setRegistrationMessage('Registration successful!');
            } else {
                const data = await response.json();
                setRegistrationMessage(`Registration failed: ${data.error}`);
            }
        } catch (error) {
            console.error('Error during registration:', error);
            setRegistrationMessage('Error during registration');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        await handleRegister();
    };

    return (
        <div className="container">
            <h1 className="title">IntelliLearn</h1>
            <h2>Register</h2>
            <form className="form" onSubmit={handleSubmit}>
                <input className="input" type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
                <input className="input" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
                <button className="button" type="submit">Register</button>
            </form>
            {registrationMessage && <p>{registrationMessage}</p>}
            <button className="toggle-button" onClick={() => navigate('/login')}>Go to Login</button>
        </div>
    );
};

export default Register;
