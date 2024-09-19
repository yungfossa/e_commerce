import { React, useState, useEffect } from "react";
import styled from "styled-components";
import { faGlobe, faSearch } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import TextInput from "../shared/input/TextInput.tsx";
import { useAppSelector } from "../hooks.ts";
import { Link } from "react-router-dom";

const Wrapper = styled.div`
    width: 100%;
    color: white;
    background: #00bf72;
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
`;

export default function Header() {
	const access_token = useAppSelector((s) => s.user.access_token);
	const [profile, setProfile] = useState<any>(null);

	useEffect(() => {
		if (access_token === "") {
			return;
		}

		fetch("http://localhost:5000/profile", {
			headers: {
				Authorization: `Bearer ${access_token}`,
			},
		})
			.then((r) => r.json())
			.then((r) => {
				setProfile(r.data);
			});
	}, [access_token]);

	return (
		<Wrapper>
			<Section>
				<FontAwesomeIcon
					style={{ "margin-right": "0.75rem" }}
					size="m"
					icon={faGlobe}
				/>
				Shop Sphere
			</Section>
			<Section grow={true}>
				<TextInput icon={faSearch} placeholder="Search..." />
			</Section>
			{profile ? (
				<Section>Welcome back {profile.name}</Section>
			) : (
				<Section>
					<Link to="/login">Sign In</Link> or <Link to="/signup">Sign Up</Link>
				</Section>
			)}
		</Wrapper>
	);
}
