import React, { useEffect } from "react";
import MainNavbar from "../../Components/static/MainNavbar";

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
    </div>
  );
};

export default SearchResult;
