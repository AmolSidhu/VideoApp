import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Form from "react-bootstrap/Form";
import Button from "react-bootstrap/Button";
import server from "../static/Constants";

const VerificationForm = () => {
    const [email, setEmail] = useState('');
    const [verificationCode, setVerificationCode] = useState('');
    const [error, setError] = useState('');
    const [resendError, setResendError] = useState('');
    const [canResend, setCanResend] = useState(true);
    const [timer, setTimer] = useState(0);
    const navigate = useNavigate();

    useEffect(() => {
        let interval;
        if (timer > 0) {
            interval = setInterval(() => {
                setTimer((prev) => prev - 1);
            }, 1000);
        } else {
            setCanResend(true);
        }
        return () => clearInterval(interval);
    }, [timer]);

    const VerifyUser = (e) => {
        e.preventDefault();
        setError('');
        setResendError('');

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

    const handleResendEmail = () => {
        if (!canResend) {
            setResendError('Please wait before requesting a new email.');
            return;
        }

        fetch(server + '/resend_verification/', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
            }),
        })
            .then((res) => {
                if (!res.ok) {
                    setResendError('Failed to resend verification email.');
                    throw new Error('Network response error');
                }
                return res.json();
            })
            .then((data) => {
                if (data.success) {
                    setCanResend(false);
                    setTimer(120);
                    setResendError('Verification email resent. Please check your email.');
                } else {
                    setResendError('Failed to resend verification email.');
                }
            })
            .catch((error) => {
                console.error('Fetch error:', error);
                setResendError('An error occurred while resending the verification email.');
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
            <p>
                Please check your email and spam folder for a verification email. If you did not receive an email{' '}
                <button type="button" onClick={handleResendEmail} disabled={!canResend} style={{ background: 'none', color: 'blue', textDecoration: 'underline', border: 'none', padding: 0, cursor: 'pointer' }}>
                    click here
                </button>.
            </p>
            <p>{error}</p>
            <p>{resendError}</p>
            <p>{!canResend && `Please wait ${timer} seconds before resending the email.`}</p>
        </div>
    );
};

export default VerificationForm;
