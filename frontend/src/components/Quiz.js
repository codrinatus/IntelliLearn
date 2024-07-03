import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from 'axios';
// axios.defaults.baseUrl = "http://localhost:3001/"

function Quiz() {
    const { level } = useParams();
    const navigate = useNavigate();

    const [ questions, setQuestions ] = useState([])
    const [ currentQuestion, setCurrentQuestion ] = useState(0)
    const [questionStats, setQuestionStats] = useState([]);


    const [isNextButton, setIsNextButton] = useState(false);
    const [isResultButton, setIsResultButton] = useState(false);
    const [selectedIndex, setSelectedIndex] = useState();
    const [selectedAnswers, setSelectedAnswers] = useState([]);
    const [time, setTime] = useState(30);
    const [isErrorMessage, setIsErrorMessage] = useState(false);
    const [isResult, setIsResult] = useState(false);

    useEffect(() => {
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/quiz/${level}`, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('token')}`
            }
        })
            .then(response => {
                console.log(response.data)
                setQuestions(response.data);
            })
            .catch(error => {
                console.error("There was an error fetching the questions!", error);
            });
    }, [level]);


    const selectAnswer = (index) => {
        if (currentQuestion === questions.length - 1) {
            setIsNextButton(false);
            setIsResultButton(true);
        } else {
            setIsNextButton(true);
        }
        setSelectedIndex(index);
    };

    const nextQuestion = async (index) => {
        if (currentQuestion >= questions.length - 1) {
            addAnswer(index);
            setCurrentQuestion(0);
            setIsResult(true);
            console.log(questionStats)
            await updateQuestionStats(questionStats);
        } else {
            setTime(30);
            setIsNextButton(false);
            addAnswer(index);
            setCurrentQuestion(currentQuestion + 1);
            setSelectedIndex();
        }
    };

    const updateQuestionStats = async (stats) => {
        const token = localStorage.getItem('token');
        try {
            await axios.post('http://localhost:3001/updatestats', {
                question_stats: stats
            }, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
        } catch (error) {
            console.error('Error updating question stats:', error);
        }
    };

    const addAnswer = (index) => {
        const selectedAnswer = {
            answer: questions[currentQuestion][`choice${String.fromCharCode(65 + index)}`],
            trueAnswer: questions[currentQuestion].correctchoiceletter === String.fromCharCode(65 + index)
        };
        console.log("Adding answer: ", selectedAnswer);
        const newAnswers = [...selectedAnswers, selectedAnswer];
        console.log("Updated answers array: ", newAnswers); // Debugging log
        setSelectedAnswers(newAnswers);
        const questionId = questions[currentQuestion].question_id
        const questionDiff = questions[currentQuestion].difficulty
        const status = index != null && questions[currentQuestion].correctchoiceletter === String.fromCharCode(65 + index)
        const newStat = {
            question_id:questionId,
            status: status === true ? 2:1,
            difficulty: questionDiff
        }
        setQuestionStats((prevStats) => [...prevStats, newStat]);
        console.log(newStat);
    };

    const handleSeeResults = () => {
        navigate("/result", {
            state: {
                answers: selectedAnswers,
                questions: questions,
            },
        });
    };


    useEffect(() => {
        const timer = setInterval(() => {
            setTime((prevTime) => prevTime - 1);
        }, 1000);
        time <= 5 ? setIsErrorMessage(true) : setIsErrorMessage(false);
        if (time < 0) {
            nextQuestion(null);
        }
        return () => clearInterval(timer);
    }, [time]);

    if (!questions || questions.length === 0) {
        return <div>Loading...</div>;
    }

    return isResult ? (
        handleSeeResults()
    ) : (
        <div>
            <div className="progress-container">
                <div className="progress-top">
                    <div className="progress-texts">
                        <h2 className="progress-title">Progress</h2>
                        <p className="progress-description">
                            Topic: {level}
                        </p>
                    </div>
                    <div className="progress-icon">
                        <i className="bi bi-bar-chart"></i>
                    </div>
                </div>
                <div className="progress-bottom">
                    <div
                        className="progress-circle"
                        aria-valuemin="0"
                        aria-valuemax="100"
                        style={{
                            "--value":
                                ((currentQuestion + 1) / questions.length) * 100,
                        }}
                    >
                        <span className="progress-big">{currentQuestion + 1}</span>
                        <span className="progress-mini">/{questions.length}</span>
                    </div>
                    <p className="progress-detail">
                        You are solving the question number {currentQuestion + 1} out of a total of{" "}
                        {questions.length} questions
                    </p>
                </div>
            </div>
            <div className="question-container">
                <div className="question-text">
                    <h2 className="question-title">Question: {currentQuestion + 1}</h2>
                    <h3 className="question">
                        {questions[currentQuestion].question}
                    </h3>
                </div>
                <div
                    className="progress-circle time"
                    aria-valuemin="0"
                    aria-valuemax="100"
                    style={{ "--value": (time / 30) * 100 }}
                >
                    <span className="time">{time}</span>
                </div>
            </div>

            <div className="answers-containers">
                {Object.keys(questions[currentQuestion]).filter(key => key.startsWith('choice')).map((key, index) => (
                    <label
                        onClick={() => selectAnswer(index)}
                        key={index}
                        htmlFor={index}
                        className={selectedIndex === index ? "answer-label selected" : "answer-label"}
                    >
                        {questions[currentQuestion][key]}
                        <input type="radio" name="answer" id={index} />
                    </label>
                ))}
            </div>

            {isNextButton ? (
                <div className="next">
                    <button
                        onClick={() => nextQuestion(selectedIndex)}
                        type="button"
                        className="next-btn"
                    >
                        Next Question
                        <div className="icon">
                            <i className="bi bi-arrow-right"></i>
                        </div>
                    </button>
                </div>
            ) : null}

            {isResultButton ? (
                <div className="next">
                    <button
                        onClick={() => nextQuestion(selectedIndex)}
                        type="button"
                        className="next-btn result-btn"
                    >
                        See Results
                        <div className="icon">
                            <i className="bi bi-bar-chart"></i>
                        </div>
                    </button>
                </div>
            ) : null}

            {isErrorMessage ? (
                <div className="message animation">
                    <div className="icon">
                        <i className="bi bi-exclamation-triangle"></i>
                    </div>
                    <span>You must hurry up!</span>
                </div>
            ) : null}
        </div>
    );
}

export default Quiz;
