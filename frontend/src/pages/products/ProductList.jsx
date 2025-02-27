import { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const ProductList = () => {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const [products, setProducts] = useState([]);
  const [nextPage, setNextPage] = useState(null);
  const [prevPage, setPrevPage] = useState(null);

  const fetchProducts = async (url) => {
    try {
      const response = await axios.get(url);
      setProducts(response.data.results);
      setNextPage(response.data.next);
      setPrevPage(response.data.previous);
    } catch (error) {
      console.error("Error fetching products:", error);
    }
  };

  useEffect(() => {
    fetchProducts(`${API_BASE_URL}/products/`);
  }, []);

  return (
    <div className="container mx-auto p-6">
      <h2 className="text-3xl font-semibold mb-6">Products</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {products.map((product) => (
          <div key={product.id} className="bg-white shadow-md p-4 rounded-lg">
            {product.image && (
              <img
                src={product.image}
                alt={product.title}
                className="w-full h-40 object-cover mb-4 rounded"
              />
            )}
            <h3 className="text-xl font-semibold">{product.title}</h3>
            <p className="text-gray-500">{product.price} ₸</p>
            <Link to={`/products/${product.id}`} className="text-blue-500 mt-2 block">
              View Details
            </Link>
          </div>
        ))}
      </div>

      <div className="flex justify-between mt-6">
        {prevPage && (
          <button
            onClick={() => fetchProducts(prevPage)}
            className="bg-gray-500 text-white px-4 py-2 rounded"
          >
            Previous
          </button>
        )}
        {nextPage && (
          <button
            onClick={() => fetchProducts(nextPage)}
            className="bg-blue-500 text-white px-4 py-2 rounded"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
};

export default ProductList;