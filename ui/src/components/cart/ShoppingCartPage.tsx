import { React, useEffect, useState } from "react";
import Header from "../../shared/Header";
import { useAppSelector } from "../../hooks";
import Client from "../../shared/client/client";
import styled from "styled-components";
import { Link } from "react-router-dom";

const Wrapper = styled.div`
`;

const ProductWrapper = styled.div`
`;

export default function CartPage() {
	const access_token = useAppSelector((s) => s.user.access_token);
	const client = new Client(access_token);

	const [cart, setCart] = useState<any>(null);

	useEffect(() => {
		client.get("http://localhost:5000/cart").then((r) => {
			setCart(r.data);
		});
	}, []);

	return (
		<>
			<Header />

			<Wrapper>
				{cart?.cart_entries.map((cart_entry) => {
					return (
						<ProductWrapper key={cart_entry.product_id}>
							<Link to={`/${cart_entry.product_id}/${cart_entry.listing_id}`}>
								{cart_entry.product_name}
							</Link>
						</ProductWrapper>
					);
				})}
			</Wrapper>
		</>
	);
}
