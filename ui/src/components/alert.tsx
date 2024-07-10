import {createContext, ReactNode, useState} from "react";
import styled from "styled-components";

type AlertType = 'info' | 'error';

interface Alert {
    id: number,
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

const AlertWrapper = styled.div`
    width: 300px;
    height: 40px;
    line-height: 28px;
    margin: 0.1rem;
    padding: 0 1rem 0 1rem;
    border: 2px solid transparent;
    border-radius: 8px;
    outline: none;
    background-color: #f3f3f4;
    color: #0d0c22;
    transition: .3s ease;
    display: flex;
    align-items: center;
`;

export const AlertProvider = ({children}: { children: ReactNode }) => {
    const [alerts, setAlert] = useState<Alert[]>([]);

    const showAlert = (message: string, type: AlertType) => {
        const id = performance.now();
        setAlert((alerts) => [...alerts, {id, message, type}]);
        setTimeout(() => {
            setAlert((alerts) => [...alerts.filter(a => a.id !== id)]);
        }, 3000);
    }

    return (<AlertContext.Provider value={{alerts, showAlert}}>
        <AlertsWrapper>
            {alerts.map(a => <AlertWrapper>{a.message}</AlertWrapper>)}
        </AlertsWrapper>
        {children}
    </AlertContext.Provider>)
}

export default AlertContext;