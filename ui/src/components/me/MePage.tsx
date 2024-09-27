import { React, useState, useContext, useEffect } from "react";
import AlertContext from "../../components/Alert.tsx";
import { useNavigate } from "react-router-dom";
import { useAppSelector } from "../../hooks.ts";
import Header from "../../shared/Header.tsx";
import styled from "styled-components";
import Client from "../../shared/client/client.tsx";

const ProfileImage = styled.img`
	border-radius: 50%;
	width: 100px;
	height: 100px;
`;

const default_avatar_url = "https://st3.depositphotos.com/9998432/13335/v/450/depositphotos_133352156-stock-illustration-default-placeholder-profile-icon.jpg";

export default function() {
	const navigate = useNavigate();
	const { showAlert } = useContext(AlertContext);

	const access_token = useAppSelector((s) => s.user.access_token);
	const client = new Client(access_token);

	const [profile, setProfile] = useState(null);

	useEffect(() => {
		client.get(`http://localhost:5000/profile`)
			.then((r) => {
				setProfile(r.data);
			})
			.catch((e) => {
				showAlert("An error occured", "error");
				navigate("/");
			});
	}, []);

	if (!profile) {
		return <>Loading...</>
	}

	return (
		<>
			<Header />

			<ProfileImage src={profile.image_src || default_avatar_url} />

			<br />

			<h1>Hi {profile.first_name}!</h1>

			<br />

			Email: {profile.email}

			<br />

			Name: {profile.first_name}

			<br />

			Surname: {profile.last_name}
		</>
	);

}
