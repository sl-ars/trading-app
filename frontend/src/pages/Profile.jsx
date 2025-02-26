import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const Profile = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const [user, setUser] = useState({});
  const [editMode, setEditMode] = useState(null);
  const [updatedData, setUpdatedData] = useState({});
  const [message, setMessage] = useState(null);

  useEffect(() => {
    if (!token) {
      navigate("/login", { replace: true });
    }

    axios
      .get(`${API_BASE_URL}/users/profile/`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((response) => {
        setUser(response.data);
        setUpdatedData({
          first_name: response.data.first_name || "",
          last_name: response.data.last_name || "",
          phone_number: response.data.phone_number || "",
          avatar: null,
        });
      })
      .catch(() => navigate("/login", { replace: true }));
  }, [token, navigate]);

  const handleEdit = (field) => setEditMode(field);

  const handleSave = (field) => {
  const formData = new FormData();

  if (field === "avatar" && updatedData.avatar) {
    formData.append("avatar", updatedData.avatar);
    axios
      .patch(`${API_BASE_URL}/users/profile/avatar/`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      })
      .then((response) => {
        setUser((prev) => ({ ...prev, avatar_url: response.data.avatar_url }));
        setEditMode(null);
        setMessage({ type: "success", text: "Avatar updated successfully!" });

        setTimeout(() => setMessage(null), 3000);
      })
      .catch(() => {
        setMessage({ type: "error", text: "Failed to update avatar!" });
      });
  } else {
    formData.append(field, updatedData[field]);
    axios
      .patch(`${API_BASE_URL}/users/profile/update/`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then((response) => {
        setUser((prev) => ({ ...prev, [field]: response.data.updated_fields[field] }));
        setEditMode(null);
        setMessage({ type: "success", text: "Profile updated successfully!" });

        setTimeout(() => setMessage(null), 3000);
      })
      .catch(() => {
        setMessage({ type: "error", text: "Failed to update profile!" });
      });
  }
};

  return (
    <div className="container mx-auto px-6 pt-16">
      <h2 className="text-3xl font-semibold mb-6">Profile</h2>

      {message && (
        <div className={`text-center py-2 mb-2 ${message.type === "success" ? "text-green-600" : "text-red-600"}`}>
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

        <div className="flex flex-col items-center bg-white p-6 rounded-lg shadow border">
          {user.avatar_url ? (
            <img src={user.avatar_url} alt="Profile" className="w-32 h-32 rounded-full mb-4 border" />
          ) : (
            <div className="w-32 h-32 bg-gray-200 rounded-full mb-4 flex items-center justify-center">
              <span className="text-gray-500">No Image</span>
            </div>
          )}

          {editMode === "avatar" ? (
            <div className="flex flex-col gap-2">
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setUpdatedData({ ...updatedData, avatar: e.target.files[0] })}
                className="text-sm"
              />
              <button className="bg-green-500 text-white px-4 py-2 rounded" onClick={() => handleSave("avatar")}>
                Save
              </button>
            </div>
          ) : (
            <button className="text-blue-500" onClick={() => handleEdit("avatar")}>
              Change Avatar
            </button>
          )}
        </div>


        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-xl font-semibold mb-4">Personal Info</h3>
          {[
            { key: "first_name", label: "First Name" },
            { key: "last_name", label: "Last Name" },
            { key: "phone_number", label: "Phone Number" },
          ].map(({ key, label }) => (
            <div key={key} className="mb-4">
              <p className="font-medium">{label}:</p>
              {editMode === key ? (
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={updatedData[key]}
                    onChange={(e) => setUpdatedData({ ...updatedData, [key]: e.target.value })}
                    className="border p-2 w-full rounded-md"
                  />
                  <button className="bg-green-500 text-white px-3 py-1 rounded" onClick={() => handleSave(key)}>
                    Save
                  </button>
                </div>
              ) : (
                <div className="flex justify-between">
                  <p>{user[key] || "Not set"}</p>
                  <button className="text-blue-500" onClick={() => handleEdit(key)}>
                    Edit
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>


      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">

        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-xl font-semibold mb-4">Account Info</h3>
          <p><span className="font-medium">Username:</span> {user.username}</p>
          <p><span className="font-medium">Email:</span> {user.email}</p>
          <p><span className="font-medium">Role:</span> {user.role}</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-xl font-semibold mb-4">Balance</h3>
          <p className="text-2xl font-bold">{user.balance || "0.00"} ₸</p>
          <button className="mt-4 bg-blue-500 text-white px-4 py-2 rounded w-full">
            Top Up Balance
          </button>
        </div>
      </div>
    </div>
  );
};

export default Profile;