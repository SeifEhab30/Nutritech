import { useEffect } from "react";
import { useLocation } from "react-router-dom";

const BRAND = "Nutritech";

// Per-route browser tab title (YouTube-style): home is just the brand,
// every other page is "Nutritech - {page}".
const TITLES = {
  "/": null, // home -> brand only
  "/macros-calculator": "Macros Calculator",
  "/meal-planner": "Meal Planner",
  "/food-search": "Food Search",
  "/image-recognition": "Image Recognition",
  "/chatbot": "Chatbot",
  "/login": "Login",
  "/register": "Register",
  "/profile": "Profile",
};

const DocumentTitle = () => {
  const { pathname } = useLocation();

  useEffect(() => {
    const page = TITLES[pathname];
    document.title = page ? `${BRAND} - ${page}` : BRAND;
  }, [pathname]);

  return null;
};

export default DocumentTitle;
