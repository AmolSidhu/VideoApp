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

  useEffect(() => {
    const fetchVideoRecord = async () => {
      try {
        const token = localStorage.getItem("token");
        const serial = new URLSearchParams(window.location.search).get(
          "serial"
        );
        const response = await fetch(`${server}/get_video_record/${serial}/`, {
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
        setLoading(false);
      } catch (error) {
        setError(error.message);
      }
    };

    fetchVideoRecord();
  }, []);

  const handlePatch = async () => {
    try {
      const token = localStorage.getItem("token");
      const serial = new URLSearchParams(window.location.search).get("serial");
      const response = await fetch(`${server}/update_video_record/${serial}/`, {
        method: "PATCH",
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(video),
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
        const serial = new URLSearchParams(window.location.search).get(
          "serial"
        );
        const response = await fetch(
          `${server}/delete_video_record/${serial}/`,
          {
            method: "DELETE",
            headers: {
              Authorization: token,
              "Content-Type": "application/json",
            },
          }
        );

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

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <input defaultValue={video.title} placeholder="Title" />
      </div>
      <div>
        <textarea defaultValue={video.description} placeholder="Description" />
      </div>
      <div>
        <input type="checkbox" defaultChecked={video.private} /> Private
      </div>
      <div>
        <label>Genres:</label>
        {video.genres &&
          video.genres.map((genre, index) => (
            <div key={index}>
              <input value={genre} readOnly />
              <button
                type="button"
                onClick={() =>
                  setVideo((prevVideo) => ({
                    ...prevVideo,
                    genres: prevVideo.genres.filter((_, i) => i !== index),
                  }))
                }
              >
                Remove
              </button>
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
              <button
                type="button"
                onClick={() =>
                  setVideo((prevVideo) => ({
                    ...prevVideo,
                    directors: prevVideo.directors.filter(
                      (_, i) => i !== index
                    ),
                  }))
                }
              >
                Remove
              </button>
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
              <button
                type="button"
                onClick={() =>
                  setVideo((prevVideo) => ({
                    ...prevVideo,
                    creators: prevVideo.creators.filter((_, i) => i !== index),
                  }))
                }
              >
                Remove
              </button>
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
              <button
                type="button"
                onClick={() =>
                  setVideo((prevVideo) => ({
                    ...prevVideo,
                    writers: prevVideo.writers.filter((_, i) => i !== index),
                  }))
                }
              >
                Remove
              </button>
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
              <button
                type="button"
                onClick={() =>
                  setVideo((prevVideo) => ({
                    ...prevVideo,
                    stars: prevVideo.stars.filter((_, i) => i !== index),
                  }))
                }
              >
                Remove
              </button>
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
        <div style={{ display: "inline-block" }}>
          <img src={video.image} alt="Video thumbnail" />
        </div>
        <div style={{ display: "block", verticalAlign: "top" }}>
          <input type="file" />
        </div>
      </div>
      <button type="submit">Submit</button>
      <button type="button" onClick={handleDelete}>
        Delete
      </button>
    </form>
  );
};

export default EditVideoRecord;
