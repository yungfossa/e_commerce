import { useEffect, useState } from "react";
import Header from "../../shared/Header";
import { useAppSelector } from "../../hooks";
import Client from "../../shared/client/client";
import styled from "styled-components";
import { Link } from "react-router-dom";
import Button from "../../shared/input/Button";

const Wrapper = styled.div`
`;

const ProductWrapper = styled.div`
`;

interface Address {
	street: string;
	city: string;
	state: string;
	country: string;
	postal_code: string;
}

function checkout(client, address: Address) {
	return () => {
		client.post("http://localhost:5000/orders", {
			address_street: address.street,
			address_city: address.city,
			address_state: address.state,
			address_country: address.country,
			address_postal_code: address.postal_code,
		});
	};
}

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
			{cart?.cart_total} dolla
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
				<Button
					text="checkout"
					onClick={checkout(client, {
						street: "Via Arba 1",
						city: "Tesis di Vivaro",
						state: "Italy",
						country: "Italy",
						postal_code: "33099",
					})}
				/>
			</Wrapper>
		</>
	);
}
