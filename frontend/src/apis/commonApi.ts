import request from "@/utils/request";

export function getTaskMessages(taskId: string) {
  return request.get(`/tasks/${taskId}/messages`);
}

export function cancelTask(taskId: string) {
  return request.post(`/tasks/${taskId}/cancel`);
}

export function getTask(taskId: string) {
  return request.get(`/tasks/${taskId}`);
}

export function createTask(data: { problem: string; mode: string }) {
  return request.post("/tasks", data);
}
