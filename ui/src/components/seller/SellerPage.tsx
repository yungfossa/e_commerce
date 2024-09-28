import { React, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import Header from "../../shared/Header.tsx";
import { useAppSelector } from "../../hooks.ts";
import ReviewRating from "../../shared/ReviewRating.tsx";
import Card from "../../shared/Card.tsx";
import Client from "../../shared/client/client.tsx";
import styled from "styled-components";

const ListingWrapper = styled.div`
`;

const ReviewWrapper = styled.div`
`;

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

		client.get(`http://localhost:5000/products/${id}/reviews`).then((r) => {
			setSellerReviews(r.data);
		});
	}, []);

	return (
		<>
			<Header />
			Listings:
			<br />
			{sellerListings?.map((listing) => {
				return (
					<ListingWrapper key={listing.id}>
						<Link to={`/products/${listing.product.id}/${listing.id}`}>
							{listing.product.name} - {listing.price}
						</Link>
					</ListingWrapper>
				);
			})}
			Reviews:
			<br />
			{sellerReviews?.map((review) => {
				return (
					<Card key={review.id}>
						<ReviewWrapper>
							{review.customer.name} <br />
							{review.title} - {review.description} <br />
							<ReviewRating score={review.rating} />
						</ReviewWrapper>
					</Card>
				);
			})}
		</>
	);
}
