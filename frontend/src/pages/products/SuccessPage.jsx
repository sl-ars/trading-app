import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";

const SuccessPage = () => {
  const { orderId } = useParams();
  const [paymentStatus, setPaymentStatus] = useState(null);
  const navigate = useNavigate();
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const token = localStorage.getItem("access_token");

  useEffect(() => {
    const checkPaymentStatus = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/sales/sales-orders/${orderId}/`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (response.data.status === "paid") {
          setPaymentStatus("success");
        } else {
          setPaymentStatus("failed");
        }
      } catch (error) {
        setPaymentStatus("failed");
        console.error("Error verifying payment:", error);
      }
    };

    checkPaymentStatus();

    // Auto-redirect back to My Orders after 5 seconds
    const timer = setTimeout(() => navigate("/orders"), 5000);
    return () => clearTimeout(timer);
  }, [orderId, navigate, API_BASE_URL, token]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      {paymentStatus === "success" ? (
        <div className="bg-green-100 text-green-700 p-6 rounded-lg shadow-lg">
          <h2 className="text-3xl font-bold mb-4">Payment Successful!</h2>
          <p>Your order #{orderId} has been successfully paid.</p>
          <p>Thank you for your purchase!</p>
        </div>
      ) : paymentStatus === "failed" ? (
        <div className="bg-red-100 text-red-700 p-6 rounded-lg shadow-lg">
          <h2 className="text-3xl font-bold mb-4">Payment Failed</h2>
          <p>Something went wrong. Your payment was not completed.</p>
          <p>Please try again or contact support.</p>
        </div>
      ) : (
        <p>Checking payment status...</p>
      )}
    </div>
  );
};

export default SuccessPage;