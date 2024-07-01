import React, { useEffect, useState } from "react";
import server from "../static/Constants";

const EditVideoRecord = () => {
  const [video, setVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newGenre, setNewGenre] = useState("");
  const [newDirector, setNewDirector] = useState("");
  const [newCreator, setNewCreator] = useState("");
  const [newWriter, setNewWriter] = useState("");
  const [newStar, setNewStar] = useState("");
  const [thumbnail, setThumbnail] = useState(null);
  const [seasons, setSeasons] = useState([]);
  const [currentSeason, setCurrentSeason] = useState(1);
  const [episodes, setEpisodes] = useState([]);
  const [originalEpisodes, setOriginalEpisodes] = useState([]);

  useEffect(() => {
    const fetchVideoRecord = async () => {
      try {
        const token = localStorage.getItem("token");
        const serial = new URLSearchParams(window.location.search).get("serial");
        const response = await fetch(`${server}/get_video_record/${serial}/`, {
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
        setVideo(data.video);
        setSeasons(Object.keys(data.video.season_metadata).map(Number));
        setCurrentSeason(1);
        fetchEpisodes(1, serial);
        setLoading(false);
      } catch (error) {
        setError(error.message);
      }
    };

    fetchVideoRecord();
  }, []);

  const fetchEpisodes = async (season, serial) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${server}/get_season_records/${serial}/${season}/`, {
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
      setEpisodes(data.season);
      setOriginalEpisodes(data.season.map(ep => ({ ...ep })));
    } catch (error) {
      setError(error.message);
    }
  };

  const handlePatch = async () => {
    try {
      const token = localStorage.getItem("token");
      const serial = new URLSearchParams(window.location.search).get("serial");
      const formData = new FormData();
      formData.append("title", video.title);
      formData.append("description", video.description);
      formData.append("private", video.private);
      formData.append("genres", JSON.stringify(video.genres));
      formData.append("directors", JSON.stringify(video.directors));
      formData.append("creators", JSON.stringify(video.creators));
      formData.append("writers", JSON.stringify(video.writers));
      formData.append("stars", JSON.stringify(video.stars));
      if (thumbnail) {
        formData.append("thumbnail", thumbnail);
      }

      const response = await fetch(`${server}/update_video_record/${serial}/`, {
        method: "PATCH",
        headers: {
          Authorization: token,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
    } catch (error) {
      setError(error.message);
    }
  };

  const handleDelete = async () => {
    if (window.confirm("Are you sure you want to delete this record?")) {
      try {
        const token = localStorage.getItem("token");
        const serial = new URLSearchParams(window.location.search).get("serial");
        const response = await fetch(`${server}/delete_video_record/${serial}/`, {
          method: "DELETE",
          headers: {
            Authorization: token,
            "Content-Type": "application/json",
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
      } catch (error) {
        setError(error.message);
      }
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handlePatch();
  };

  const handleAddGenre = () => {
    if (newGenre.trim() !== "") {
      setVideo((prevVideo) => ({
        ...prevVideo,
        genres: [...(prevVideo.genres || []), newGenre.trim()],
      }));
      setNewGenre("");
    }
  };

  const handleAddDirector = () => {
    if (newDirector.trim() !== "") {
      setVideo((prevVideo) => ({
        ...prevVideo,
        directors: [...(prevVideo.directors || []), newDirector.trim()],
      }));
      setNewDirector("");
    }
  };

  const handleAddCreator = () => {
    if (newCreator.trim() !== "") {
      setVideo((prevVideo) => ({
        ...prevVideo,
        creators: [...(prevVideo.creators || []), newCreator.trim()],
      }));
      setNewCreator("");
    }
  };

  const handleAddWriter = () => {
    if (newWriter.trim() !== "") {
      setVideo((prevVideo) => ({
        ...prevVideo,
        writers: [...(prevVideo.writers || []), newWriter.trim()],
      }));
      setNewWriter("");
    }
  };

  const handleAddStar = () => {
    if (newStar.trim() !== "") {
      setVideo((prevVideo) => ({
        ...prevVideo,
        stars: [...(prevVideo.stars || []), newStar.trim()],
      }));
      setNewStar("");
    }
  };

  const handleSeasonChange = (season) => {
    setCurrentSeason(season);
    const serial = new URLSearchParams(window.location.search).get("serial");
    fetchEpisodes(season, serial);
  };

  const handleEpisodeChange = (index, field, value) => {
    setEpisodes((prevEpisodes) =>
      prevEpisodes.map((ep, i) =>
        i === index ? { ...ep, [field]: value } : ep
      )
    );
  };

  const handleSaveEpisode = async (index) => {
    try {
      const token = localStorage.getItem("token");
      const serial = new URLSearchParams(window.location.search).get("serial");
      const episodeData = episodes[index];
      const originalEpisodeData = originalEpisodes[index];
      const response = await fetch(`${server}/update_episode_record/${serial}/${currentSeason}/${originalEpisodeData.episode}/`, {
        method: "PATCH",
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          master_serial: video.serial,
          new_episode: episodeData.episode,
          new_season: episodeData.season,
          episode_serial: originalEpisodeData.episode_serial
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
    } catch (error) {
      setError(error.message);
    }
  };

  const handleDeleteEpisode = async (episode, season) => {
    if (window.confirm("Are you sure you want to delete this episode?")) {
      try {
        const token = localStorage.getItem("token");
        const serial = new URLSearchParams(window.location.search).get("serial");
        const originalEpisode = originalEpisodes.find(ep => ep.episode === episode);
        const response = await fetch(`${server}/delete_episode_record/${serial}/${season}/${originalEpisode.episode}/`, {
          method: "DELETE",
          headers: {
            Authorization: token,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            master_id: video.serial,
            episode_serial: originalEpisode.episode_serial
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
      } catch (error) {
        setError(error.message);
      }
    }
  };

  const handleSeasonUpdate = async () => {
    try {
      const token = localStorage.getItem("token");
      const serial = new URLSearchParams(window.location.search).get("serial");
      const response = await fetch(`${server}/update_season_records/${serial}/`, {
        method: "PATCH",
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          master_id: video.id,
          season: currentSeason,
          new_season: currentSeason,
          new_episode: episodes.map((episode) => episode.episode),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
    } catch (error) {
      setError(error.message);
    }
  };

  const handleDeleteSeason = async (season) => {
    const confirmation = window.prompt("Type DELETE to confirm deletion of this season:");
    if (confirmation === "DELETE") {
      try {
        const token = localStorage.getItem("token");
        const serial = new URLSearchParams(window.location.search).get("serial");
        const response = await fetch(`${server}/delete_season_records/${serial}/`, {
          method: "DELETE",
          headers: {
            Authorization: token,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            master_id: video.id,
            season: season,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
      } catch (error) {
        setError(error.message);
      }
    } else {
      alert("Incorrect confirmation input. Season deletion aborted.");
    }
  };

  const handleImageChange = (e) => {
    setThumbnail(e.target.files[0]);
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Thumbnail:</label>
          {video.image && (
            <img src={video.image} alt="Current Thumbnail" style={{ maxWidth: "200px" }} />
          )}
          <input type="file" onChange={handleImageChange} accept="image/*" />
        </div>
        <div>
          <label>Title:</label>
          <input
            value={video.title}
            onChange={(e) => setVideo({ ...video, title: e.target.value })}
            required
          />
        </div>
        <div>
          <label>Description:</label>
          <textarea
            value={video.description}
            onChange={(e) => setVideo({ ...video, description: e.target.value })}
            required
          />
        </div>
        <div>
          <label>Private:</label>
          <input
            type="checkbox"
            checked={video.private}
            onChange={(e) => setVideo({ ...video, private: e.target.checked })}
          />
        </div>
        <div>
          <label>Genres:</label>
          {video.genres &&
            video.genres.map((genre, index) => (
              <div key={index}>
                <input value={genre} readOnly />
              </div>
            ))}
          <input
            value={newGenre}
            onChange={(e) => setNewGenre(e.target.value)}
            placeholder="Add Genre"
          />
          <button type="button" onClick={handleAddGenre}>
            Add
          </button>
        </div>
        <div>
          <label>Directors:</label>
          {video.directors &&
            video.directors.map((director, index) => (
              <div key={index}>
                <input value={director} readOnly />
              </div>
            ))}
          <input
            value={newDirector}
            onChange={(e) => setNewDirector(e.target.value)}
            placeholder="Add Director"
          />
          <button type="button" onClick={handleAddDirector}>
            Add
          </button>
        </div>
        <div>
          <label>Creators:</label>
          {video.creators &&
            video.creators.map((creator, index) => (
              <div key={index}>
                <input value={creator} readOnly />
              </div>
            ))}
          <input
            value={newCreator}
            onChange={(e) => setNewCreator(e.target.value)}
            placeholder="Add Creator"
          />
          <button type="button" onClick={handleAddCreator}>
            Add
          </button>
        </div>
        <div>
          <label>Writers:</label>
          {video.writers &&
            video.writers.map((writer, index) => (
              <div key={index}>
                <input value={writer} readOnly />
              </div>
            ))}
          <input
            value={newWriter}
            onChange={(e) => setNewWriter(e.target.value)}
            placeholder="Add Writer"
          />
          <button type="button" onClick={handleAddWriter}>
            Add
          </button>
        </div>
        <div>
          <label>Stars:</label>
          {video.stars &&
            video.stars.map((star, index) => (
              <div key={index}>
                <input value={star} readOnly />
              </div>
            ))}
          <input
            value={newStar}
            onChange={(e) => setNewStar(e.target.value)}
            placeholder="Add Star"
          />
          <button type="button" onClick={handleAddStar}>
            Add
          </button>
        </div>
        <div>
          <button type="submit">Save Video</button>
          <button type="button" onClick={handleDelete}>
            Delete Video
          </button>
        </div>
      </form>

      {video.series && (
        <div>
          <h2>Seasons:</h2>
          {seasons.map((season) => (
            <div key={season}>
              <h3>Season {season}</h3>
              <button onClick={() => handleSeasonChange(season)}>
                View Season {season}
              </button>
              <button onClick={() => handleDeleteSeason(season)}>
                Delete Season {season}
              </button>
              {currentSeason === season && (
                <form onSubmit={handleSeasonUpdate}>
                  <div>
                    <label>Season:</label>
                    <label>Episode:</label>
                  </div>
                  {episodes.map((episode, index) => (
                    <div key={index} style={{ display: "flex", alignItems: "center" }}>
                      <input
                        value={episode.season}
                        onChange={(e) => handleEpisodeChange(index, "season", e.target.value)}
                        placeholder="Season"
                      />
                      <input
                        value={episode.episode}
                        onChange={(e) => handleEpisodeChange(index, "episode", e.target.value)}
                        placeholder="Episode"
                      />
                      <button type="button" onClick={() => handleSaveEpisode(index)}>
                        Save
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteEpisode(episode.episode, currentSeason)}
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                  <button type="submit">Save Season {currentSeason}</button>
                </form>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EditVideoRecord;
