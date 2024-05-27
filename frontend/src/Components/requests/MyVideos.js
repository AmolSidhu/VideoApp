import React, { useState, useEffect } from "react";
import server from "../static/Constants";

function MyVideos() {
  const [videos, setVideos] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMyVideos = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${server}/get_my_videos/`, {
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
        setVideos(data.videos);
      } catch (error) {
        setError(error.message);
      }
    };

    fetchMyVideos();
  }, []);

  return (
    <div>
      {error && <p>Error: {error}</p>}
      {videos.map((video) => (
        <div key={video.serial}>
          <h1>{video.title}</h1>
          <p>{video.description}</p>
          <p>{video.uploaded_date}</p>
          <a href={`/edit/video?serial=${video.serial}`}>Edit</a>
        </div>
      ))}
      <div>
        <a href={`/edit/video/all/`}>View All Uploads</a>
      </div>
    </div>
  );
}

export default MyVideos;
