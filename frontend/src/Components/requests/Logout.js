import server from "../static/Constants";

const handleLogout = async () => {
  try {
    const response = await fetch(`${server}/logout/`, {
      method: "PATCH",
      credentials: "include",
    });

    if (response.ok) {
      console.log("Logged out successfully");
      localStorage.removeItem("token");
      document.cookie =
        "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
      window.location.href = "/login/";
    } else {
      console.error("Failed to logout");
    }
  } catch (error) {
    console.error("Error during logout:", error);
  }
};

export default handleLogout;
