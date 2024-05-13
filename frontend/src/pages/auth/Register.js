import React, {useEffect} from "react";
import RegistrationForm from "../../Components/forms/RegistrationForm";
import MainNavbar from "../../Components/static/MainNavbar";


const Register = () => {
    useEffect(() => {
        document.title = "Register";
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>Register</h1>
        <RegistrationForm />
        </div>
    );
}

export default Register;