import { React } from "react";
import styled from "styled-components";

type Size = "small" | "medium" | "large";

interface Props {
	children: string | JSX.Element | JSX.Element[];
	size: Size;
}

const Wrapper = styled.div<{ size: number }>`
	font-size: ${(props) => props.size}px;
`;

function computeSize(size: Size): number {
	switch (size) {
		case "small":
			return 10;
		case "medium":
			return 15;
		case "large":
			return 20;
		default:
			return 15;
	}
}

export default function Text({ children, size }: Props) {
	return <Wrapper size={computeSize(size)}>{children}</Wrapper>;
}
