import request from "@/utils/request";

export function getTaskMessages(taskId: string) {
  return request.get(`/api/tasks/${taskId}/messages`);
}

export function cancelTask(taskId: string) {
  return request.post(`/api/tasks/${taskId}/cancel`);
}

export function getTask(taskId: string) {
  return request.get(`/api/tasks/${taskId}`);
}

export function createTask(data: { problem: string; mode: string }) {
  return request.post("/api/tasks", data);
}
