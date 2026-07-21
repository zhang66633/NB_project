import request from "@/utils/request";

export function getApiKeys() {
  return request.get("/apikeys");
}

export function addApiKey(data: { name: string; key: string; provider: string; model_name: string }) {
  return request.post("/apikeys", data);
}

export function deleteApiKey(id: string) {
  return request.delete(`/apikeys/${id}`);
}

export function setDefaultApiKey(id: string) {
  return request.post(`/apikeys/${id}/default`);
}