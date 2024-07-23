import styled from "styled-components";

const Wrapper = styled.div`
    width: 300px;
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

export default function Alert() {
	return <Wrapper></Wrapper>;
}
