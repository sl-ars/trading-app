import { useEffect, useState, useRef } from "react";
import axios from "axios";

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const notifRef = useRef(null);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const WSS_BASE_URL = import.meta.env.VITE_WSS_BASE_URL;
  const token = localStorage.getItem("access_token");

  const wsUrl = token ? `${WSS_BASE_URL}/notifications/?token=${token}` : null;
  const notificationSound = "/sounds/notification.mp3"; // FIXED sound path

  useEffect(() => {
    if (!wsUrl) return;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => console.log("WebSocket Connected");

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.notification && data.notification.message) {
          playNotificationSound();
          setNotifications((prev) => [data.notification, ...prev]);
          setUnreadCount((prev) => prev + 1);
        }
      } catch (error) {
        console.error("WebSocket Message Error:", error);
      }
    };

    ws.onclose = (event) => console.log("WebSocket Closed", event.reason);
    ws.onerror = (error) => console.error("WebSocket Error:", error);

    return () => {
      if (ws) ws.close();
    };
  }, [wsUrl]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (notifRef.current && !notifRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const playNotificationSound = () => {
    const audio = new Audio(notificationSound);
    audio.play().catch((err) => console.error("Audio Play Failed", err));
  };

  const toggleNotifications = async () => {
    setShowNotifications((prev) => !prev);

    if (!showNotifications) {
      setUnreadCount(0);
      try {
        await axios.post(`${API_BASE_URL}/notifications/mark_as_read/`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } catch (error) {
        console.error("Error marking notifications as read:", error);
      }
    }
  };

  return (
    <div className="relative" ref={notifRef}>
      <button className="relative text-gray-700 hover:text-blue-500 transition" onClick={toggleNotifications}>
        🔔
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-2 bg-red-500 text-white text-xs px-1 rounded-full">
            {unreadCount}
          </span>
        )}
      </button>

      {showNotifications && (
        <div className="absolute bg-white shadow-md rounded-lg p-4 mt-2 right-0 w-64 border z-50">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-sm font-semibold">Notifications</h3>
            <button className="text-xs text-gray-500 hover:text-red-500" onClick={() => setNotifications([])}>
              Clear
            </button>
          </div>
          <div className="max-h-48 overflow-y-auto">
            {notifications.length > 0 ? (
              notifications.map((notif, index) => (
                <p key={index} className="text-sm text-gray-700 border-b py-1">
                  {notif.message} {/* FIXED: Access message properly */}
                </p>
              ))
            ) : (
              <p className="text-sm text-gray-500">No new notifications</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Notifications;