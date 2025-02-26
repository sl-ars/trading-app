import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const Login = ({ setUser }) => {
  const navigate = useNavigate();
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });

  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/users/login/`, formData);
      localStorage.setItem("access_token", response.data.access);
      localStorage.setItem("user", JSON.stringify(response.data.user));

      setUser(response.data.user);
      setMessage({ type: "success", text: "Login successful! Redirecting..." });

      setTimeout(() => {
        navigate("/");
      }, 1500);
    } catch (error) {
      setMessage({ type: "error", text: "Invalid credentials! Try again." });
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="w-full max-w-lg bg-white p-8 rounded-lg shadow-md border">
        <h2 className="text-3xl font-semibold text-center mb-6 text-gray-800">Login</h2>

        {message && (
          <div className={`text-center py-2 mb-2 ${message.type === "success" ? "text-green-600" : "text-red-600"}`}>
            {message.text}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block font-medium mb-1 text-gray-700">Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              className="border p-2 w-full rounded-md focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block font-medium mb-1 text-gray-700">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              className="border p-2 w-full rounded-md focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-md font-semibold hover:bg-blue-700 transition"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p className="text-center mt-4">
          Don't have an account?{" "}
          <button className="text-blue-500 hover:underline" onClick={() => navigate("/register")}>
            Register
          </button>
        </p>
      </div>
    </div>
  );
};

export default Login;