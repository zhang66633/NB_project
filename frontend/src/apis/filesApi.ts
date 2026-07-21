import request from "@/utils/request";

export function uploadFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return request.post("/files/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

export function downloadFile(fileId: string) {
  return request.get(`/files/${fileId}`, { responseType: "blob" });
}
