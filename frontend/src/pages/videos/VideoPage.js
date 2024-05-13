import React, { useEffect } from "react";
import MainNavbar from "../../Components/static/MainNavbar";
import VideoList from "../../Components/requests/VideoList";
import GenreVideoList from "../../Components/requests/GenreVideoList";

const VideoPage = () => {
  useEffect(() => {
    document.title = "View Videos";
  }, []);
  return (
    <div>
      <MainNavbar />
      <h1>Video Page</h1>
      <VideoList />
      <br />
      <br />
      <GenreVideoList />
    </div>
  );
};

export default VideoPage;
