import { useEffect, useMemo, useState } from "react";
import styled from "styled-components";
import { useAppSelector } from "./hooks.ts";
import Header from "./shared/Header.tsx";
import { Link } from "react-router-dom";
import Client from "./shared/client/client.tsx";
import Card from "./shared/Card.tsx";
import MultiRangeSlider from "./shared/input/MultiRangeSlider.tsx";


const SearchWrapper = styled.div`
`;

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

function toggleCategory(category: string, fileteredCategorie, setFilteredCategories) {
	return (e) => {
		setFilteredCategories({ ...fileteredCategorie, [category]: e.target.checked })
	}
}

export default function App() {
	const access_token = useAppSelector((s) => s.user.access_token);
	const client = new Client(access_token);

	const [products, setProducts] = useState<Product[]>([]);
	const [categories, setCategories] = useState<string[]>([]);
	const [maxPrice, setMaxPrice] = useState<number>(0);

	const [minFilterPrice, setMinFilterPrice] = useState<number>(0);
	const [maxFilterPrice, setMaxFilterPrice] = useState<number>(undefined);

	const [fileteredCategories, setFilteredCategories] = useState<any>({});

	useEffect(() => {
		client
			.post("http://localhost:5000/products", { offset: 0, limit: 10 })
			.then((r) => {
				setProducts(r.data as Product[]);
				setMaxPrice(Math.max(...r.data.map(product => +product.min_price)));
				console.log(Math.max(...r.data.map(product => +product.min_price)));
				console.log(r.data.map(product => +product.min_price));
				const categories = [... new Set(r.data.map(product => product.category))] as string[];
				setCategories(categories);
				setFilteredCategories(categories.reduce((m, o) => {
					m[o] = true;
					return m;
				}, {}))
			});
	}, []);

	return (
		<>
			<Header />

			<SearchWrapper>
				{categories.map(category => {
					return <div><input type="checkbox" checked={fileteredCategories[category]} onClick={toggleCategory(category, fileteredCategories, setFilteredCategories)} />{category}</div>;
				})}
				{maxPrice > 0 &&
					<MultiRangeSlider
						min={0}
						max={maxPrice}
						onChange={({ min, max }) => {
							console.log(min, max)
							setMinFilterPrice(min);
							setMaxFilterPrice(max);
						}}
					/>
				}
			</SearchWrapper>

			<ProductsWrapper>
				{products?.filter(product => maxFilterPrice === undefined || (Math.floor(product.min_price) >= minFilterPrice && Math.floor(product.min_price) <= maxFilterPrice))
					.filter(product => fileteredCategories[product.category])
					.map((product) => {
						return (
							<Card key={product.id}>
								<Link to={`/products/${product.id}`}>
									<img height="250px" width="250px" src={product.image_src} />
									<p>{product.name}</p>
									<p>{product.min_price}</p>
								</Link>
							</Card>
						);
					})}
			</ProductsWrapper >
		</>
	);
}
