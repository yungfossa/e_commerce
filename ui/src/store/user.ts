import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

export const authenticate = createAsyncThunk(
	"user/authenticate",
	async (
		{ email, password }: { email: string; password: string },
		{ rejectWithValue },
	): Promise<string> => {
		console.log("requested");
		return await fetch("http://localhost:5000/login", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ email, password }),
		})
			.then((r) => {
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

type Status = "unknown" | "pending" | "success" | "failed";

export const userSlice = createSlice({
	name: "user",
	initialState: {
		access_token: "",
		status: "unknown" as Status,
	},
	reducers: {},
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

export default userSlice.reducer;
