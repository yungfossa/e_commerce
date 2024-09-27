import { useState, useContext, useEffect } from "react";
import AlertContext from "../../components/Alert.tsx";
import { useNavigate } from "react-router-dom";
import { useAppSelector } from "../../hooks.ts";
import Card from "../../shared/Card.tsx";
import Header from "../../shared/Header.tsx";
import styled from "styled-components";
import Client from "../../shared/client/client.tsx";
import { useGetProfileQuery } from "../../store/api.ts";

const ProfileImage = styled.img`
	border-radius: 50%;
	width: 100px;
	height: 100px;
`;

const Wrapper = styled.div`
	margin: 3rem;
`;

const default_avatar_url =
	"https://st3.depositphotos.com/9998432/13335/v/450/depositphotos_133352156-stock-illustration-default-placeholder-profile-icon.jpg";

export default function() {
	const navigate = useNavigate();
	const { showAlert } = useContext(AlertContext);

	const { data, error, isLoading } = useGetProfileQuery('', {});

	if (isLoading) {
		return <>Loading...</>;
	}

	const profile = data.data;

	return (
		<>
			<Header />

			<Wrapper>
				<Card>
					<ProfileImage src={profile.image_src || default_avatar_url} />
					<br />
					<h1>Hi {profile.first_name}!</h1>
					<br />
					Email: {profile.email}
					<br />
					Name: {profile.first_name}
					<br />
					Surname: {profile.last_name}
				</Card>
			</Wrapper>
		</>
	);
}
