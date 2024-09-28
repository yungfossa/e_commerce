import { faStar } from "@fortawesome/free-regular-svg-icons";
import { faStar as faSolidStar } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import styled from "styled-components";

const Wrapper = styled.div`
`;

interface Props {
	score: number;
}

export default function ReviewRating({ score }: Props) {
	return (
		<Wrapper>
			{[...Array(score)].map((n) => {
				return <FontAwesomeIcon key={n} icon={faSolidStar} />;
			})}
			{[...Array(5 - score)].map((n) => {
				return <FontAwesomeIcon key={5 - n} icon={faStar} />;
			})}
		</Wrapper>
	);
}
