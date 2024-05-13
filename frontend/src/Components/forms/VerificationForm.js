import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import server from "../static/Constants";



const VerificationForm = () => {
    const [email, setEmail] = useState('');
    const [verificationCode, setVerificationCode] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const VerifyUser = (e) => {
        e.preventDefault();

        console.log(email, verificationCode);
        fetch(server + '/verification/', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                verificationCode: verificationCode,
            }),
        })
            .then((res) => {
                console.log('Response Status:', res.status);
                if (!res.ok) {
                    setError('An error occurred during verification (error code 4766)');
                    throw new Error('Network response error');
                }
                return res.json();
            })
            .then((data) => {
                console.log('Response Data:', data);
                if (data.msg) {
                    navigate('/login/');
                } else {
                    setError('An error occurred during verification (error code 4767)');
                }
            })
            .catch((error) => {
                console.error('Fetch error:', error);
                if (error.response) {
                    setError('An error occurred during verification (error code 4768)');
                }
                setError('An error occurred during verification (error code 4769)');
            });
    };

return (
    <div>
        <Form onSubmit={VerifyUser}>
            <Form.Group>
                <Form.Label>Email address</Form.Label>
                <Form.Control
                type="email"
                placeholder="Enter email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                />
            </Form.Group>
            <Form.Group>
                <Form.Label>Verification Code</Form.Label>
                <Form.Control
                type="text"
                placeholder="Enter verification code"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                />
            </Form.Group>
            <Form.Group>
                <Button variant="primary" type="submit">
                    Submit
                </Button>
            </Form.Group>
        </Form>
        <p>{error}</p>
    </div>
    )
}

export default VerificationForm;
