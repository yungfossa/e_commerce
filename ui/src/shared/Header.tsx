import { React, useState, useEffect } from "react";
import styled from "styled-components";
import {
	faGlobe,
	faSearch,
	faShoppingCart,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import TextInput from "../shared/input/TextInput.tsx";
import { useAppSelector } from "../hooks.ts";
import { Link } from "react-router-dom";
import Client from "./client/client.tsx";
import { useDispatch } from "react-redux";
import { logout } from "../store/user.ts";

const Wrapper = styled.div`
    width: 100%;
    color: white;
    background: #008793;
    height: 70px;
    padding: 0 1rem;
    margin: 0px;

    box-sizing: border-box;

    display: flex;
    justify-content: space-between;
    align-items: center;
`;

const Section = styled.div<{ grow?: boolean }>`
	display: flex;
	${(props) => (props.grow ? "flex-grow: 1;" : "")}
	padding: 0 1rem;
	align-items: center;
`;

const Title = styled.div`
	font-weight: bold;
	font-size: 25px;
`;

export default function Header() {
	const access_token = useAppSelector((s) => s.user.access_token);
	const client = new Client(access_token);

	const dispatch = useDispatch();

	const [profile, setProfile] = useState<any>(null);

	useEffect(() => {
		client
			.get("http://localhost:5000/profile")
			.then((r) => setProfile(r.data))
			.catch((e) => {
				console.log("logging out");
				dispatch(logout());
			});
	}, []);

	return (
		<Wrapper>
			<Link
				to="/"
				style={{
					color: "white",
					textDecoration: "none",
				}}
			>
				<Section>
					<FontAwesomeIcon
						style={{ marginRight: "0.75rem" }}
						size="2x"
						icon={faGlobe}
					/>
					<Title>Shop Sphere</Title>
				</Section>
			</Link>
			<Section grow={true}>
				<TextInput icon={faSearch} placeholder="Search..." />
			</Section>
			{profile ? (
				<Section>
					<Link to="/me" style={{ color: "white", textDecoration: "none" }}>
						Welcome back <br />{" "}
						<u>
							<b>{profile.first_name}</b>
						</u>
					</Link>
					<div style={{ paddingLeft: "3rem" }} />
					<Link to="/cart">
						<FontAwesomeIcon
							style={{ marginRight: "0.75rem", color: "white" }}
							size="2x"
							icon={faShoppingCart}
						/>
					</Link>
				</Section>
			) : (
				<Section>
					<Link to="/login" style={{ color: "white" }}>
						Sign In
					</Link>
					<div style={{ paddingLeft: "0.5rem" }} />
					or
					<div style={{ paddingLeft: "0.5rem" }} />
					<Link to="/register" style={{ color: "white" }}>
						Sign Up
					</Link>
				</Section>
			)}
		</Wrapper>
	);
}
