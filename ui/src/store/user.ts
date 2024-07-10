import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

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
			body: JSON.stringify({
				email: email,
				password: password,
			}),
		})
			.then((r) => {
				if (!r.ok) {
					return r.json().then((r) => {
						throw new Error(r.message);
					});
				}
				return r.json();
			})
			.then((r) => r.access_token)
			.catch(async (e) => {
				return rejectWithValue(e);
			});
	},
);

type Status = "idle" | "pending" | "success" | "failed";

export const userSlice = createSlice({
	name: "user",
	initialState: {
		access_token: "",
		status: "idle",
	},
	reducers: {},
	extraReducers: (builder) => {
		builder.addCase(authenticate.pending, (state) => {
			state.status = "pending";
		});
		builder.addCase(authenticate.fulfilled, (state, action) => {
			state.access_token = action.payload;
			state.status = "success";
		});
		builder.addCase(authenticate.rejected, (state, action) => {
			console.log(action.payload.message);
			state.status = "failed";
		});
	},
});

export default userSlice.reducer;
