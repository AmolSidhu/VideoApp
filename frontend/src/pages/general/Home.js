import React, {useEffect} from "react";
import MainNavbar from "../../Components/static/MainNavbar";

const Home = () => {
    useEffect(() => {
        document.title = "Home";
    }, []);
    return (
        <div>
        <MainNavbar />
        <h1>Home</h1>
        </div>
    );
}

export default Home;