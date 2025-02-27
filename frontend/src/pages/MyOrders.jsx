import { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const MyOrders = () => {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const token = localStorage.getItem("access_token");

  const [orders, setOrders] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchOrders();
  }, [currentPage, statusFilter]);

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/trading/orders/`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { page: currentPage, status: statusFilter },
      });
      setOrders(response.data.results);
      setTotalPages(Math.ceil(response.data.count / 10));
    } catch (error) {
      console.error("Error fetching orders:", error.response?.data || error.message);
    }
  };

  const handleCancelOrder = async (orderId) => {
    if (!window.confirm("Are you sure you want to cancel this order?")) return;
    try {
      await axios.post(`${API_BASE_URL}/trading/orders/${orderId}/cancel/`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      fetchOrders();
    } catch (error) {
      console.error("Failed to cancel order:", error);
    }
  };

  const handlePayment = async (orderId) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/sales/sales-orders/create_payment_session/`,
        { orderId: orderId },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      } else {
        console.error("No checkout URL received:", response.data);
      }
    } catch (error) {
      console.error("Payment session creation failed:", error);
    }
  };

  const generateInvoice = async (salesOrderId) => {
    try {
      await axios.post(
        `${API_BASE_URL}/sales/invoices/`,
        { sales_order: salesOrderId },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      alert("Invoice is being generated! Refresh the page in a few moments.");
    } catch (error) {
      console.error("Failed to generate invoice:", error.response?.data || error.message);
      alert("Failed to generate invoice.");
    }
  };

    const downloadInvoice = async (url) => {
      try {
        if (url) {
          window.open(url, "_blank");
        } else {
          console.error("No download URL received:", url);
        }
      } catch (error) {
        console.error("Failed to fetch invoice download URL:", error.response?.data || error.message);
        alert("Failed to fetch invoice.");
      }
    };

  return (
    <div className="container mx-auto p-6">
      <h2 className="text-3xl font-semibold mb-6">My Orders</h2>

      {/* Status Filter */}
      <div className="mb-4 flex items-center gap-4">
        <label className="mr-2 font-semibold">Filter by Status:</label>
        <select
          className="border p-2 rounded"
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setCurrentPage(1);
          }}
        >
          <option value="">All</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="shipped">Shipped</option>
          <option value="paid">Paid</option>
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
                </div>
              )}

              {/* Cancel, Pay Now, and Invoice Buttons */}
              <div className="mt-4 flex gap-4">
                {order.status === "pending" && (
                  <button
                    className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
                    onClick={() => handleCancelOrder(order.id)}
                  >
                    Cancel Order
                  </button>
                )}
                {order.sales_order?.status !== "paid" && order.status === "approved" && (
                  <button
                    className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition"
                    onClick={() => handlePayment(order.id)}
                  >
                    Pay Now
                  </button>
                )}
                {order.sales_order?.status === "paid" && (
                  order.sales_order.invoice ? (
                    <button
                      className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600 transition"
                      onClick={() => downloadInvoice(order.sales_order.invoice.pdf_file)}
                    >
                      Download Invoice
                    </button>
                  ) : (
                    <button
                      className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
                      onClick={() => generateInvoice(order.sales_order.id)}
                    >
                      Generate Invoice
                    </button>
                  )
                )}
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p>No orders found.</p>
      )}

      {/* Pagination */}
      <div className="flex justify-center mt-6">
        <button
          onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
          disabled={currentPage === 1}
          className={`px-4 py-2 mx-2 ${currentPage === 1 ? "bg-gray-300" : "bg-blue-500 text-white"} rounded-lg`}
        >
          Previous
        </button>

        <span className="px-4 py-2">Page {currentPage} of {totalPages}</span>

        <button
          onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
          disabled={currentPage === totalPages}
          className={`px-4 py-2 mx-2 ${currentPage === totalPages ? "bg-gray-300" : "bg-blue-500 text-white"} rounded-lg`}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default MyOrders;