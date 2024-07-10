import {createAsyncThunk, createSlice} from '@reduxjs/toolkit'


export const authenticate = createAsyncThunk(
    'user/authenticate',
    async ({email, password}: { email: string, password: string }): Promise<string> => {
        return await fetch('http://localhost:5000/login', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                'email': email,
                'password': password,
            })
        })
            .then(r => r.json())
            .then(r => r.access_token)
    })

export const userSlice = createSlice({
    name: 'user',
    initialState: {
        access_token: '',
        fetching: false,
    },
    reducers: {},
    extraReducers: (builder) => {
        builder.addCase(authenticate.pending, (state) => {
            state.fetching = true;
        })
        builder.addCase(authenticate.fulfilled, (state, action) => {
            state.access_token = action.payload;
            state.fetching = false;
        })
    },
})

export default userSlice.reducer