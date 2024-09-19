import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const Wrapper = styled.div<{ width?: number }>`
    width: ${(props) => (props.width ? `${props.width}px` : "100%")};
    margin: 0.5rem;
    padding: 0 1rem 0 1rem;
    background-color: #f3f3f4;
    color: #0d0c22;
    border: 2px solid transparent;
    border-radius: 8px;

    display: flex;
    align-items: center;
    flex-direction: row;
`;

const InputWrapper = styled.input<{ width?: number }>`
    width: 100%;
    height: 40px;
    line-height: 28px;
    outline: none;
    transition: .3s ease;

    background-color: #f3f3f4;
    color: #0d0c22;
    border: 0;

    // makes buttons and input fields the same width
    box-sizing: border-box;
`;

interface Props {
	placeholder: string;
	password?: boolean;
	width?: number;
	setInput?: (s: string) => void;
	icon?: any;
}

export default function TextInput({
	placeholder,
	password,
	width,
	setInput,
	icon,
}: Props) {
	return (
		<Wrapper width={width}>
			{icon !== undefined && (
				<FontAwesomeIcon
					style={{ "margin-right": "0.75rem" }}
					size="m"
					icon={icon}
				/>
			)}
			<InputWrapper
				width={width}
				type={password ? "password" : "text"}
				placeholder={placeholder}
				onInput={(e) => setInput(e.target.value)}
			/>
		</Wrapper>
	);
}
