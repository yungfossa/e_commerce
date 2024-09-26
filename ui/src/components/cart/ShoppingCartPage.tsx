import { React, useEffect, useState } from "react";
import Header from "../../shared/Header";
import { useAppSelector } from "../../hooks";
import Client from "../../shared/client/client";

export default function() {
	const access_token = useAppSelector((s) => s.user.access_token);
	const client = new Client(access_token);

	const [cart, setCart] = useState<any>(null);

	useEffect(() => {
		client.get("http://localhost:5000/cart")
			.then((r) => {
				setCart(r.data);
			});
	}, []);

	return (
		<>
			<Header />
			{JSON.stringify(cart)}
		</>
	);
}
