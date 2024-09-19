import { useContext, useEffect, useState } from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheckCircle } from "@fortawesome/free-regular-svg-icons";
import { useAppDispatch, useAppSelector } from "./hooks.ts";
import { authenticate } from "./store/user.ts";
import AlertContext from "./components/Alert.tsx";
import Header from "./shared/Header.tsx";
import { Link } from "react-router-dom";

const ProductsWrapper = styled.div`
	display: grid;
	grid-template-columns: auto auto auto auto auto;

	padding: 100px;
`;

const ProductWrapper = styled.div`
`;

function App() {
	const access_token = useAppSelector((s) => s.user.access_token);
	const [products, setProducts] = useState<any[]>([]);

	useEffect(() => {
		if (access_token === "") {
			return;
		}

		fetch("http://localhost:5000/products", {
			method: "POST",
			headers: {
				Authorization: `Bearer ${access_token}`,
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ offset: 0, limit: 10 }),
		})
			.then((r) => r.json())
			.then((r) => {
				setProducts(r.data);
			});
	}, [access_token]);

	return (
		<>
			<Header />

			<ProductsWrapper>
				{products &&
					products.map((product) => {
						return (
							<ProductWrapper>
								<Link to={`/products/${product.id}`}>
									<img height="250px" width="250px" src={product.image_src} />
									<p>{product.name}</p>
									<p>{product.category.name}</p>
								</Link>
							</ProductWrapper>
						);
					})}
			</ProductsWrapper>
		</>
	);
}

export default App;
