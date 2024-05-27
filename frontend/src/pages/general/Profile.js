import React, { useEffect } from "react";
import MainNavbar from "../../Components/static/MainNavbar";
import MyVideos from "../../Components/requests/MyVideos";

const Profile = () => {
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "/login/";
    } else {
      document.title = "Edit Video";
    }
    document.title = "Profile";
  }, []);
  return (
    <div>
      <MainNavbar />
      <h1>Profile</h1>
      <MyVideos />
    </div>
  );
};

export default Profile;
