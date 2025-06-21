import axios from "axios";
import { base_url } from "./BASE_URL";

const API_URL = `${base_url}/api/member`;

// 創建一個帶有認證功能的 axios 實例
const authAxios = axios.create({
  baseURL: API_URL
});

// 獲取下一個會員編號
interface ApiResponse<T> {
    success: boolean;
    data?: T;
    next_code?: T; // 根據後端返回的鍵名調整
    error?: string;
}

// 添加請求攔截器，自動為所有請求添加 token
authAxios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * 前端使用的會員資料結構
 */
export interface Member {
  Member_ID: string;
  Name: string;
  Gender: string;
  Birth: string;
  Phone: string;
  Address: string;
  LineID: string;
  BloodType: string;
  Referrer: string;  // 介紹人 ID
  Occupation: string;
  Note: string;
}

/**
 * 後端資料庫的會員資料結構
 */
interface BackendMember {
  member_id: number | string;
  name: string;
  birthday: Date | string;
  gender: 'Male' | 'Female' | 'Other' | string;
  blood_type: 'A' | 'B' | 'AB' | 'O' | string;
  line_id: string;
  address: string;
  inferrer_id: number | string | null;
  phone: string;
  occupation: string;
  note: string;
}

/**
 * 將後端資料轉換為前端格式
 */
const transformBackendToFrontend = (member: BackendMember): Member => {
  return {
    Member_ID: String(member.member_id),
    Name: member.name,
    Gender: member.gender || '',
    Birth: member.birthday ? (typeof member.birthday === 'string' ? member.birthday : member.birthday.toISOString().split('T')[0]) : '',
    Phone: member.phone || '',
    Address: member.address || '',
    LineID: member.line_id || '',
    BloodType: member.blood_type || '',
    Referrer: member.inferrer_id ? String(member.inferrer_id) : '',
    Occupation: member.occupation || '',
    Note: member.note || ''
  };
};

/**
 * 將前端資料轉換為後端格式
 */
const transformFrontendToBackend = (member: Partial<Member>): Partial<BackendMember> => {
  const backendMember: Partial<BackendMember> = {};
  
  if (member.Member_ID) backendMember.member_id = member.Member_ID;
  if (member.Name) backendMember.name = member.Name;
  if (member.Gender) backendMember.gender = member.Gender;
  if (member.Birth) backendMember.birthday = member.Birth;
  if (member.Phone) backendMember.phone = member.Phone;
  if (member.Address) backendMember.address = member.Address;
  if (member.LineID) backendMember.line_id = member.LineID;
  if (member.BloodType) backendMember.blood_type = member.BloodType;
  if (member.Referrer) backendMember.inferrer_id = member.Referrer;
  if (member.Occupation) backendMember.occupation = member.Occupation;
  if (member.Note) backendMember.note = member.Note;
  
  return backendMember;
};

/**
 * Get all members
 */
export const getAllMembers = async (): Promise<Member[]> => {
  try {
    const response = await authAxios.get('/list');
    const transformedData = response.data.map(transformBackendToFrontend);
    return transformedData;
  } catch (error) {
    console.error("Failed to fetch members:", error);
    throw error;
  }
};

/**
 * Search members by keyword (name, phone, etc.)
 */
export const searchMembers = async (keyword: string): Promise<Member[]> => {
  try {
    const response = await authAxios.get('/search', {
      params: { keyword }
    });
    const transformedData = response.data.map(transformBackendToFrontend);
    return transformedData;
  } catch (error) {
    console.error("Failed to search members:", error);
    throw error;
  }
};

/**
 * Search member by specific ID
 */
export const searchMemberById = async (memberId: string): Promise<Member[]> => {
  try {
    const response = await authAxios.get(`/${memberId}`);
    const transformedData = [transformBackendToFrontend(response.data)];
    return transformedData;
  } catch (error) {
    console.error("Failed to search member by ID:", error);
    throw error;
  }
};

/**
 * Get a single member by ID (returns the member object directly, not in an array)
 */
export const getMemberById = async (memberId: string): Promise<Member | null> => {
  try {
    const response = await authAxios.get(`/${memberId}`);
    return transformBackendToFrontend(response.data);
  } catch (error) {
    console.error("Failed to get member by ID:", error);
    return null;
  }
};

/**
 * Add a new member
 */
export const addMember = async (memberData: Omit<Member, 'Member_ID'>) => {
  try {
    const backendData = transformFrontendToBackend(memberData);
    const response = await authAxios.post('/create', backendData);
    return response.data;
  } catch (error) {
    console.error("Failed to add member:", error);
    throw error;
  }
};

/**
 * Update an existing member
 */
export const updateMember = async (memberId: string, memberData: Partial<Member>) => {
  try {
    const backendData = transformFrontendToBackend(memberData);
    const response = await authAxios.put(`/${memberId}`, backendData);
    return response.data;
  } catch (error) {
    console.error("Failed to update member:", error);
    throw error;
  }
};

/**
 * Delete a member
 */
export const deleteMember = async (memberId: string) => {
  try {
    const response = await authAxios.delete(`/${memberId}`);
    return response.data;
  } catch (error) {
    console.error("Failed to delete member:", error);
    throw error;
  }
};

/**
 * Add a new member with simplified parameters
 */
export const createMember = async (memberData: {
  name: string;
  birthday: string;
  address?: string;
  phone?: string;
  gender?: string;
  bloodType?: string;
  lineId?: string;
  referral?: string;
  occupation?: string;
  note?: string;
}) => {
  try {
    const backendData = {
      name: memberData.name,
      birthday: memberData.birthday,
      address: memberData.address || '',
      phone: memberData.phone || '',
      gender: memberData.gender || 'Other',
      blood_type: memberData.bloodType || '',
      line_id: memberData.lineId || '',
      inferrer_id: memberData.referral || null,
      occupation: memberData.occupation || '',
      note: memberData.note || ''
    };
    
    const response = await authAxios.post('/create', backendData);
    return response.data;
  } catch (error) {
    console.error("Failed to create member:", error);
    throw error;
  }
};

/**
 * Export members data to Excel
 */
export const exportMembers = async () => {
  try {
    const response = await authAxios.get('/export', {
      responseType: "blob"
    });
    return response.data;
  } catch (error) {
    console.error("Failed to export members:", error);
    throw error;
  }
};

/**
 * Check if member exists
 */
export const checkMemberExists = async (memberId: string): Promise<boolean> => {
  try {
    const response = await authAxios.get(`/check/${memberId}`);
    return response.data.exists;
  } catch (error) {
    console.error(`Failed to check if member ID ${memberId} exists:`, error);
    return false;
  }
};

/**
 * next member inedex
 */
export const getNextMemberCode = async (): Promise<ApiResponse<string>> => {
    try {
        const response = await axios.get(`${API_URL}/next-code`);
        return response.data;
    } catch (error: any) {
        console.error("獲取下一個會員編號失敗:", error);
        return { success: false, error: error.response?.data?.error || "獲取編號時發生網路錯誤" };
    }
};