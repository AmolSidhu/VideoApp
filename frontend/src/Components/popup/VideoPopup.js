import React, { useState, useEffect } from "react";
import server from "../static/Constants";

function VideoPopup({ serial, onClose }) {
  const [video, setVideo] = useState(null);
  const [error, setError] = useState(null);
  const [episodes, setEpisodes] = useState([]);
  const [selectedSeason, setSelectedSeason] = useState(null);

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
      if (data.series && data.season_metadata) {
        const firstSeason = Object.keys(data.season_metadata)[0];
        setSelectedSeason(firstSeason);
        fetchEpisodes(firstSeason);
      }
    } catch (error) {
      setError(error.message);
    }
  };

  const fetchEpisodes = async (season) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${server}/episode_data/${serial}/${season}`, {
        method: "GET",  // Change this to "GET"
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      setEpisodes(data.episodes);
    } catch (error) {
      console.error("Error fetching episodes:", error);
    }
  };

  const handleSeasonChange = (event) => {
    const season = event.target.value;
    setSelectedSeason(season);
    fetchEpisodes(season);
  };

  useEffect(() => {
    fetchVideo(); // eslint-disable-next-line
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
    const coParam = video.series ? "s" : "n";
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
            <p>Description: {video.video_description}</p>
            <p>Rating: {video.video_rating}</p>
            {video.series && video.season_metadata && (
              <div>
                <h3>Select Season:</h3>
                <select onChange={handleSeasonChange} value={selectedSeason}>
                  {Object.keys(video.season_metadata).map((season) => (
                    <option key={season} value={season}>
                      Season {season}
                    </option>
                  ))}
                </select>
                {episodes.length > 0 && (
                  <div>
                    <h3>Episodes:</h3>
                    <ul>
                      {episodes.map((episode) => (
                        <li key={episode.video_serial}>
                          {episode.episode} -{" "}
                          <a href={`/player/?serial=${episode.video_serial}&co=${coParam}`}>
                            Play
                          </a>
                          {episode.resume && (
                            <>
                              {" "}or{" "}
                              <a href={`/player/?serial=${episode.video_serial}&resume=true&co=${coParam}`}>
                                Resume
                              </a>
                            </>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
            <a href={`/player/?serial=${serial}&co=${coParam}`}>Watch Video</a>
            <br />
            {video.resume && (
              <a href={`/player/?serial=${serial}&resume=true&co=${coParam}`}>
                Resume
              </a>
            )}
          </div>
        </div>
      </div>
    );
  } else {
    return null;
  }
}

export default VideoPopup;
