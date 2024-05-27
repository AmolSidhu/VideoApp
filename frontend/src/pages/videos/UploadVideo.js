import React, { useEffect } from "react";
import MainNavbar from "../../Components/static/MainNavbar";
import UploadVideoForm from "../../Components/forms/UploadVideoForm";

const UploadVideo = () => {
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "/login/";
    } else {
      document.title = "Edit Video";
    }
    document.title = "Upload Video";
  }, []);
  return (
    <div>
      <MainNavbar />
      <h1>Upload Video</h1>
      <UploadVideoForm />
    </div>
  );
};

export default UploadVideo;
