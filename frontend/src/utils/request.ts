import axios from "axios";

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 60000,
});

// Attach JWT token to every request
service.interceptors.request.use(
  (config) => {
    try {
      const token = localStorage.getItem("mma:token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch {
      /* ignore */
    }
    return config;
  },
  (error) => {
    console.log(error);
    return Promise.reject(error);
  },
);

service.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error),
);

export default service;
export { service as request };
