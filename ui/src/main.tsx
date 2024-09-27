import { createBrowserRouter, RouterProvider } from "react-router-dom";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./main.css";
import { Provider } from "react-redux";
import { AlertProvider } from "./components/Alert.tsx";

import store from "./store/store.ts";
import LoginPage from "./components/login/LoginPage.tsx";
import RegisterPage from "./components/register/RegisterPage.tsx";
import ProductsPage from "./components/products/ProductsPage.tsx";
import SellerPage from "./components/seller/SellerPage.tsx";
import MePage from "./components/me/MePage.tsx";
import ShoppingCartPage from "./components/cart/ShoppingCartPage.tsx";

const router = createBrowserRouter([
	{
		path: "/",
		element: <App />,
	},
	{
		path: "/me",
		element: <MePage />,
	},
	{
		path: "/cart",
		element: <ShoppingCartPage />,
	},
	{
		path: "/products/:pid/:lid?",
		element: <ProductsPage />,
	},
	{
		path: "/seller/:id",
		element: <SellerPage />,
	},
	{
		path: "/login",
		element: <LoginPage />,
	},
	{
		path: "/register",
		element: <RegisterPage />,
	},
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
	<Provider store={store}>
		<AlertProvider>
			<RouterProvider router={router} />
		</AlertProvider>
	</Provider>,
);
