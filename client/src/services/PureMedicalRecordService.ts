import axios from "axios";
import { base_url } from "./BASE_URL";

const API_URL = `${base_url}/api/pure-medical-record`;

export interface PureMedicalRecord {
  ipn_pure_id: number;
  Name?: string; // 來自會員資料
  blood_preasure?: string;
  date?: string;
  height?: number; // 雖然不在表格顯示，但 API 可能仍會回傳
  weight?: number;
  body_fat_percentage?: number; // <--- 新增體脂肪欄位
  visceral_fat?: number;
  basal_metabolic_rate?: number;
  body_age?: number;
  bmi?: string; // 通常 BMI 是計算出來的
  pure_item?: string;
  staff_name?: string; // 服務人
  note?: string;
  // ... 其他可能的欄位 ...
  member_id?: number; // 假設有會員ID
}

// 獲取所有淨化健康紀錄
export const getAllPureRecords = async () => {
  try {
    const response = await axios.get(`${API_URL}`);
    return response.data;
  } catch (error) {
    console.error("獲取淨化健康紀錄失敗", error);
    return [];
  }
};

// 搜尋淨化健康紀錄
export const searchPureRecords = async (keyword: string) => {
  try {
    const response = await axios.get(`${API_URL}/search`, {
      params: { keyword }
    });
    return response.data;
  } catch (error) {
    console.error("搜尋淨化健康紀錄失敗", error);
    return [];
  }
};

// 按過濾條件搜尋淨化健康紀錄
export const filterPureRecords = async (filters: {
  name?: string;
  pure_item?: string;
  staff_name?: string;
}) => {
  try {
    const response = await axios.get(`${API_URL}/filter`, {
      params: filters
    });
    return response.data;
  } catch (error) {
    console.error("過濾淨化健康紀錄失敗", error);
    return [];
  }
};

// 獲取特定會員的淨化健康紀錄
export const getMemberPureRecords = async (memberId: string) => {
  try {
    const response = await axios.get(`${API_URL}/member/${memberId}`);
    return response.data;
  } catch (error) {
    console.error("獲取會員淨化健康紀錄失敗", error);
    return [];
  }
};

// 新增淨化健康紀錄
export const addPureRecord = async (data: {
  member_id: string;
  staff_id?: string;
  visceral_fat?: string | number;
  blood_preasure?: string;
  basal_metabolic_rate?: string | number;
  date?: string;
  body_age?: string | number;
  height?: string | number;
  weight?: string | number;
  bmi?: string | number;
  pure_item?: string;
  note?: string;
}) => {
  return axios.post(`${API_URL}`, data);
};

// 更新淨化健康紀錄
export const updatePureRecord = async (
  pureId: number,
  data: {
    member_id?: string;
    staff_id?: string;
    visceral_fat?: string | number;
    blood_preasure?: string;
    basal_metabolic_rate?: string | number;
    date?: string;
    body_age?: string | number;
    height?: string | number;
    weight?: string | number;
    bmi?: string | number;
    pure_item?: string;
    note?: string;
  }
) => {
  return axios.put(`${API_URL}/${pureId}`, data);
};

// 刪除淨化健康紀錄
export const deletePureRecord = async (pureId: number) => {
  return axios.delete(`${API_URL}/${pureId}`);
};

// 導出淨化健康紀錄
export const exportPureRecords = async () => {
  try {
    const response = await axios.get(`${API_URL}/export`, {
      responseType: "blob"
    });
    return response.data;
  } catch (error) {
    console.error("導出淨化健康紀錄失敗", error);
    throw error;
  }
}; 