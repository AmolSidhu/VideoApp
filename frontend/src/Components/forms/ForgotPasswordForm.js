import React, { useState } from "react";
import server from "../static/Constants";

const ForgotPasswordForm = () => {
    const [email, setEmail] = useState("");
    const [error, setError] = useState("");

    const SendResetEmail = (e) => {
        e.preventDefault();

        fetch(server + "/forgot_password/", {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                email: email,
            }),
        })
            .then((res) => {
                if (!res.ok) {
                    setError("An error occurred during password reset (Network response error)");
                    throw new Error("Network response error");
                }
                return res.json();
            })
            .then((data) => {
                if (data.message) {
                    setError("Password reset email sent");
                } else {
                    setError("An error occurred during password reset (token not received)");
                }
            })
            .catch((_error) => {
                setError("An error occurred during password reset (Validation error)");
            });
    };

    return (
        <div className="standard_form">
            <form onSubmit={SendResetEmail}>
                <div>
                    <label>Email Address</label>
                    <input
                        type="email"
                        value={email}
                        placeholder="Enter email"
                        onChange={(e) => setEmail(e.target.value)}
                    />
                </div>
                <div>
                    <button type="submit">Send Reset Email</button>
                </div>
                <div>
                    <p>{error}</p>
                </div>
            </form>
        </div>
    );
};

export default ForgotPasswordForm;
