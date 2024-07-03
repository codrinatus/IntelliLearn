import React, { useState } from "react";
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";

function GeneratedQuestions() {
    const navigate = useNavigate();
    const [selectedQuestions, setSelectedQuestions] = useState([]);
    const location = useLocation();
    const questions = location.state?.questions.questions || [];
    const [editableQuestions, setEditableQuestions] = useState(questions);

    const handleSelectQuestion = (index) => {
        const selected = [...selectedQuestions];
        if (selected.includes(index)) {
            selected.splice(selected.indexOf(index), 1);
        } else {
            selected.push(index);
        }
        setSelectedQuestions(selected);
    };

    const handleQuestionChange = (index, key, value) => {
        const updatedQuestions = [...editableQuestions];
        updatedQuestions[index][key] = value;
        setEditableQuestions(updatedQuestions);
    };

    const handleSubmit = () => {
        const selectedQuestionObjects = selectedQuestions.map(index => editableQuestions[index]);
        axios.post('${process.env.REACT_APP_BACKEND_URL}/insert-questions', selectedQuestionObjects, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('token')}`
            }
        }).then(response => {
            console.log('Questions inserted successfully:', response.data);
            navigate("/main");
        }).catch(error => {
            console.error('There was an error inserting the questions!', error);
        });
    };

    return (
        <div>
            <h2>Select and Edit Questions to Insert into Database</h2>
            <div className="questions-container">
                {editableQuestions.length > 0 ? (
                    editableQuestions.map((question, index) => (
                        <div
                            key={index}
                            className={`question-container ${selectedQuestions.includes(index) ? "selected" : ""}`}
                            onClick={() => handleSelectQuestion(index)}
                        >
                            <textarea
                                className="question-title"
                                value={question.question}
                                onChange={(e) => handleQuestionChange(index, 'question', e.target.value)}
                            />
                            <div className="choices-dropdown">
                                {Object.keys(question).filter(key => key.startsWith('choice')).map((key, choiceIndex) => (
                                    <div key={choiceIndex} className="choice-item">
                                        <input
                                            type="text"
                                            value={question[key]}
                                            onChange={(e) => handleQuestionChange(index, key, e.target.value)}
                                        />
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))
                ) : (
                    <p>No questions available</p>
                )}
            </div>
            <button className="submit-button" onClick={handleSubmit}>Insert Selected Questions</button>
        </div>
    );
}

export default GeneratedQuestions;
