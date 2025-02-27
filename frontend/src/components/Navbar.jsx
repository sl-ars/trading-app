import { Link, useNavigate } from "react-router-dom";
import Notifications from "./notifications/Notifications";

const Navbar = ({ user, setUser }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    navigate("/login");
  };

  return (
    <nav className="bg-white shadow-md py-4 fixed w-full z-50">
      <div className="container mx-auto flex justify-between items-center px-6">
        <Link to="/" className="text-2xl font-bold text-blue-600 hover:text-blue-700 transition">
          TradingApp
        </Link>

        <div className="flex items-center space-x-6">
          {user && <Notifications />}

          <Link to="/browse" className="text-gray-700 hover:text-blue-500 transition">Browse</Link>

          {user ? (
            <>

              {user.role === "trader" && (
                <>
                  <Link to="/products/create" className="text-gray-700 hover:text-blue-500 transition">Create Listing</Link>
                  <Link to="/listings" className="text-gray-700 hover:text-blue-500 transition">My Listings</Link>
                </>
              )}


              {user.role === "customer" && (
                <Link to="/orders" className="text-gray-700 hover:text-blue-500 transition">My Orders</Link>
              )}


              {user.role === "sales_rep" && (
                <Link to="/orders" className="text-gray-700 hover:text-blue-500 transition">Manage Orders</Link>
              )}


              {user.role === "admin" && (
                <>
                  <Link to="/users" className="text-gray-700 hover:text-blue-500 transition">Users</Link>
                  <Link to="/manage-listings" className="text-gray-700 hover:text-blue-500 transition">Manage Listings</Link>
                  <Link to="/orders" className="text-gray-700 hover:text-blue-500 transition">All Orders</Link>
                </>
              )}

              <Link to="/profile" className="text-gray-700 hover:text-blue-500 transition">Profile</Link>
              <button
                onClick={handleLogout}
                className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-gray-700 hover:text-blue-500 transition">Login</Link>
              <Link to="/register" className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;