import React, { useEffect } from "react";
import MainNavbar from "../../Components/static/MainNavbar";
import TestRequest from "../../Components/requests/TestRequest";

const UploadVideo = () => {
  useEffect(() => {
    document.title = "Test Image";
  }, []);
  return (
    <div>
      <MainNavbar />
      <h1>Upload Video</h1>
      <TestRequest />
    </div>
  );
};

export default UploadVideo;
