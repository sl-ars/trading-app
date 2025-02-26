import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

const MainPage = () => {
  const [categories, setCategories] = useState([]);
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [latestProducts, setLatestProducts] = useState([]);

  useEffect(() => {
    axios.get(`${import.meta.env.VITE_API_BASE_URL}/products/categories/`)
      .then(response => setCategories(response.data))
      .catch(error => console.error("Error loading categories:", error));

    axios.get(`${import.meta.env.VITE_API_BASE_URL}/products/featured/`)
      .then(response => setFeaturedProducts(response.data))
      .catch(error => console.error("Error loading featured products:", error));

    axios.get(`${import.meta.env.VITE_API_BASE_URL}/products/latest/`)
      .then(response => setLatestProducts(response.data))
      .catch(error => console.error("Error loading latest products:", error));
  }, []);

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="text-center bg-blue-500 text-white py-10 rounded-lg shadow-md">
        <h1 className="text-4xl font-bold">Welcome to Trading App</h1>
        <p className="text-lg mt-2">Buy and Sell Products Easily</p>
        <Link to="/products" className="mt-4 inline-block bg-white text-blue-600 px-6 py-3 rounded-md shadow-md">
          Browse Listings
        </Link>
      </div>

      {/* Categories */}
      <div className="my-10">
        <h2 className="text-2xl font-semibold text-center">Categories</h2>
        <div className="flex flex-wrap justify-center gap-4 mt-4">
          {categories.map(category => (
            <Link key={category.id} to={`/products?category=${category.id}`}
              className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-md shadow-md">
              {category.name}
            </Link>
          ))}
        </div>
      </div>

      {/* Featured Products */}
      <div className="my-10">
        <h2 className="text-2xl font-semibold text-center">Featured Listings</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
          {featuredProducts.map(product => (
            <div key={product.id} className="bg-white shadow-md rounded-md overflow-hidden">
              <img src={product.image || "/no_image.png"} className="w-full h-48 object-cover" alt={product.title} />
              <div className="p-4">
                <h3 className="text-lg font-semibold">{product.title}</h3>
                <p className="text-blue-600 font-bold">{product.price} ₸</p>
                <Link to={`/products/${product.id}`} className="text-blue-500 hover:underline">View Details</Link>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Latest Listings */}
      <div className="my-10">
        <h2 className="text-2xl font-semibold text-center">Latest Listings</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
          {latestProducts.map(product => (
            <div key={product.id} className="bg-white shadow-md rounded-md overflow-hidden">
              <img src={product.image || "/no_image.png"} className="w-full h-48 object-cover" alt={product.title} />
              <div className="p-4">
                <h3 className="text-lg font-semibold">{product.title}</h3>
                <p className="text-blue-600 font-bold">{product.price} ₸</p>
                <Link to={`/products/${product.id}`} className="text-blue-500 hover:underline">View Details</Link>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};

export default MainPage;