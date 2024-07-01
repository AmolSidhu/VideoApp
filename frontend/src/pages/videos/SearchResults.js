import React, { useEffect } from "react";
import MainNavbar from "../../Components/static/MainNavbar";
import VideoResultsPage from "../../Components/requests/VideoResultsPage";

const SearchResult = () => {
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "/login/";
    }
    document.title = "Search Results";
  }, []);
  return (
    <div>
      <MainNavbar />
      <h1>Results</h1>
      <VideoResultsPage />
    </div>
  );
};

export default SearchResult;
