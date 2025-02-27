import { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const TraderOrders = () => {
  const [orders, setOrders] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [statusFilter, setStatusFilter] = useState("");
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const token = localStorage.getItem("access_token");

  useEffect(() => {
    fetchOrders();
  }, [statusFilter]);

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/trading/orders/`, {
        headers: { Authorization: `Bearer ${token}` },
        params: statusFilter ? { status: statusFilter } : {},
      });
      setOrders(response.data.results);
    } catch (error) {
      console.error("Failed to fetch trader orders:", error);
    }
  };

  const handleStatusChange = async (orderId, newStatus) => {
    try {
      await axios.post(`${API_BASE_URL}/trading/orders/${orderId}/${newStatus}/`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchOrders();
    } catch (error) {
      console.error("Failed to update order status:", error);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <h2 className="text-3xl font-semibold mb-6">Trader Orders</h2>

      {/* Status Filter */}
      <div className="mb-4">
        <label className="mr-2">Filter by Status:</label>
        <select
          className="border p-2 rounded"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="shipped">Shipped</option>
        </select>
      </div>

      {orders.length > 0 ? (
        <ul>
          {orders.map((order) => (
            <li key={order.id} className="border p-4 mb-2 rounded shadow-md">
              <div className="flex justify-between items-center">
                  <div>
                      <p className="text-lg font-semibold">Order #{order.id} - {order.status}</p>
                      <p><span className="font-semibold">Product:</span> {order.product.title}</p>
                      <p><span className="font-semibold">Quantity:</span> {order.quantity}</p>
                      <p><span className="font-semibold">Total Price:</span> {order.total_price} ₸</p>
                      <p><span className="font-semibold">Customer:</span> {order.user.username} ({order.user.email})</p>

                  </div>

                  {/* View Details Button */}
                  <button
                      className="bg-gray-500 text-white px-3 py-1 rounded-lg hover:bg-gray-600 transition mr-2"
                  onClick={() => setSelectedOrder(order.id === selectedOrder ? null : order.id)}
                >
                  {selectedOrder === order.id ? "Hide Details" : "View Details"}
                </button>
              </div>

              {/* Order Details */}
              {selectedOrder === order.id && (
                <div className="mt-4 border-t pt-4">
                  <h3 className="text-lg font-semibold">Order Details</h3>
                  <p><span className="font-semibold">Order Date:</span> {order.created_at}</p>
                  <p><span className="font-semibold">Payment Status:</span> {order.payment_status}</p>

                  {/* View Product Button */}
                  <button
                    className="bg-blue-500 text-white px-3 py-1 rounded-lg hover:bg-blue-600 transition mt-2"
                    onClick={() => setSelectedProduct(order.product.id === selectedProduct ? null : order.product.id)}
                  >
                    {selectedProduct === order.product.id ? "Hide Product Details" : "View Product"}
                  </button>

                  {/* Product Details */}
                  {selectedProduct === order.product.id && (
                    <div className="mt-4 border-t pt-4">
                      <h3 className="text-lg font-semibold">{order.product.title}</h3>
                      <p>{order.product.description}</p>
                      <img src={order.product.image} alt={order.product.title} className="w-32 h-32 object-cover rounded mt-2" />
                      <div className="mt-2">
                        <Link
                          to={`/products/${order.product.id}`}
                          className="bg-blue-500 text-white px-3 py-1 rounded-lg hover:bg-blue-600 transition"
                        >
                          View Product Page
                        </Link>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Approve, Reject, and Ship Buttons */}
              {order.status === "pending" && (
                <div className="mt-4 flex gap-4">
                  <button
                    className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition"
                    onClick={() => handleStatusChange(order.id, "approve")}
                  >
                    Approve
                  </button>
                  <button
                    className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
                    onClick={() => handleStatusChange(order.id, "reject")}
                  >
                    Reject
                  </button>
                </div>
              )}

              {order.status === "paid" && (
                <div className="mt-4">
                  <button
                    className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600 transition"
                    onClick={() => handleStatusChange(order.id, "ship")}
                  >
                    Ship Order
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p>No orders found.</p>
      )}
    </div>
  );
};

export default TraderOrders;