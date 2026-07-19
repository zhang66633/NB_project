import request from "@/utils/request";

export function getApiKeys() {
  return request.get("/api/apikeys");
}

export function addApiKey(data: { name: string; key: string; provider: string }) {
  return request.post("/api/apikeys", data);
}

export function deleteApiKey(id: string) {
  return request.delete(`/api/apikeys/${id}`);
}
