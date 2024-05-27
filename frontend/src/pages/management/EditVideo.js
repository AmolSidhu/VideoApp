import React, { useEffect } from "react";
import MainNavbar from "../../Components/static/MainNavbar";
import EditVideoRecord from "../../Components/forms/EditVideoRecord";

const EditVideo = () => {
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "/login/";
    } else {
      document.title = "Edit Video";
    }
  }, []);
  return (
    <div>
      <MainNavbar />
      <h1>Edit Video</h1>
      <EditVideoRecord />
    </div>
  );
};

export default EditVideo;
