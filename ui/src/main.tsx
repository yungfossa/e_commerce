import {createBrowserRouter, RouterProvider,} from "react-router-dom";
import ReactDOM from 'react-dom/client'
import App from "./App.tsx";
import './main.css'
import {Provider} from "react-redux";

import store from './store/store.ts'
import LoginPage from "./components/login/LoginPage.tsx";
import {AlertProvider} from "./components/alert.tsx";

const router = createBrowserRouter([
    {
        path: "/",
        element: <App/>,
    },
    {
        path: "/login",
        element: <LoginPage/>,
    },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
    <Provider store={store}>
        <AlertProvider>
            <RouterProvider router={router}/>
        </AlertProvider>
    </Provider>,
)
