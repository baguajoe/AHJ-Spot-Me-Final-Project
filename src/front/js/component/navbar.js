import React from "react";
import { Link, useNavigate } from "react-router-dom";

export const Navbar = () => {
    const navigate = useNavigate();

    // Check if the user is logged in
    const isLoggedIn = !!localStorage.getItem("authToken") || !!localStorage.getItem("token");

    // Sign Out function
    const handleSignOut = () => {
        localStorage.removeItem("authToken"); // Clear the auth token
        localStorage.removeItem("token");
        alert("You have been signed out.");
        navigate("/login"); // Redirect to login page
    };

    return (
        <nav className="navbar navbar-light bg-light">
            <div className="container">
                <Link to="/">
                    <span className="navbar-brand mb-0 h1">Spot Me</span>
                </Link>
                <div className="ml-auto">
                    {isLoggedIn ? (
                        <button onClick={handleSignOut} className="btn btn-secondary">
                            Sign Out
                        </button>
                    ) : (
                        <>
                            <Link to="/login">
                                <button className="btn btn-primary">Login</button>
                            </Link>
                            <Link to="/signup">
                                <button className="btn btn-primary ms-2">Sign Up</button>
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
};
