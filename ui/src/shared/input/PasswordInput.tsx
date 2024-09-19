import { React, useState } from "react";
import TextInput from "../../shared/input/TextInput.tsx";
import styled from "styled-components";

interface Props {
	width?: number;
	placeholder: string;
	setPassword: (s: string) => void;
}

interface PasswordMatchedConstraints {
	length: bool;
	number: bool;
	uppercase: bool;
	lowercase: bool;
}

// TODO better styling
const Wrapper = styled.div`
	width: 300px;
`;

// TODO better styling
const ConstraintWrapper = styled.li<{ valid: bool }>`
	color: ${(props) => (props.valid ? "green" : "red")};
`;

function renderPasswordMatchedConstraints(
	isPasswordValid: bool,
	c: PasswordMatchedConstraints,
) {
	if (isPasswordValid === undefined || isPasswordValid) {
		return <></>;
	}

	return (
		<Wrapper>
			Password must contain:
			<ul>
				<ConstraintWrapper valid={c.length}>
					minimum 8 characters
				</ConstraintWrapper>
				<ConstraintWrapper valid={c.number}>
					at least one number
				</ConstraintWrapper>
				<ConstraintWrapper valid={c.uppercase}>
					at least one uppercase letter
				</ConstraintWrapper>
				<ConstraintWrapper valid={c.lowercase}>
					at least one lowercase letter
				</ConstraintWrapper>
			</ul>
		</Wrapper>
	);
}

export default function PasswordInput({ width, setPassword }: Props) {
	const [isPasswordValid, setIsPasswordValid] = useState<bool>(undefined);
	const [passwordMatchedConstraints, setPasswordMatchedConstraints] =
		useState<PasswordMatchedConstraints>({});

	const checkPassword = (s) => {
		setPassword(s);
		const length = s.length > 8;
		const number = /[0-9]/.test(s);
		const uppercase = /[A-Z]/.test(s);
		const lowercase = /[a-z]/.test(s);
		setIsPasswordValid(length && number && uppercase && lowercase);
		setPasswordMatchedConstraints({
			length,
			number,
			uppercase,
			lowercase,
		});
	};

	return (
		<>
			<TextInput
				width={width}
				password
				placeholder="Enter your password"
				setInput={checkPassword}
			/>
			{renderPasswordMatchedConstraints(
				isPasswordValid,
				passwordMatchedConstraints,
			)}
		</>
	);
}
