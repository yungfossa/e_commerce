import styled from "styled-components";
import TextInput from "../../shared/input/TextInput.tsx";
import Button from "../../shared/input/Button.tsx";
import { useMemo, useState, useContext } from "react";
import { faGlobe } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import AlertContext from "../../components/alert.tsx";
import { useAppDispatch, useAppSelector } from "../../hooks.ts";
import { useNavigate } from "react-router-dom";
import { authenticate } from "../../store/user.ts";

const Wrapper = styled.div`
    background-image: linear-gradient(to right bottom, #051937, #004d7a, #008793, #00bf72, #a8eb12);
    width: 100%;
    height: 100vh;
`;

const IconWrapper = styled.div`
    position: fixed;
    color: white;
    display: flex;
    width: calc(100% - 700px);
    height: 100vh;
    align-content: space-around;
    align-items: center;
    justify-content: center;
`;

const PanelWrapper = styled.div`
    background: white;
    width: 700px;
    height: 100vh;
    float: right;
    padding-top: 300px;
    display: flex;
    align-items: center;
    flex-direction: column;
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
			.then((e) => {
				showAlert("ok", "success");
				return navigate("/");
			})
			.catch((e) => {
				showAlert(e.message, "error");
			});
	};

	return (
		<Wrapper>
			<IconWrapper>
				<FontAwesomeIcon size="10x" icon={faGlobe} />
			</IconWrapper>
			<PanelWrapper>
				<h1> Shop Sphere </h1>
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
				<Button width={200} text="Log In" onClick={() => submit()}></Button>
			</PanelWrapper>
		</Wrapper>
	);
}
