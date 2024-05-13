import React, { useEffect } from "react";
import MainNavbar from "../../Components/static/MainNavbar";
import VideoPlayer from "../../Components/requests/VideoStream";

const ViewVideo = () => {
  useEffect(() => {
    document.title = "View";
  }, []);
  return (
    <div>
      <MainNavbar />
      <h1>View Page</h1>
      <VideoPlayer />
    </div>
  );
};

export default ViewVideo;
