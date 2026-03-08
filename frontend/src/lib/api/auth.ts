import axios from "axios";

const API = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://localhost:4000",
    withCredentials: true,
});

export const googleLogin = () => {
    window.location.href = `${import.meta.env.VITE_API_URL || "http://localhost:4000"
        }/auth/google`;
};

export const getMe = async (token: string) => {
    const res = await API.get("/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
    });
    return res.data;
};
