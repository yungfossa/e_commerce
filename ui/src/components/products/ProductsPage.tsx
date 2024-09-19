import { React, useEffect, useState } from "react";
import styled from "styled-components";
import { useAppDispatch, useAppSelector } from "../../hooks.ts";
import { useParams } from "react-router-dom";
import Header from "../../shared/Header.tsx";
import { Link } from "react-router-dom";

const ListingsWrapper = styled.div`
`;

export default function ProductsPage() {
	let { id } = useParams();

	const access_token = useAppSelector((s) => s.user.access_token);
	const [product, setProduct] = useState<any>(null);

	useEffect(() => {
		if (access_token === "") {
			return;
		}

		fetch(`http://localhost:5000/products/${id}`, {
			headers: {
				Authorization: `Bearer ${access_token}`,
			},
		})
			.then((r) => r.json())
			.then((r) => {
				setProduct(r.data);
			});
	}, [access_token]);

	if (product === null) {
		return "Loading...";
	}

	return (
		<>
			<Header />

			<p>{product.name}</p>
			<p>{product.category.name}</p>
			<img height="250px" width="250px" src={product.image_src} />

			<ul>
				{product &&
					product.listings.map((l) => {
						return (
							<ListingsWrapper>
								<Link to={`/products/${id}/${l.id}`}>
									<p>{l.seller.name}</p>
									<p>only {l.quantity} left</p>
									<p>{l.price} dolla</p>
								</Link>
							</ListingsWrapper>
						);
					})}
			</ul>
		</>
	);
}
