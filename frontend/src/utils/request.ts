import axios from "axios";

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 10000,
});

service.interceptors.request.use(
  (config) => config,
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
