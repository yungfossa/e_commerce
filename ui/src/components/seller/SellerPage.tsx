import { React, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import Header from "../../shared/Header.tsx";
import { useAppSelector } from "../../hooks.ts";
import Client from "../../shared/client/client.tsx";

export default function () {
	let { id } = useParams();

	const access_token = useAppSelector((s) => s.user.access_token);
	const client = new Client(access_token);

	const [sellerListings, setSellerListings] = useState(null);
	const [sellerReviews, setSellerReviews] = useState(null);

	useEffect(() => {
		client.get(`http://localhost:5000/products/${id}`).then((r) => {
			setSellerListings(r.data);
		});
	}, []);

	useEffect(() => {
		client.get(`http://localhost:5000/products/${id}/reviews`).then((r) => {
			setSellerReviews(r.data);
		});
	}, []);

	return (
		<>
			<Header />
			Listings:
			<br />
			{sellerListings?.map((l) => {
				return (
					<>
						<Link to={`/products/${l.product.id}/${l.id}`}>
							{l.product.name} - {l.price}
						</Link>
						<br />
					</>
				);
			})}
			Reviews:
			<br />
			{sellerReviews?.map((review) => {
				return (
					<>
						{review.title} - {review.description} - {review.rating}
						<br />
					</>
				);
			})}
		</>
	);
}
