import styled from "styled-components";

const Wrapper = styled.div`
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
	children: string | JSX.Element | JSX.Element[];
}

export default function Crad({ children }: Props) {
	return <Wrapper>{children}</Wrapper>;
}
