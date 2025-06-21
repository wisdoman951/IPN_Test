import axios from "axios";
import { base_url } from "./BASE_URL";

const API_URL = `${base_url}/api/medical-record`;

// 獲取所有健康檢查記錄
export const getAllMedicalRecords = async () => {
  const response = await axios.get(`${API_URL}/list`);
  return response.data;
};

// 搜尋健康檢查記錄
export const searchMedicalRecords = async (keyword: string) => {
  const response = await axios.get(`${API_URL}/search`, {
    params: { keyword }
  });
  return response.data;
};

/*// 新增健康檢查記錄
export const createMedicalRecord = async (data: {
  memberId: string;
  height: string;
  weight: string;
  bloodPressure: string;
  remark: string;
  symptom: string;
  familyHistory: string;
  restrictedGroup: string;
}) => {
  return axios.post(`${API_URL}/create`, data);
};*/

// 刪除健康檢查記錄
export const deleteMedicalRecord = async (recordId: number) => {
  return axios.delete(`${API_URL}/${recordId}`);
};

// 匯出健康檢查記錄
export const exportMedicalRecords = async () => {
  const response = await axios.get(`${API_URL}/export`, {
    responseType: "blob"
  });
  return response.data;
}; 

// 根據 ID 獲取單筆健康檢查記錄
export const getMedicalRecordById = async (recordId: number) => {
  const response = await axios.get(`${API_URL}/${recordId}`);
  return response.data;
};
// 注意：為了彈性，將 create 和 update 的資料類型統一起來
// 我們可以定義一個共用的 Type，但為了簡單起見，這裡直接修改
export const createMedicalRecord = async (data: any) => {
  return axios.post(`${API_URL}/create`, data);
};

export const updateMedicalRecord = async (recordId: number, data: any) => {
  return axios.put(`${API_URL}/update/${recordId}`, data);
};