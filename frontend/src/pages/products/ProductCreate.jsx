import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const ProductCreate = () => {
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
  const [message, setMessage] = useState(null);

  useEffect(() => {
    axios
      .get(`${API_BASE_URL}/products/categories/`)
      .then((response) => setCategories(response.data))
      .catch(() => setCategories([]));
  }, []);

  const handleChange = (e) => {
    setProduct({ ...product, [e.target.name]: e.target.value });
  };

  const handleCategoryChange = (e) => {
    setProduct({ ...product, category: e.target.value });
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
    if (product.image) {
      formData.append("image", product.image);
    }

    axios
      .post(`${API_BASE_URL}/products/`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      })
      .then(() => {
        setMessage({ type: "success", text: "Product created successfully!" });
        setTimeout(() => navigate("/listings"), 2000);
      })
      .catch(() => {
        setMessage({ type: "error", text: "Failed to create product" });
      });
  };

  return (
    <div className="container mx-auto p-6">
      <h2 className="text-3xl font-semibold mb-6">Create Product</h2>
      <form onSubmit={handleSubmit} className="bg-white p-6 shadow-md rounded-lg">
        <input type="text" name="title" placeholder="Title" className="border p-2 w-full mb-4" onChange={handleChange}
               required/>
        <textarea name="description" placeholder="Description" className="border p-2 w-full mb-4"
                  onChange={handleChange} required/>
        <input type="number" name="price" placeholder="Price" className="border p-2 w-full mb-4" onChange={handleChange}
               required/>
        <input type="number" name="stock" placeholder="Stock" className="border p-2 w-full mb-4" onChange={handleChange}
               required/>
        <select
            name="category"
            className="border p-2 w-full mb-4"
            onChange={handleCategoryChange}
            required
        >
          <option value="">Select Category</option>
          {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
          ))}
        </select>
        <input type="file" name="image" className="border p-2 w-full mb-4" onChange={handleImageChange}/>
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded w-full">Create</button>
      </form>
    </div>
  );
};

export default ProductCreate;