import React, { useState } from 'react';
import {useNavigate} from "react-router-dom";

const Admin = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('');
    const [processStatus, setProcessStatus] = useState('');
    const navigate  = useNavigate()


    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
    };

    const handleFileUpload = async () => {
        if (!selectedFile) {
            setUploadStatus('No file selected');
            return;
        }

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            setUploadStatus('Uploading...');
            const response = await fetch('${process.env.REACT_APP_BACKEND_URL}/upload', {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('token')}`,
                },
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                setUploadStatus('File uploaded successfully');
                console.log(result)
                setProcessStatus(result.text);
                navigate("/generatedquestions", {
                    state: {
                        questions: result,
                    },
                });

            } else {
                setUploadStatus('File upload failed');
            }
        } catch (error) {
            console.error('Error during file upload:', error);
            setUploadStatus('Error during file upload');
        }
    };

    return (
        <div className="admin-container">
            <h1>Admin Controls</h1>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleFileUpload}>Upload PDF</button>
            <p>{uploadStatus}</p>
        </div>
    );
};

export default Admin;
