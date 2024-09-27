import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const api = createApi({
	reducerPath: "api",
	baseQuery: fetchBaseQuery({
		baseUrl: "http://localhost:5000",
		prepareHeaders: (headers, { getState }) => {
			const state = getState();
			console.log(state);
			const token = state.user.access_token;
			if (token) {
				headers.set("authorization", `Bearer ${token}`);
				return headers;
			}
		},
	}),
	endpoints: (builder) => ({
		getProfile: builder.query({
			query: () => ({
				url: "/profile",
				method: "GET",
			}),
		}),
	}),
});

export const { useGetProfileQuery } = api;
