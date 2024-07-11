import { useContext, useEffect, useState } from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCheckCircle } from "@fortawesome/free-regular-svg-icons";
import { useAppDispatch, useAppSelector } from "./hooks.ts";
import { authenticate } from "./store/user.ts";
import AlertContext from "./components/alert.tsx";
import Header from "./shared/Header.tsx";

const Wrapper = styled.table`
`;

const Row = styled.tr`
`;

const MIN_COLUMN_WIDTH = 150;

const Column = styled.td<{ width?: number }>`
    width: ${(props) => props.width || MIN_COLUMN_WIDTH}px;
    background-color: white;
    color: black;
`;

type UserType = "customer" | "seller" | "admin";

interface User {
	name: string;
	surname: string;
	user_type: UserType;
}

function UsersTable(users: User[]) {
	return (
		<Wrapper>
			<Row>
				<Column width={300}>Name</Column>
				<Column>Surname</Column>
				<Column>User Type</Column>
			</Row>
			{users.map((u) => {
				return (
					<Row>
						<Column width={300}>{u.name}</Column>
						<Column>{u.surname}</Column>
						<Column>
							{u.user_type === "admin" && (
								<FontAwesomeIcon icon={faCheckCircle} />
							)}
						</Column>
					</Row>
				);
			})}
		</Wrapper>
	);
}

function App() {
	const [users, setUsers] = useState<User[]>([]);

	const access_token = useAppSelector((s) => s.user.access_token);
	const fetching = useAppSelector((s) => s.user.fetching);

	const dispatch = useAppDispatch();

	useEffect(() => {
		if (access_token === "") {
			return;
		}

		fetch("http://localhost:5000/users", {
			headers: {
				Authorization: `Bearer ${access_token}`,
			},
		})
			.then((r) => r.json())
			.then((r) => {
				console.log(r.users);
				setUsers(r.users);
			});
	}, [access_token]);

	if (fetching) {
		return "fetching";
	}

	if (!users) {
		return <>loading...</>;
	}

	return (
		<>
			<Header />
		</>
	);
	// return UsersTable(users);
}

export default App;
