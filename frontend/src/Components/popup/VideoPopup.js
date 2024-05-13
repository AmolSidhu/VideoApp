import React, { useState, useEffect } from "react";
import server from "../static/Constants";

function VideoPopup({ serial, onClose }) {
  const [video, setVideo] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchVideo = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${server}/video_data/${serial}`, {
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
        setVideo(data);
        console.log(data);
      } catch (error) {
        setError(error.message);
      }
    };

    fetchVideo();
  }, [serial]);

  if (error) {
    return (
      <div className="popup">
        <div className="popup-inner">
          <button onClick={onClose}>Close</button>
          <p>Error: {error}</p>
        </div>
      </div>
    );
  } else if (video) {
    return (
      <div className="popup">
        <div className="popup-inner">
          <button onClick={onClose}>Close</button>
          <div>
            <h2>{video.video_name}</h2>
            {video.video_genres && video.video_genres.length > 0 && (
              <p>Tags: {video.video_genres.join(", ")}</p>
            )}
            {video.video_directors && video.video_directors.length > 0 && (
              <p>Directors: {video.video_directors.join(", ")}</p>
            )}
            {video.video_writers && video.video_writers.length > 0 && (
              <p>Writers: {video.video_writers.join(", ")}</p>
            )}
            {video.video_stars && video.video_stars.length > 0 && (
              <p>Stars: {video.video_stars.join(", ")}</p>
            )}
            {video.video_creators && video.video_creators.length > 0 && (
              <p>Creators: {video.video_creators.join(", ")}</p>
            )}
            <p>Duration: {video.video_duration}</p>
            <p>Serial: {serial}</p>
            <p>Total Rating Score: {video.video_rating}</p>
            <p>Description: {video.video_description}</p>
            <a href={`/player/?serial=${serial}`}>Watch Video</a>
          </div>
        </div>
      </div>
    );
  } else {
    return null;
  }
}

export default VideoPopup;
