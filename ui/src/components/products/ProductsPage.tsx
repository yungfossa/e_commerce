import { React, useEffect, useState, useContext } from "react";
import styled from "styled-components";
import { useAppDispatch, useAppSelector } from "../../hooks.ts";
import { useParams } from "react-router-dom";
import Header from "../../shared/Header.tsx";
import { Link } from "react-router-dom";
import AlertContext from "../../components/Alert.tsx";
import { useNavigate } from "react-router-dom";

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

export default function ProductsPage() {
	const navigate = useNavigate();
	const { showAlert } = useContext(AlertContext);

	let { id } = useParams();

	const access_token = useAppSelector((s) => s.user.access_token);
	const [product, setProduct] = useState<any>(null);
	const [listing, setListing] = useState<any>(null);

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
				setListing(r.data.listings[0] || null);
			})
			.catch((e) => {
				showAlert("An error occured", "error");
				navigate("/");
			});
	}, [access_token]);

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
						{listing.seller.name && <Link to={`/seller/${listing.seller.name}`}>View {listing.seller.name} store</Link>}
					</Store>
					<img height="250px" width="250px" src={product.image_src} />
					{listing?.price || "Item not available, sorry bud."}
				</ProductWrapper>

				<ListingWrapper>
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
				</ListingWrapper>
			</Wrapper>

			Reviews:
			<ul>
				{product &&
					product.listings.map((p: any) => {
						return p.reviews.map((l: any) => {
							return (
								<ListingsWrapper>
									<p>{l.title}</p>
									<p>{l.description}</p>
									<p>{l.rating}</p>
								</ListingsWrapper>
							);
						})

					})}
			</ul>
		</>
	);
}
