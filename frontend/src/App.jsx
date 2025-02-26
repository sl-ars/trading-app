import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
// import Home from "./pages/Home";
import axios from "axios";

function App() {
  const [user, setUser] = useState(null);
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/users/profile/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
        });
        setUser(response.data);
      } catch (error) {
        setUser(null);
      }
    };
    fetchUser();
  }, []);

  return (
    <Router>
      <Navbar user={user} setUser={setUser} />
      <Routes>
        {/*<Route path="/" element={<Home />} />*/}
        <Route path="/login" element={<Login setUser={setUser} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </Router>
  );
}

export default App;