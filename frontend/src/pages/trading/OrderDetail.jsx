import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";

const OrderDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [message, setMessage] = useState(null);
  const token = localStorage.getItem("access_token");
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  useEffect(() => {
    axios.get(`${API_BASE_URL}/trading/orders/${id}/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    .then(response => setOrder(response.data))
    .catch(error => console.error("Failed to fetch order:", error));
  }, [id]);

  const handleCancel = async () => {
    try {
      await axios.post(`${API_BASE_URL}/trading/orders/${id}/cancel/`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage({ type: "success", text: "Order cancelled successfully!" });
      setTimeout(() => navigate("/orders"), 2000);
    } catch (error) {
      setMessage({ type: "error", text: "Failed to cancel order." });
    }
  };

  if (!order) return <p>Loading order details...</p>;

  return (
    <div className="container mx-auto p-6">
      <h2 className="text-3xl font-semibold mb-4">Order Details</h2>
      {message && <p className={`text-${message.type === "success" ? "green" : "red"}-500`}>{message.text}</p>}
      <div className="bg-white p-6 shadow-md rounded-lg">
        <img src={order.product.image} alt={order.product.title} className="w-full h-64 object-cover rounded-md mb-4" />
        <h3 className="text-xl font-semibold">{order.product.title}</h3>
        <p>Quantity: {order.quantity}</p>
        <p>Total Price: {order.total_price} KZT</p>
        <p>Status: <span className={`font-semibold ${order.status === "pending" ? "text-yellow-500" : "text-green-600"}`}>{order.status}</span></p>
        {order.status === "pending" && (
          <button onClick={handleCancel} className="bg-red-500 text-white px-4 py-2 rounded mt-4">
            Cancel Order
          </button>
        )}
      </div>
    </div>
  );
};

export default OrderDetail;