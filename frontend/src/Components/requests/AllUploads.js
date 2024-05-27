import React, { useState, useEffect, useRef } from "react";
import server from "../static/Constants";

function AllUploads() {
  const [videos, setVideos] = useState([]);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const loader = useRef(null);

  useEffect(() => {
    const fetchMyVideos = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${server}/get_my_uploads/${page}/`, {
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
        if (data.videos.length === 0) {
          setHasMore(false);
        } else {
          setVideos((prevVideos) => [...prevVideos, ...data.videos]);
          setPage((prevPage) => prevPage + 1);
        }
      } catch (error) {
        setError(error.message);
      }
    };

    if (hasMore) {
      fetchMyVideos();
    }
  }, [page, hasMore]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore) {
          setPage((prevPage) => prevPage + 1);
        }
      },
      { threshold: 1 }
    );

    const currentLoader = loader.current;

    if (currentLoader) {
      observer.observe(currentLoader);
    }

    return () => {
      if (currentLoader) {
        observer.unobserve(currentLoader);
      }
    };
  }, [loader, hasMore]);

  return (
    <div>
      {error && <p>Error: {error}</p>}
      {videos.map((video, index) => (
        <div key={video.serial}>
          <h1>{video.title}</h1>
          <p>{video.description}</p>
          <p>{video.uploaded_date}</p>
          <a href={`/edit/video?serial=${video.serial}`}>Edit</a>
          {hasMore && index === videos.length - 1 && (
            <div ref={loader}>Loading...</div>
          )}
        </div>
      ))}
    </div>
  );
}

export default AllUploads;
