import React, { useEffect } from "react";
import MainNavbar from "../../Components/static/MainNavbar";
import VideoList from "../../Components/requests/VideoList";
import GenreVideoList from "../../Components/requests/GenreVideoList";
import RecentlyViewed from "../../Components/requests/RecentlyViewed";
import VideoSearch from "../../Components/requests/VideoSearch";

const VideoPage = () => {
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "/login/";
    } else {
      document.title = "Edit Video";
    }
    document.title = "View Videos";
  }, []);
  return (
    <div>
      <MainNavbar />
      <VideoSearch />
      <h1>Video Page</h1>
      <VideoList />
      <br />
      <br />
      <RecentlyViewed />
      <br />
      <br />
      <GenreVideoList />
    </div>
  );
};

export default VideoPage;
