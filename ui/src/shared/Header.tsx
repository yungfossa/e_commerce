import { React } from "react";
import styled from "styled-components";
import { faGlobe, faSearch } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import TextInput from "../shared/input/TextInput.tsx";

const Wrapper = styled.div`
    width: 100%;
    color: white;
    background: #00bf72;
    height: 70px;
    padding: 0 1rem;
    margin: 0px;

    box-sizing: border-box;
    
    display: flex; 
    justify-content: space-between; 
    align-items: center;
`;

const Section = styled.div<{ grow?: bool }>`
	display: flex;
	${(props) => (props.grow ? "flex-grow: 1;" : "")}
	padding: 0 1rem;
`;

export default function Header() {
	return (
		<Wrapper>
			<Section>
				<FontAwesomeIcon
					style={{ "margin-right": "0.75rem" }}
					size="m"
					icon={faGlobe}
				/>
				Shop Sphere
			</Section>
			<Section grow={true}>
				<TextInput icon={faSearch} placeholder="Search..." />
			</Section>
			<Section>Welcome little fella</Section>
		</Wrapper>
	);
}
