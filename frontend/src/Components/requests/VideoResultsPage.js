import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import VideoPopup from "../popup/VideoPopup";
import server from "../static/Constants";

const VideoResultsPage = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSerial, setSelectedSerial] = useState(null);
  const location = useLocation();

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const queryParams = new URLSearchParams(location.search);
        const query = queryParams.get("query");
        const token = localStorage.getItem("token");

        if (query) {
          const response = await fetch(
            `${server}/video/search/${encodeURIComponent(query)}/`,
            {
              method: "GET",
              headers: {
                Authorization: token,
                "Content-Type": "application/json",
              },
            }
          );

          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }

          const data = await response.json();
          setResults(data.videos);
        }
      } catch (error) {
        console.error("Error fetching search results:", error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [location.search]);

  const openPopup = (serial) => {
    setSelectedSerial(serial);
  };

  const closePopup = () => {
    setSelectedSerial(null);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="video-results-container">
      <h1>Search Results</h1>
      <div className="video-scroll-container">
        {results.map((result, index) => (
          <div
            key={index}
            className="video-item"
            onClick={() => openPopup(result.serial)}
          >
            <img src={result.image_url} alt={result.title} />
            <p>{result.title}</p>
          </div>
        ))}
      </div>
      {selectedSerial && (
        <div className="popup">
          <div className="popup-inner">
            <button onClick={closePopup}>Close</button>
            <VideoPopup serial={selectedSerial} onClose={closePopup} />
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoResultsPage;
