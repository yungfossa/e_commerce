import { React, useEffect, useState, useContext } from "react";
import styled from "styled-components";
import { useAppSelector } from "../../hooks.ts";
import { useParams } from "react-router-dom";
import Header from "../../shared/Header.tsx";
import { Link } from "react-router-dom";
import AlertContext from "../../components/Alert.tsx";
import { useNavigate } from "react-router-dom";
import Button from "../../shared/input/Button.tsx";
import Client from "../../shared/client/client.tsx";
import ReviewRating from "../../shared/ReviewRating.tsx";

const ListingsWrapper = styled.div`
	border: 1px black solid;
`;

const ListingWrapper = styled.div`
	border: 1px black solid;
	flex: 50%;
`;

const ProductWrapper = styled.div`
	border: 1px black solid;
	padding: 100px;
	flex: 50%;
`;

const Wrapper = styled.div`
	border: 1px black solid;
	display: flex;
	padding: 100px;
`;

const Title = styled.div`
	font-weight: bold;
	font-size: 50px;
`;

const Category = styled.div`
	color: gray;
`;

const Store = styled.div`
`;

function createAddToCartFn(client: Client, lid: string) {
	const { showAlert } = useContext(AlertContext);
	return () => {
		client
			.post("http://localhost:5000/cart", {
				listing_id: lid,
				quantity: 1,
			})
			.then((r) => {
				showAlert(JSON.stringify(r), "info");
			});
	};
}

export default function ProductsPage() {
	const { showAlert } = useContext(AlertContext);

	const navigate = useNavigate();

	const { pid, lid } = useParams();

	const access_token = useAppSelector((s) => s.user.access_token);
	const client = new Client(access_token);

	const [product, setProduct] = useState<any>(null);
	const [listing, setListing] = useState<any>(null);

	useEffect(() => {
		client
			.post(`http://localhost:5000/products/${pid}`, {
				offset: 0,
				limit: 100,
			})
			.then((r) => {
				setProduct(r.data);
				if (lid) {
					setListing(r.data.listings.filter((r: any) => r.id === lid)[0]);
				} else {
					setListing(r.data.listings[0]);
				}
			})
			.catch((e) => {
				showAlert("An error occured", "error");
				navigate("/");
			});
	}, [lid]);

	if (product === null) {
		return "Loading...";
	}

	return (
		<>
			<Header />
			<Wrapper>
				<ProductWrapper>
					<Title>{product.name}</Title>
					<Category>{product.category.name}</Category>
					<Store>
						{listing.seller.name && (
							<Link to={`/seller/${listing.seller.id}`}>
								View {listing.seller.name} store
							</Link>
						)}
					</Store>
					<img height="250px" width="250px" src={product.image_src} />
					<br />
					For small price of{" "}
					{listing?.price || "Item not available, sorry bud."} dolla.
				</ProductWrapper>

				<ListingWrapper>
					<ul>
						{product?.listings.map((listing) => {
							return (
								<ListingsWrapper key={listing.id}>
									<Link to={`/products/${pid}/${listing.id}`}>
										<p>{listing.seller.name}</p>
										<p>only {listing.quantity} left</p>
										<p>{listing.price} dolla</p>
									</Link>
									{access_token ? (
										<Button
											text="add to cart"
											width={300}
											onClick={createAddToCartFn(client, listing.id)}
										/>
									) : (
										<Link to="/login">Wanna buy? Login</Link>
									)}
								</ListingsWrapper>
							);
						})}
					</ul>
				</ListingWrapper>
			</Wrapper>
			Reviews:
			<ul>
				{product?.listings.map((p) => {
					return p.reviews.map((l) => {
						return (
							<ListingsWrapper>
								<p>{l.customer.name} wrote:</p>
								<p>
									<b>{l.title}</b>
									<ReviewRating score={l.rating} />
								</p>
								<p>{l.description}</p>
							</ListingsWrapper>
						);
					});
				})}
			</ul>
		</>
	);
}
