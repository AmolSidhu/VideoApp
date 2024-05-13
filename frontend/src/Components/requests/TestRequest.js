import React, { useState, useEffect } from "react";
import server from "../static/Constants";

const TestRequest = () => {
  const [image, setImage] = useState(null);

  useEffect(() => {
    const fetchImage = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(`${server}/image_test/`, {
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
        setImage(data.image);
        console.log(data.image);
      } catch {}
    };
    fetchImage();
  }, []);

  return (
    <div>
      <h1>Test Request</h1>
      <p>Test Request</p>
      <img src={image} alt="Test" />
    </div>
  );
};

export default TestRequest;
