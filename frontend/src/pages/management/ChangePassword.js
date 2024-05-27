import React, { useEffect } from "react";
import MainNavbar from "../../Components/static/MainNavbar";

const ChangePassword = () => {
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "/login/";
    } else {
      document.title = "Edit Video";
    }
    document.title = "Edit Video";
  }, []);
  return (
    <div>
      <MainNavbar />
      <h1>Change Password</h1>
    </div>
  );
};

export default ChangePassword;
