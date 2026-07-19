import request from "@/utils/request";

export function submitModelingTask(data: {
  problem: string;
  mode: "teach" | "execute";
  files?: File[];
}) {
  const formData = new FormData();
  formData.append("problem", data.problem);
  formData.append("mode", data.mode);
  if (data.files) {
    data.files.forEach((file) => formData.append("files", file));
  }
  return request.post("/api/tasks", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}
