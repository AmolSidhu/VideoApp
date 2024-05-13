import React, { useEffect, useState } from "react";
import videojs from "video.js";
import "video.js/dist/video-js.css";
import server from "../static/Constants";
import { useLocation } from "react-router-dom";

const VideoPlayer = () => {
  const videoRef = React.useRef(null);
  const location = useLocation();
  const search = location.search;
  const [player, setPlayer] = useState(null);

  useEffect(() => {
    const videoElement = videoRef.current;

    if (videoElement) {
      const params = new URLSearchParams(search);
      const serial = params.get("serial");
      const token = localStorage.getItem("token");
      const src = `${server}/stream/${serial}/${token}/`;

      console.log("Video source:", src);

      const vjsPlayer = videojs(
        videoElement,
        {
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
        },
        () => {
          console.log("Video is ready to be played!");
        }
      );

      setPlayer(vjsPlayer);

      return () => {
        if (player) {
          player.dispose();
        }
      };
    }
  }, [search, player]);

  return (
    <div>
      <div data-vjs-player>
        <video ref={videoRef} className="video-js vjs-big-play-centered" />
      </div>
    </div>
  );
};

export default VideoPlayer;
