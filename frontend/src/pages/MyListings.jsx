import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

const MyListings = () => {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);
  const [categories, setCategories] = useState([]);
  const [filters, setFilters] = useState({
    category: "",
    minPrice: "",
    maxPrice: "",
  });

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const token = localStorage.getItem("access_token");

  useEffect(() => {
    fetchListings();
    fetchCategories();
  }, [filters]);

  const fetchListings = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/products/my_listings/`, {
        headers: { Authorization: `Bearer ${token}` },
        params: filters,
      });
      setListings(response.data);
    } catch (error) {
      setMessage({ type: "error", text: "Failed to fetch listings" });
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/products/categories/`);
      setCategories(response.data);
    } catch (error) {
      console.error("Error fetching categories:", error);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this listing?")) return;

    try {
      await axios.delete(`${API_BASE_URL}/products/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setListings((prev) => prev.filter((listing) => listing.id !== id));
      setMessage({ type: "success", text: "Listing deleted successfully" });
    } catch (error) {
      setMessage({ type: "error", text: "Failed to delete listing" });
    }
  };

  return (
    <div className="container mx-auto px-6 pt-16">
      <h2 className="text-3xl font-semibold mb-6">My Listings</h2>

      {message && (
        <div className={`text-center py-2 mb-4 ${message.type === "success" ? "text-green-600" : "text-red-600"}`}>
          {message.text}
        </div>
      )}

      <div className="flex justify-between mb-4">
        <Link to="/products/create" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
          + Add New Listing
        </Link>
        <Link to="/trader/orders" className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition">
          View Orders
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-4">
        <select
          value={filters.category}
          onChange={(e) => setFilters({ ...filters, category: e.target.value })}
          className="border p-2 rounded"
        >
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>

        <input
          type="number"
          placeholder="Min Price"
          value={filters.minPrice}
          onChange={(e) => setFilters({ ...filters, minPrice: e.target.value })}
          className="border p-2 rounded"
        />
        <input
          type="number"
          placeholder="Max Price"
          value={filters.maxPrice}
          onChange={(e) => setFilters({ ...filters, maxPrice: e.target.value })}
          className="border p-2 rounded"
        />
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : listings.length === 0 ? (
        <p>No listings found.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {listings.map((listing) => (
            <div key={listing.id} className="bg-white shadow-md rounded-lg p-4">
              <img src={listing.image} alt={listing.title} className="w-full h-40 object-cover rounded-md mb-4" />
              <h3 className="text-lg font-semibold">{listing.title}</h3>
              <p className="text-gray-700">{listing.price} ₸</p>
              <div className="flex justify-between mt-4">
                <Link to={`/products/${listing.id}`} className="bg-blue-500 text-white px-3 py-1 rounded-lg hover:bg-blue-600 transition">
                  View
                </Link>
                <Link to={`/products/edit/${listing.id}`} className="bg-yellow-500 text-white px-3 py-1 rounded-lg hover:bg-yellow-600 transition">
                  Edit
                </Link>
                <button onClick={() => handleDelete(listing.id)} className="bg-red-500 text-white px-3 py-1 rounded-lg hover:bg-red-600 transition">
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyListings;