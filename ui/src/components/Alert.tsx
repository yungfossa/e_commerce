import { createContext, ReactNode, useState } from "react";
import styled from "styled-components";

// TODO animate the alerts

type AlertType = "success" | "info" | "error";

interface Alert {
	id: number;
	message: string;
	type: AlertType;
}

interface Props {
	alerts: Alert[];
	showAlert: (message: string, type: AlertType) => void;
}

const AlertContext = createContext<Props>({} as Props);

const AlertsWrapper = styled.div`
    position: absolute;
    right: 0;
    bottom: 0;
    padding: 1rem;
`;

const AlertWrapper = styled.div<{ color: string; bg: string }>`
    width: 300px;
    height: 40px;
    line-height: 28px;
    margin: 0.1rem;
    padding: 0 1rem 0 1rem;
    border: 2px solid transparent;
    border-radius: 8px;
    outline: none;
    background-color: ${(props) => props.color};
    color: ${(props) => props.bg};
    transition: .3s ease;
    display: flex;
    align-items: center;
`;

interface Color {
	color: string;
	bg: string;
}

function computeColorFromSeverity(t: AlertType): Color {
	switch (t) {
		case "success":
			// TODO pick a color for successful alerts
			return { color: "#00ff00", bg: "#ffffff" };
		case "info":
			return { color: "#f3f3f4", bg: "#0d0c22" };
		case "error":
			// TODO pick a color for error alerts
			return { color: "#ff0000", bg: "#ffffff" };
		default:
			return { color: "#f3f3f4", bg: "#0d0c22" };
	}
}

export const AlertProvider = ({ children }: { children: ReactNode }) => {
	const [alerts, setAlert] = useState<Alert[]>([]);

	const showAlert = (message: string, type: AlertType) => {
		const id = performance.now();
		setAlert((alerts) => [...alerts, { id, message, type }]);
		setTimeout(() => {
			setAlert((alerts) => [...alerts.filter((a) => a.id !== id)]);
		}, 3000);
	};

	return (
		<AlertContext.Provider value={{ alerts, showAlert }}>
			<AlertsWrapper>
				{alerts.map((a) => (
					// TODO bg and color should be swapped, and we shouldn't call computeColorFromSeverity twice
					<AlertWrapper
						bg={computeColorFromSeverity(a.type).bg}
						color={computeColorFromSeverity(a.type).color}
					>
						{a.message}
					</AlertWrapper>
				))}
			</AlertsWrapper>
			{children}
		</AlertContext.Provider>
	);
};

export default AlertContext;
