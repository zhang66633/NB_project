import request from "@/utils/request";

export function uploadFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return request.post("/api/files/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

export function downloadFile(fileId: string) {
  return request.get(`/api/files/${fileId}`, { responseType: "blob" });
}
