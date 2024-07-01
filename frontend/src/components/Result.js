import React from "react";
import { Link, useLocation } from "react-router-dom";

function Result() {
    const location = useLocation();
    const allAnswers = location.state?.answers || [];
    const allQuestions = location.state?.questions || [];
    console.log(allAnswers);
    console.log(allQuestions)

    let correctAnswersCount = 0;

    allAnswers.forEach((answer, index) => {
        if (answer.trueAnswer) {
            correctAnswersCount++;
        }
    });

    const percentile = Math.round((correctAnswersCount / allQuestions.length) * 100);

    return (
        <div className="result">
            <div className="result-container">
                <div className="result-bg">
                    <span className="percentage">{percentile}%</span>
                </div>
                <p className="result-detail">
                    You answered {correctAnswersCount} out of {allQuestions.length} questions
                    correctly!
                </p>
                <Link to="/" className="new-quiz">
                    Start a new quiz!
                </Link>
            </div>
            <h2 className="check-answers-title">Check Correct Answers</h2>
            <div className="check-answers-boxes">
                {allQuestions.map((question, index) => (
                    <div
                        key={index}
                        className={
                            allAnswers[index].trueAnswer
                                ? "check-answer-container correct"
                                : "check-answer-container wrong"
                        }
                    >
                        <div className="check-answer-top">
                            <div className="check-texts">
                                <p className="check-answer-count">Question: {index + 1}</p>
                                <h3 className="check-answer-question">{question.question}</h3>
                            </div>
                            <div className="check-icon">
                                <i
                                    className={
                                        allAnswers[index].trueAnswer ? "bi bi-check" : "bi bi-x"
                                    }
                                ></i>
                            </div>
                        </div>
                        <div className="check-answer-bottom">
                            <div className="answer-box">
                                <span className="answer-title">Your Answer</span>
                                <span className="answer-text">{allAnswers[index].answer}</span>
                            </div>
                            <div className="answer-box">
                                <span className="answer-title">Correct Answer</span>
                                <span className="answer-text">
                                    {question[`choice${String.fromCharCode(65 + question.correctchoiceletter.charCodeAt(0) - 65)}`]}
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default Result;
