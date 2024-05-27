import React, { useState, useEffect } from "react";
import VideoPopup from "../popup/VideoPopup";
import server from "../static/Constants";

function RecentlyViewed() {
  const [videos, setVideos] = useState([]);
  const [error, setError] = useState(null);
  const [selectedSerial, setSelectedSerial] = useState(null);

  useEffect(() => {
    const fetchVideos = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${server}/recently_viewed/`, {
          method: "GET",
          headers: {
            Authorization: token,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        setVideos(data.videos || []);
      } catch (error) {
        setError(error.message);
      }
    };

    fetchVideos();
  }, []);

  const openPopup = (serial) => {
    setSelectedSerial(serial);
  };

  const closePopup = () => {
    setSelectedSerial(null);
  };

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (videos.length === 0) {
    return null;
  }

  return (
    <div className="video-list-container">
      <h1>Video History</h1>
      <div className="video-scroll-container">
        {videos.map((video, index) => (
          <div
            key={index}
            className="video-item"
            onClick={() => openPopup(video.serial)}
          >
            <img src={video.image_url} alt={video.title} />
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
}

export default RecentlyViewed;
