import { React } from "react";
import { useParams } from "react-router-dom";

import Header from "../../shared/Header.tsx";

export default function() {
	let { id } = useParams();

	return (
		<>
			<Header />
			{"Seller page for " + id}
		</>
	);

}
