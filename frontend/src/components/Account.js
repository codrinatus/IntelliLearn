import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Modal } from 'react-bootstrap';

const Account = () => {
    const [questions, setQuestions] = useState({});
    const [userStats, setUserStats] = useState([]);
    const [questioNR, setQuestioNR] = useState(0);
    const [selectedQuestion, setSelectedQuestion] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [selectedStatus, setSelectedStatus] = useState(0);

    useEffect(() => {
        const fetchAccountData = async () => {
            try {
                const response = await axios.get('${process.env.REACT_APP_BACKEND_URL}/account', {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('token')}`
                    }
                });
                console.log('Response:', response.data);
                setQuestions(response.data.questions);
                setUserStats(response.data.user_stats);
                setQuestioNR(response.data.last_question_id);
            } catch (error) {
                console.error('Error fetching account data:', error);
            }
        };

        fetchAccountData();
    }, []);

    const getStatus = (questionId) => {
        const stat = userStats.find(stat => stat.question_id === questionId);
        return stat ? stat.status : 0;
    };

    const getColor = (status, difficulty) => {
        const colors = {
            0: 'grey',
            1: { easy: 'lightgreen', medium: 'lightyellow', hard: 'lightcoral' },
            2: { easy: 'green', medium: 'yellow', hard: 'red' }
        };
        if (status === 0) return colors[0];
        if (status === 1) return colors[1][difficulty];
        if (status === 2) return colors[2][difficulty];
    };

    const handleClick = (questionId) => {
        const status = getStatus(questionId);
        if (status > 0) {
            setSelectedQuestion(questions[questionId]);
            setSelectedStatus(status);
            setShowModal(true);
        }
    };

    return (
        <div className="account-container">
            <h1>Account Page</h1>
            <div className="questions-grid">
                {Array.from({ length: questioNR }, (_, i) => i + 1).map(questionId => {
                    const question = questions[questionId] || {};
                    const status = getStatus(questionId);
                    return (
                        <div
                            key={questionId}
                            className="question-id"
                            style={{ backgroundColor: getColor(status, question.difficulty) }}
                            onClick={() => handleClick(questionId)}
                        >
                            {questionId}
                        </div>
                    );
                })}
            </div>

            <Modal show={showModal} onHide={() => setShowModal(false)} centered className="custom-modal">
                <div
                    className="modal-content"
                    style={{
                        backgroundColor: selectedQuestion ? getColor(getStatus(selectedQuestion.question_id), selectedQuestion.difficulty) : 'white'
                    }}
                >
                    <div className="modal-header">
                        <button type="button" className="close" onClick={() => setShowModal(false)}>
                            &times;
                        </button>
                    </div>
                    <div className="modal-body">
                        {selectedQuestion && (
                            <>
                                <p><strong>Question:</strong> {selectedQuestion.question}</p>
                                <p><strong>Response:</strong> {selectedStatus === 2 ? selectedQuestion.correct_response : '?'}</p>
                            </>
                        )}
                    </div>
                </div>
            </Modal>
        </div>
    );
};

export default Account;
