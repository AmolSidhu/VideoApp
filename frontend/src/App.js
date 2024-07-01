import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

//pages import General
import Home from "./pages/general/Home";
import Profile from "./pages/general/Profile";

//page import Auth
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import Verification from "./pages/auth/Verification";

//pages import Videos
import UploadVideo from "./pages/videos/UploadVideo";
import VideoPage from "./pages/videos/VideoPage";
import VideoRecommendations from "./pages/videos/VideoRecommendations";
import ViewVideo from "./pages/videos/ViewVideo";
import SearchResult from "./pages/videos/SearchResults";

//pages import misc
import NotFound from "./pages/misc/NotFound";

//import management pages
import ViewAllUploads from "./pages/management/ViewAllUploads";
import EditVideo from "./pages/management/EditVideo";
import ChangePassword from "./pages/management/ChangePassword";
import ForgotPassword from "./pages/management/ForgotPassword";

//testing pages delete later
import Test from "./pages/misc/Test";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route index element={<Home />} />
        <Route path="/home/" element={<Home />} />
        <Route path="/profile/" element={<Profile />} />

        <Route path="/login/" element={<Login />} />
        <Route path="/register/" element={<Register />} />
        <Route path="/verification/" element={<Verification />} />

        <Route path="/upload/" element={<UploadVideo />} />
        <Route path="/video/" element={<VideoPage />} />
        <Route path="/recommendations/" element={<VideoRecommendations />} />
        <Route path="/player/" element={<ViewVideo />} />
        <Route path="/search/v/" element={<SearchResult />} />

        <Route path="*" element={<NotFound />} />

        <Route path="/edit/video/all/" element={<ViewAllUploads />} />
        <Route path="/edit/video/" element={<EditVideo />} />
        <Route path="/change/password/" element={<ChangePassword />} />
        <Route path="/u/forgot-password/" element={<ForgotPassword />} />

        <Route path="/test/" element={<Test />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
