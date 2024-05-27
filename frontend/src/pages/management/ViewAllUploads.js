import React, { useEffect } from "react";
import MainNavbar from "../../Components/static/MainNavbar";
import AllUploads from "../../Components/requests/AllUploads";

const ViewAllUploads = () => {
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "/login/";
    } else {
      document.title = "Edit Video";
    }
    document.title = "All Uploads";
  }, []);
  return (
    <div>
      <MainNavbar />
      <h1>View All Uploads</h1>
      <AllUploads />
    </div>
  );
};

export default ViewAllUploads;
