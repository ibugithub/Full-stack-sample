import { createSlice, createAsyncThunk, type PayloadAction } from '@reduxjs/toolkit';
import { AxiosReqInstance } from '@/components/accounts/utils/axiosInstance';
import { ProfileInterface } from '@/types/interface';

interface AuthState {
  isAuthenticated: boolean;
  loogedInUser: ProfileInterface;
  isUnVerified: boolean;
  status: 'idle' | 'loading' | 'authenticated' | 'unauthenticated';
  currentRequestId?: string;
}

const initialState: AuthState = {
  isAuthenticated: false,
  loogedInUser: {} as ProfileInterface,
  isUnVerified: false,
  status: 'idle',
};

export const fetchLoggedInUser = createAsyncThunk(
  'auth/fetchLoggedInUser',
  async (_, { rejectWithValue }) => {
    const protectedRoute = AxiosReqInstance();
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
      return rejectWithValue('No access token found');
    }
    const baseUrl = process.env.NEXT_PUBLIC_BACKEND_BASE_URL || '';
    const url = `${baseUrl}/api/users/validateUser/`;
    try {
      const response = await protectedRoute.post(url);
      if (response.status === 200) {
        return response.data;
      } else {
        return rejectWithValue('Invalid token');
      }
    } catch {
      return rejectWithValue('Could not validate session');
    }
  },
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    updateAccountName(
      state,
      action: PayloadAction<{ email: string; name: string; first_name: string; last_name: string }>,
    ) {
      const current = state.loogedInUser.user ?? state.loogedInUser;
      if (!state.isAuthenticated || current.email !== action.payload.email) return;
      Object.assign(current, action.payload);
    },
    signOut(state) {
      state.isAuthenticated = false;
      state.loogedInUser = {} as ProfileInterface;
      state.isUnVerified = false;
      state.status = 'unauthenticated';
      state.currentRequestId = undefined;
    },
    setUnVerified(state, action) {
      state.isUnVerified = action.payload;
    },
  },
  extraReducers(builder) {
    builder.addCase(fetchLoggedInUser.pending, (state, action) => {
      state.status = 'loading';
      state.currentRequestId = action.meta.requestId;
    });
    builder.addCase(fetchLoggedInUser.fulfilled, (state, action) => {
      if (state.currentRequestId !== action.meta.requestId) return;
      state.currentRequestId = undefined;
      if (action.payload) {
        state.loogedInUser = action.payload;
        state.isAuthenticated = true;
        state.status = 'authenticated';
      } else {
        state.isAuthenticated = false;
        state.loogedInUser = {} as ProfileInterface;
        state.status = 'unauthenticated';
      }
    });
    builder.addCase(fetchLoggedInUser.rejected, (state, action) => {
      if (state.currentRequestId !== action.meta.requestId) return;
      state.currentRequestId = undefined;
      state.isAuthenticated = false;
      state.loogedInUser = {} as ProfileInterface;
      state.status = 'unauthenticated';
    });
  },
});

export const { setUnVerified, signOut, updateAccountName } = authSlice.actions;
export const authReducer = authSlice.reducer;
