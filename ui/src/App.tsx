import { useEffect, useState } from "react";
import styled from "styled-components";
import { useAppSelector } from "./hooks.ts";
import Header from "./shared/Header.tsx";
import { Link } from "react-router-dom";
import Client from "./shared/client/client.tsx";
import Card from "./shared/Card.tsx";

const ProductsWrapper = styled.div`
	width: 100%;
	margin: auto;

	display: grid;
	grid-template-columns: auto auto auto auto;
	justify-content: space-around;
	gap: 5%;
`;

export interface Product {
	category: string;
	description: string;
	id: string;
	image_src: string;
	name: string;
}

export default function App() {
	const access_token = useAppSelector((s) => s.user.access_token);
	const client = new Client(access_token);

	const [products, setProducts] = useState<Product[]>([]);

	useEffect(() => {
		client
			.post("http://localhost:5000/products", { offset: 0, limit: 10 })
			.then((r) => {
				setProducts(r.data as Product[]);
			});
	}, []);

	return (
		<>
			<Header />

			<ProductsWrapper>
				{products?.map((product) => {
					return (
						<Card key={product.id}>
							<Link to={`/products/${product.id}`}>
								<img height="250px" width="250px" src={product.image_src} />
								<p>{product.name}</p>
							</Link>
						</Card>
					);
				})}
			</ProductsWrapper>
		</>
	);
}
