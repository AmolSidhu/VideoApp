import React, {useEffect} from "react";
import LoginForm from "../../Components/forms/LoginForm";
import MainNavbar from "../../Components/static/MainNavbar";

const Login = () => {
    useEffect(() => {
        document.title = "Login";
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>Login</h1>
        <LoginForm />
        </div>
    );
}

export default Login;