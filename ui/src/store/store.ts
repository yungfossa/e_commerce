import { configureStore } from "@reduxjs/toolkit";
import userReducer from "./user.ts";
import { api } from "./api.ts";

const reHydrateStore = () => {
	if (localStorage.getItem("applicationState") !== null) {
		return JSON.parse(localStorage.getItem("applicationState")); // re-hydrate the store
	}
};

const localStorageMiddleware = ({ getState }) => {
	return (next) => (action) => {
		const result = next(action);
		localStorage.setItem("applicationState", JSON.stringify(getState()));
		return result;
	};
};

const store = configureStore({
	reducer: {
		user: userReducer,
		[api.reducerPath]: api.reducer,
	},
	preloadedState: reHydrateStore(),
	middleware: (getDefaultMiddleware) =>
		getDefaultMiddleware()
			.concat(localStorageMiddleware)
			.concat(api.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;
