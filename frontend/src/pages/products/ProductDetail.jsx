import { useState, useEffect } from "react";
import {useParams, useNavigate, redirect} from "react-router-dom";
import axios from "axios";

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const token = localStorage.getItem("access_token");

  const [product, setProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    axios.get(`${API_BASE_URL}/products/${id}/`)
      .then((response) => setProduct(response.data))
      .catch(() => navigate("/"));
  }, [id, navigate]);

  const handleBuyNow = async () => {
    if (!token) {
      navigate("/login");
      return;
    }

    try {
        const response = await axios.post(
          `${API_BASE_URL}/trading/orders/`,
          { product: id, quantity: 1 },
          { headers: { Authorization: `Bearer ${token}` } }
        );

        const orderId = response.data.id;
        const salesOrderId = response.data.sales_order_id;


        const paymentResponse = await axios.post(
          `${API_BASE_URL}/sales/sales-orders/create_payment_session/`,
          { orderId: orderId, salesId: salesOrderId},
          { headers: { Authorization: `Bearer ${token}` } }
        );


        window.location.href = paymentResponse.data.checkout_url;

      } catch (error)
        {

            const errorMessage = error.response?.data?.error || "Failed to create order!";
            setMessage({ type: "error", text: errorMessage });
        }
    };

  if (!product) return <p>Loading...</p>;

  return (
    <div className="container mx-auto p-6">
      <h2 className="text-3xl font-semibold mb-4">{product.title}</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <img src={product.image} alt={product.title} className="w-full h-auto rounded-lg shadow" />

        <div>
          <p className="text-gray-600">{product.description}</p>
          <p className="text-2xl font-bold mt-4">{product.price} ₸</p>

          <div className="mt-4">
            <label className="block text-gray-700">Quantity:</label>
            <input
              type="number"
              min="1"
              max={product.stock}
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className="border p-2 rounded w-20"
            />
          </div>

          {message && <p className={`text-${message.type === "error" ? "red" : "green"}-600 mt-2`}>{message.text}</p>}

          <button
            onClick={handleBuyNow}
            className="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
          >
            Buy Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;