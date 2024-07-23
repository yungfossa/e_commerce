import styled from "styled-components";
import TextInput from "../../shared/input/TextInput.tsx";
import PasswordInput from "../../shared/input/PasswordInput.tsx";
import Text from "../../shared/Text.tsx";
import Button from "../../shared/input/Button.tsx";
import { useMemo, useState, useContext } from "react";
import { faGlobe } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import AlertContext from "../../components/Alert.tsx";
import { useAppDispatch, useAppSelector } from "../../hooks.ts";
import { useNavigate } from "react-router-dom";
import { authenticate } from "../../store/user.ts";
import { Link } from "react-router-dom";

const Wrapper = styled.div`
    background-image: linear-gradient(to right bottom, #051937, #004d7a, #008793, #00bf72, #a8eb12);
    width: 100%;
    height: 100vh;
`;

const IconWrapper = styled.div`
    position: fixed;
    color: white;
    display: flex;
    width: 50%;
    height: 100vh;
    align-content: space-around;
    align-items: center;
    justify-content: center;
`;

const PanelWrapper = styled.div`
    background: white;
    width: 50%;
    height: 100vh;
    float: right;
    margin: 0 auto;
    display: flex;
    flex-direction: column;

    display: flex;
    justify-content: center;
    align-items: center;
`;

export default function RegisterPage() {
	const dispatch = useAppDispatch();

	const [email, setEmail] = useState("");
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");

	const navigate = useNavigate();

	const { showAlert } = useContext(AlertContext);

	const submit = () => {
		dispatch(authenticate({ email: username, password }))
			.unwrap()
			.then((e) => navigate("/login"))
			.catch((e) => showAlert(e.message, "error"));
	};

	return (
		<Wrapper>
			<IconWrapper>
				<FontAwesomeIcon size="10x" icon={faGlobe} />
			</IconWrapper>
			<PanelWrapper>
				<h1> Shop Sphere </h1>
				<Text size="medium">
					Already signed up? <Link to="/login">Log In</Link>
				</Text>
				{/* TODO proper padding */}
				<br />
				<br />
				<br />
				<TextInput
					width={300}
					placeholder="Enter your email address"
					setInput={setEmail}
				/>
				<TextInput
					width={300}
					placeholder="Enter your username"
					setInput={setUsername}
				/>
				<PasswordInput
					width={300}
					placeholder="Enter your password"
					setPassword={setPassword}
				/>
				<Button width={300} text="Sign Up" onClick={() => submit()}></Button>
			</PanelWrapper>
		</Wrapper>
	);
}
