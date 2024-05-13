import React, { useState, useEffect } from "react";
import server from "../static/Constants";
import VideoPopup from "../popup/VideoPopup";

function GenreVideoList() {
  const [genres, setGenres] = useState([]);
  const [error, setError] = useState(null);
  const [videosByGenre, setVideosByGenre] = useState({});
  const [selectedSerial, setSelectedSerial] = useState(null);

  useEffect(() => {
    const fetchGenres = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${server}/get_genres/`, {
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
        setGenres(data.genres.map((genre) => genre.genre));
        // Fetch videos for each genre
        await Promise.all(
          data.genres.map((genre) => fetchVideosByGenre(genre.genre))
        );
      } catch (error) {
        setError(error.message);
      }
    };

    fetchGenres();
  }, []);

  const fetchVideosByGenre = async (genre) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${server}/get_video_by_genre/${genre}`, {
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
      setVideosByGenre((prevVideosByGenre) => ({
        ...prevVideosByGenre,
        [genre]: data.videos,
      }));
    } catch (error) {
      setError(error.message);
    }
  };

  const openPopup = (serial) => {
    setSelectedSerial(serial);
  };

  const closePopup = () => {
    setSelectedSerial(null);
  };

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      {genres.map((genre, index) => (
        <div key={index}>
          <h2>{genre}</h2>
          <div className="video-scroll-container">
            {videosByGenre[genre] &&
              videosByGenre[genre].map((video, index) => (
                <div
                  key={index}
                  className="video-item"
                  onClick={() => openPopup(video.serial)}
                >
                  <img src={video.image_url} alt={video.title} />
                </div>
              ))}
          </div>
        </div>
      ))}
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

export default GenreVideoList;
