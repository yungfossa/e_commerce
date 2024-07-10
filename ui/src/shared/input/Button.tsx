import styled from "styled-components";

const DEFAULT_WIDTH = 100;

const Wrapper = styled.button<{ width?: number }>`
    width: ${props => props.width || DEFAULT_WIDTH}px;
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
    
    :hover {
        cursor: pointer;
        background-color: #d6d6da;
    }
`;

interface Props {
    text: string
    width?: number,
    onClick?: () => void
}

export default function Button({ text, width, onClick }: Props) {
    return <Wrapper width={width} onClick={onClick}>{text}</Wrapper>
}
