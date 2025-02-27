import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";

const ProductEdit = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const token = localStorage.getItem("access_token");

  const [product, setProduct] = useState({
    title: "",
    description: "",
    price: "",
    stock: "",
    category: "",
    image: null,
  });

  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);

  // Загружаем продукт и категории
  useEffect(() => {
    axios
      .get(`${API_BASE_URL}/products/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((response) => {
        setProduct(response.data);
        setLoading(false);
      })
      .catch(() => {
        setMessage({ type: "error", text: "Failed to load product" });
        setLoading(false);
      });

    axios
      .get(`${API_BASE_URL}/products/categories/`)
      .then((response) => setCategories(response.data))
      .catch(() => setCategories([]));
  }, [id, token]);

  const handleChange = (e) => {
    setProduct({ ...product, [e.target.name]: e.target.value });
  };

  const handleImageChange = (e) => {
    setProduct({ ...product, image: e.target.files[0] });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("title", product.title);
    formData.append("description", product.description);
    formData.append("price", product.price);
    formData.append("stock", product.stock);
    formData.append("category", product.category);
    if (product.image instanceof File) {
      formData.append("image", product.image);
    }

    axios
      .patch(`${API_BASE_URL}/products/${id}/`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      })
      .then(() => {
        setMessage({ type: "success", text: "Product updated successfully!" });
        setTimeout(() => navigate("/listings"), 2000);
      })
      .catch((error) => {
        setMessage({
          type: "error",
          text: error.response?.data?.message || "Failed to update product",
        });
      });
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div className="container mx-auto px-6 py-16">
      <h2 className="text-3xl font-semibold mb-6">Edit Product</h2>

      {message && (
        <div className={`text-center py-2 mb-4 ${message.type === "success" ? "text-green-600" : "text-red-600"}`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md space-y-4">
        <div>
          <label className="block font-medium">Title</label>
          <input type="text" name="title" value={product.title} onChange={handleChange} className="w-full p-2 border rounded" />
        </div>

        <div>
          <label className="block font-medium">Description</label>
          <textarea name="description" value={product.description} onChange={handleChange} className="w-full p-2 border rounded" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block font-medium">Price (₸)</label>
            <input type="number" name="price" value={product.price} onChange={handleChange} className="w-full p-2 border rounded" />
          </div>

          <div>
            <label className="block font-medium">Stock</label>
            <input type="number" name="stock" value={product.stock} onChange={handleChange} className="w-full p-2 border rounded" />
          </div>
        </div>

        <div>
          <label className="block font-medium">Category</label>
          <select name="category" value={product.category} onChange={handleChange} className="w-full p-2 border rounded">
            <option value="">Select a category</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block font-medium">Product Image</label>
          <input type="file" accept="image/*" onChange={handleImageChange} className="w-full" />
        </div>

        <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition">
          Save Changes
        </button>
      </form>
    </div>
  );
};

export default ProductEdit;