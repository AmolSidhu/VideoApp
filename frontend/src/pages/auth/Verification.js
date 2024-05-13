import React, {useEffect} from "react";
import VerificationForm from "../../Components/forms/VerificationForm";
import MainNavbar from "../../Components/static/MainNavbar";

const Verification = () => {
    useEffect(() => {
        document.title = "Verification";
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>Verification</h1>
        <VerificationForm />
        </div>
    );
}

export default Verification;