import request from "@/utils/request";

export function createTask(data: { problem: string; mode: string }) {
  return request.post("/tasks", data);
}
