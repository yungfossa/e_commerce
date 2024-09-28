import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query";

export const authenticate = createAsyncThunk(
	"user/authenticate",
	async (
		{ email, password }: { email: string; password: string },
		{ rejectWithValue },
	): Promise<string> => {
		return await fetch("http://localhost:5000/login", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ email, password }),
		})
			.then(async (r) => {
				if (!r.ok) {
					return r.json().then((r) => {
						throw new Error(r.message);
					});
				}
				return r.json();
			})
			.then((r) => r.data.access_token)
			.catch(async (e) => {
				return rejectWithValue(e);
			});
	},
);

interface State {
	access_token: string;
	status: Status;
	profile: Profile | undefined;
}

type Status = "unknown" | "pending" | "success" | "failed";

interface Profile {
	birth_date: string;
	email: string;
	first_name: string;
	last_name: string;
	phone_number: string;
	profile_img: string;
}

export const userSlice = createSlice({
	name: "user",
	initialState: {
		access_token: "",
		status: "unknown",
		profile: undefined,
	},
	reducers: {
		logout(state) {
			state.access_token = "";
		},
	},
	extraReducers: (builder) => {
		builder.addCase(authenticate.pending, (state) => {
			state.status = "pending";
		});
		builder.addCase(authenticate.fulfilled, (state, action) => {
			state.status = "success";
			state.access_token = action.payload;
		});
		builder.addCase(authenticate.rejected, (state, action) => {
			state.status = "failed";
		});
	},
});

export const { logout } = userSlice.actions;
export default userSlice.reducer;
