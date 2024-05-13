import React, {useEffect} from "react";
import MainNavbar from "../../Components/static/MainNavbar";

const VideoRecommendations = () => {
    useEffect(() => {
        document.title = "Recommendations";
    }, []);
    return (
        <div>
            <MainNavbar />
        <h1>Recommendationed Videos</h1>
        </div>
    );
}

export default VideoRecommendations;