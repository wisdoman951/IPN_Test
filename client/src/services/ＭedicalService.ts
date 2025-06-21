import axios from "axios";
import { base_url } from "./BASE_URL";

const API_URL = `${base_url}/api/medical-record`;

// 取得所有健康檢查紀錄
export const getAllMedicalRecords = async () => {
    const res = await axios.get(`${API_URL}/list`);
    return res.data;
};

// 搜尋健康檢查紀錄
export const searchMedicalRecords = async (keyword: string) => {
    const res = await axios.get(`${API_URL}/search`, {
        params: { keyword }
    });
    return res.data;
};

// 刪除單筆紀錄
// 刪除健康檢查記錄
export const deleteMedicalRecord = async (recordId: number) => {
  // 在 URL 中加入 /delete
  return axios.delete(`${API_URL}/delete/${recordId}`);
};

// 匯出 Excel
export const exportMedicalRecords = async () => {
    const res = await axios.get(`${API_URL}/export`, {
        responseType: "blob",
    });

    const blob = new Blob([res.data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.setAttribute("download", "健康檢查紀錄.xlsx");
    document.body.appendChild(link);
    link.click();
    link.remove();
};

// 檢查會員是否存在
export const checkMemberExists = async (memberId: string) => {
  try {
    const res = await axios.get(`${base_url}/api/member/check/${memberId}`);
    return res.data.exists;
  } catch (error) {
    console.error("檢查會員存在失敗", error);
    return false;
  }
};

// 根據ID取得會員資料
export const getMemberById = async (memberId: string) => {
  try {
    const res = await axios.get(`${base_url}/api/member/${memberId}`);
    return res.data;
  } catch (error) {
    console.error("獲取會員資料失敗", error);
    throw error;
  }
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