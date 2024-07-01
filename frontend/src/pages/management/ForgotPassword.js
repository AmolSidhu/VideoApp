import React, { useEffect } from "react";
import MainNavbar from "../../Components/static/MainNavbar";
import ForgotPasswordForm from "../../Components/forms/ForgotPasswordForm";

const ForgotPassword = () => {
    useEffect(() => {
        document.title = "Forgot Password";
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>Forgot Password</h1>
        <ForgotPasswordForm />
        </div>
    );
}

export default ForgotPassword;
