import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import ProductList from "./pages/products/ProductList.jsx";
import ProductDetail from "./pages/products/ProductDetail.jsx";
import ProductCreate from "./pages/products/ProductCreate.jsx";
import MyListings from "./pages/MyListings";
import ProductEdit from "./pages/products/ProductEdit.jsx";
import MyOrders from "./pages/MyOrders";
import OrderDetail from "./pages/trading/OrderDetail";
import TraderOrders from "./pages/trading/TraderOrders";
import SuccessPage  from "./pages/products/SuccessPage.jsx";

import axios from "axios";

function App() {
  const [user, setUser] = useState(null);
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
  const token = localStorage.getItem("access_token");

  useEffect(() => {
    const fetchUser = async () => {
      if (!token) return setUser(null);
      try {
        const response = await axios.get(`${API_BASE_URL}/users/profile/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setUser(response.data);
      } catch (error) {
        setUser(null);
      }
    };
    fetchUser();
  }, [token]);

  return (
    <Router>
      <Navbar user={user} setUser={setUser} />
      <Routes>
        <Route path="/login" element={<Login setUser={setUser} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<ProductList />} />
        <Route path="/browse" element={<ProductList />} />
        <Route path="/products/:id" element={<ProductDetail />} />

        <Route path="/profile" element={token ? <Profile /> : <Navigate to="/login" />} />
        <Route path="/products/create" element={user?.role === "trader" ? <ProductCreate /> : <Navigate to="/" />} />
        <Route path="/products/edit/:id" element={<ProductEdit />} />

         <Route path="/listings" element={<MyListings />} />

        <Route path="/orders/:id/success/" element={<SuccessPage />} />
        <Route path="/orders" element={<MyOrders />} />
        <Route path="/orders/:id" element={<OrderDetail />} />
        <Route path="/trader/orders" element={<TraderOrders />} />
      </Routes>
    </Router>
  );
}

export default App;