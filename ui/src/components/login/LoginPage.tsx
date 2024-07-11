import styled from "styled-components";
import TextInput from "../../shared/input/TextInput.tsx";
import Text from "../../shared/Text.tsx";
import Button from "../../shared/input/Button.tsx";
import { useMemo, useState, useContext } from "react";
import { faGlobe } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import AlertContext from "../../components/alert.tsx";
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
    display: flex;
    flex-direction: column;

    display: flex; 
    justify-content: center; 
    align-items: center;
`;

export default function LoginPage() {
	const dispatch = useAppDispatch();

	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");

	const navigate = useNavigate();

	const { showAlert } = useContext(AlertContext);

	const submit = () => {
		dispatch(authenticate({ email: username, password }))
			.unwrap()
			.then((e) => navigate("/"))
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
					Don't have an account? <Link to="/register">Sign Up</Link>
				</Text>
				{/* TODO proper padding */}
				<br />
				<br />
				<br />
				<TextInput
					width={300}
					placeholder="Enter your email address"
					setInput={setUsername}
				/>
				<TextInput
					width={300}
					password
					placeholder="Enter your password"
					setInput={setPassword}
				/>
				<Button width={300} text="Log In" onClick={() => submit()}></Button>
				<Text size="medium">
					<Link to="/register">Forgot your password?</Link>
				</Text>
			</PanelWrapper>
		</Wrapper>
	);
}
