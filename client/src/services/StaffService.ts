// client/src/services/StaffService.ts
import axios from "axios";
import { base_url } from "./BASE_URL";

const API_URL = `${base_url}/api/staff`;

// 定義員工接口
export interface Staff {
    Staff_ID: number;
    Staff_Name: string;
    Staff_ID_Number: string;
    Staff_Phone?: string;
    Staff_Status?: string;
    Staff_Email?: string;
    Staff_Sex?: string;
    Staff_Store?: string;
    Staff_PermissionLevel?: string;
    Staff_IdNumber?: string; // 身分證字號
}

// 獲取所有員工
export const getAllStaff = async () => {
    try {
        console.log("正在獲取所有員工...");
        const response = await axios.get(`${API_URL}/list`);
        
        console.log("API 返回數據:", response.data);
        
        // 檢查返回數據是否為空數組
        if (Array.isArray(response.data) && response.data.length === 0) {
            console.warn("API 返回了空的員工列表");
        }
        
        return {
            success: true,
            data: response.data
        };
    } catch (error) {
        console.error("獲取員工列表失敗:", error);
        
        // 增強錯誤信息
        if (axios.isAxiosError(error)) {
            console.error("HTTP 狀態碼:", error.response?.status);
            console.error("錯誤響應:", error.response?.data);
        }
        
        return {
            success: false,
            data: [],
            error: error instanceof Error ? error.message : String(error)
        };
    }
};

// 搜尋員工
export const searchStaff = async (keyword: string) => {
    try {
        const response = await axios.get(`${API_URL}/search`, {
            params: { keyword }
        });
        return {
            success: true,
            data: response.data
        };
    } catch (error) {
        console.error("搜尋員工失敗:", error);
        return {
            success: false,
            data: []
        };
    }
};

// 獲取單個員工資料
export const getStaffById = async (staffId: number) => {
    try {
        const response = await axios.get(`${API_URL}/${staffId}`);
        return {
            success: true,
            data: response.data
        };
    } catch (error) {
        console.error(`獲取員工 ID ${staffId} 資料失敗:`, error);
        return {
            success: false,
            data: null
        };
    }
};

// 獲取員工詳細資料
export const getStaffDetails = async (staffId: number) => {
    try {
        const response = await axios.get(`${API_URL}/details/${staffId}`);
        return {
            success: true,
            data: response.data
        };
    } catch (error) {
        console.error(`獲取員工 ID ${staffId} 詳細資料失敗:`, error);
        return {
            success: false,
            data: null
        };
    }
};

// 新增員工
export const addStaff = async (staffData: any) => {
    try {
        const response = await axios.post(`${API_URL}/add`, staffData);
        return {
            success: true,
            data: response.data
        };
    } catch (error) {
        console.error("新增員工失敗:", error);
        return {
            success: false,
            message: error instanceof Error ? error.message : "新增員工時發生錯誤"
        };
    }
};

// 更新員工資料
export const updateStaff = async (staffId: number, staffData: any) => {
    try {
        const response = await axios.put(`${API_URL}/update/${staffId}`, staffData);
        return {
            success: true,
            data: response.data
        };
    } catch (error) {
        console.error(`更新員工 ID ${staffId} 資料失敗:`, error);
        return {
            success: false,
            message: error instanceof Error ? error.message : "更新員工資料時發生錯誤"
        };
    }
};

// 刪除員工
export const deleteStaff = async (staffId: number) => {
    try {
        const response = await axios.delete(`${API_URL}/delete/${staffId}`);
        return {
            success: true,
            data: response.data
        };
    } catch (error) {
        console.error(`刪除員工 ID ${staffId} 失敗:`, error);
        return {
            success: false,
            message: error instanceof Error ? error.message : "刪除員工時發生錯誤"
        };
    }
};

// 批量刪除員工
export const deleteMultipleStaff = async (staffIds: number[]) => {
    try {
        const promises = staffIds.map(id => deleteStaff(id));
        const results = await Promise.all(promises);
        
        const allSuccessful = results.every(result => result.success);
        return {
            success: allSuccessful,
            message: allSuccessful 
                ? "所有員工刪除成功" 
                : "部分員工刪除失敗，請檢查日誌"
        };
    } catch (error) {
        console.error("批量刪除員工失敗:", error);
        return {
            success: false,
            message: error instanceof Error ? error.message : "批量刪除員工時發生錯誤"
        };
    }
};

// 獲取所有分店
export const getAllStores = async () => {
    try {
        const response = await axios.get(`${API_URL}/stores`);
        return {
            success: true,
            data: response.data
        };
    } catch (error) {
        console.error("獲取分店列表失敗:", error);
        return {
            success: false,
            data: []
        };
    }
};

// 獲取所有權限等級
export const getAllPermissions = async () => {
    try {
        const response = await axios.get(`${API_URL}/permissions`);
        return {
            success: true,
            data: response.data
        };
    } catch (error) {
        console.error("獲取權限列表失敗:", error);
        return {
            success: false,
            data: []
        };
    }
};

// 導出員工列表為 Excel (可在後端實現)
export const exportStaffToExcel = async (filters = {}) => {
    try {
        const response = await axios.get(`${API_URL}/export`, {
            params: filters,
            responseType: 'blob'
        });
        
        return {
            success: true,
            data: response.data
        };
    } catch (error) {
        console.error("導出員工列表失敗:", error);
        return {
            success: false,
            message: error instanceof Error ? error.message : "導出員工列表時發生錯誤"
        };
    }
}; 