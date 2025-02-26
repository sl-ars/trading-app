import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const Register = () => {
  const navigate = useNavigate();
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    password2: "",
    role: "customer",
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

    if (formData.password !== formData.password2) {
      setMessage({ type: "error", text: "Passwords do not match!" });
      setLoading(false);
      return;
    }

    try {
      await axios.post(`${API_BASE_URL}/users/register/`, formData);
      setMessage({ type: "success", text: "Account created! Redirecting..." });

      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (error) {
      setMessage({ type: "error", text: error.response?.data?.message || "Registration failed!" });
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="w-full max-w-lg bg-white p-8 rounded-lg shadow-md border">
        <h2 className="text-3xl font-semibold text-center mb-6">Register</h2>

        {message && (
          <div className={`text-center py-2 mb-2 ${message.type === "success" ? "text-green-600" : "text-red-600"}`}>
            {message.text}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block font-medium mb-1">Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              className="border p-2 w-full rounded-md"
            />
          </div>

          <div>
            <label className="block font-medium mb-1">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="border p-2 w-full rounded-md"
            />
          </div>

          <div>
            <label className="block font-medium mb-1">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              className="border p-2 w-full rounded-md"
            />
          </div>

          <div>
            <label className="block font-medium mb-1">Confirm Password</label>
            <input
              type="password"
              name="password2"
              value={formData.password2}
              onChange={handleChange}
              required
              className="border p-2 w-full rounded-md"
            />
          </div>

          <div>
            <label className="block font-medium mb-1">Role</label>
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="border p-2 w-full rounded-md"
            >
              <option value="customer">Customer</option>
              <option value="trader">Trader</option>
              <option value="sales">Sales Representative</option>
            </select>
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-md font-semibold hover:bg-blue-700 transition"
            disabled={loading}
          >
            {loading ? "Registering..." : "Register"}
          </button>
        </form>

        <p className="text-center mt-4">
          Already have an account?{" "}
          <button className="text-blue-500 hover:underline" onClick={() => navigate("/login")}>
            Login
          </button>
        </p>
      </div>
    </div>
  );
};

export default Register;