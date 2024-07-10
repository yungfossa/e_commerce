import styled from "styled-components";

const DEFAULT_WIDTH = 100;

const Wrapper = styled.input<{ width?: number }>`
    width: ${(props) => props.width || DEFAULT_WIDTH}px;
    height: 40px;
    line-height: 28px;
    margin: 1rem;
    padding: 0 1rem 0 1rem;
    border: 2px solid transparent;
    border-radius: 8px;
    outline: none;
    background-color: #f3f3f4;
    color: #0d0c22;
    transition: .3s ease;
`;

interface Props {
	placeholder: string;
	password?: boolean;
	width?: number;
	setInput: (s: string) => void;
}

export default function TextInput({
	placeholder,
	password,
	width,
	setInput,
}: Props) {
	return (
		<Wrapper
			width={width}
			type={password ? "password" : "text"}
			placeholder={placeholder}
			onInput={(e) => setInput(e.target.value)}
		></Wrapper>
	);
}
