import React, { useEffect, useRef } from "react";
import videojs from "video.js";
import "video.js/dist/video-js.css";
import server from "../static/Constants";
import { useLocation } from "react-router-dom";

const VideoPlayer = () => {
  const videoRef = useRef(null);
  const location = useLocation();
  const search = location.search;

  useEffect(() => {
    const videoElement = videoRef.current;

    if (videoElement) {
      const params = new URLSearchParams(search);
      const serial = params.get("serial");
      const token = localStorage.getItem("token");
      const resume = params.get("resume") === "true";
      const src = `${server}/stream/${serial}/${token}/`;

      console.log("Video source:", src);

      const vjsPlayer = videojs(videoElement, {
        controls: true,
        autoplay: false,
        preload: "auto",
        fluid: true,
        sources: [
          {
            src: src,
            type: "video/mp4",
          },
        ],
      });

      vjsPlayer.ready(() => {
        console.log("Video is ready to be played!");
        if (resume) {
          fetch(`${server}/video_history/${serial}`, {
            method: "GET",
            headers: {
              Authorization: token,
              "Content-Type": "application/json",
            },
          })
            .then((response) => {
              if (!response.ok) {
                throw new Error("Failed to fetch resume time");
              }
              return response.json();
            })
            .then((data) => {
              const resumeTime = data.video_stop_time || 0;
              console.log("Resuming video from:", resumeTime);
              vjsPlayer.currentTime(resumeTime);
            })
            .catch((error) => {
              console.error("Error fetching resume time:", error.message);
            });
        }

        const updatePlaybackTime = () => {
          const currentTime = vjsPlayer.currentTime();
          fetch(`${server}/update_playback_time/`, {
            method: "POST",
            headers: {
              Authorization: token,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              serial: serial,
              currentTime: currentTime,
            }),
          })
            .then((response) => {
              if (!response.ok) {
                throw new Error("Failed to update playback time");
              }
            })
            .catch((error) => {
              console.error("Error updating playback time:", error.message);
            });
        };

        const timerId = setInterval(updatePlaybackTime, 5000);

        return () => {
          clearInterval(timerId);
          if (vjsPlayer) {
            vjsPlayer.dispose();
          }
        };
      });
    }
  }, [search]);

  return (
    <div>
      <div data-vjs-player>
        <video ref={videoRef} className="video-js vjs-big-play-centered" />
      </div>
    </div>
  );
};

export default VideoPlayer;
