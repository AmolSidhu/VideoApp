import React, { useEffect } from "react";
import MainNavbar from "../../Components/static/MainNavbar";

const VideoRecommendations = () => {
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "/login/";
    } else {
      document.title = "Edit Video";
    }
    document.title = "Recommendations";
  }, []);
  return (
    <div>
      <MainNavbar />
      <h1>Recommendations Videos</h1>
    </div>
  );
};

export default VideoRecommendations;
