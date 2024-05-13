import React, { useEffect } from "react";
import MainNavbar from "../../Components/static/MainNavbar";
import UploadVideoForm from "../../Components/forms/UploadVideoForm";

const UploadVideo = () => {
  useEffect(() => {
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
