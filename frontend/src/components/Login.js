import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {jwtDecode} from 'jwt-decode'

const Login = ({onLoginSuccess, onAdminVerification}) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loginError, setLoginError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async () => {
        try {
            const response = await fetch('http://localhost:3001/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({username, password}),
            });

            if (response.ok) {
                const token = await response.json();
                const decodedToken = jwtDecode(token.token.toString())
                localStorage.setItem('token', token.token.toString());

                localStorage.setItem('isAdmin', decodedToken.sub.admin);
                onLoginSuccess();
                console.log(localStorage.getItem('isAdmin') === 'true')
                if (localStorage.getItem('isAdmin') === 'true') {
                    onAdminVerification();

                }
                navigate('/main')
            } else {
                setLoginError('Login failed. Check your credentials.');
            }
        } catch (error) {
            console.error('Error during login:', error);
            setLoginError('Error during login');
        }
    };

    return (
        <div className="container">
            <h1>Login</h1>
            <form className="form" onSubmit={(e) => {
                e.preventDefault();
                handleLogin();
            }}>
                <input className="input" type="text" placeholder="Username" value={username}
                       onChange={(e) => setUsername(e.target.value)}/>
                <input className="input" type="password" placeholder="Password" value={password}
                       onChange={(e) => setPassword(e.target.value)}/>
                <button className="button" type="submit">Connect</button>
                {/*<button className="button" type="button" onClick={redirectToSwaggerUI}>Go to Swagger UI</button>*/}
            </form>
            {loginError && <p>{loginError}</p>}
            <button className="toggle-button" onClick={() => navigate('/register')}>
                Go to Register
            </button>
        </div>
    );
};

export default Login;
