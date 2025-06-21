// ./src/services/ProductSellService.ts
import axios from "axios";
import { base_url } from "./BASE_URL";

const API_URL = `${base_url}/api/product-sell`;

// 產品介面 (保持不變)
export interface Product {
    product_id: number;
    product_name: string;
    product_price: number;
    inventory_id: number;
    quantity: number;
}

// 產品銷售記錄介面 - 更新以匹配 Figma
export interface ProductSellData {
  product_id: number;
  member_id: number;
  staff_id?: number;
  store_id: number;
  date?: string;
  payment_method?: string;
  transfer_code?: string; // 根據付款方式選擇性傳遞
  card_number?: string;   // 根據付款方式選擇性傳遞
  sale_category?: string;
  quantity: number;
  note?: string;

  // 價格相關欄位，直接傳遞給後端寫入 product_sell 表
  unit_price: number;         // 該產品的銷售單價
  discount_amount: number;   // 針對此銷售項目的折扣金額 (由前端計算並傳遞)
  final_price: number;        // 此銷售項目的最終價格 (unit_price * quantity - discount_amount)
  inventory_id_for_stock_update?: number; // 或者用一個更明確的名稱，表示此 ID 僅用於庫存更新
}

// 新增產品銷售的資料介面 (保持不變或按需調整)
export interface ProductSellData {
    product_id?: number;
    member_id?: number;
    staff_id?: number; // 如果提交的是銷售人員ID
    store_id: number;
    date?: string;
    payment_method?: string;
    transfer_code?: string;
    card_number?: string;
    sale_category?: string;
    inventory_id: number;
    quantity: number;
    note?: string;
    discount?: number; // 如果前端計算折扣並提交
    // 新增欄位如果需要提交
    // staff_name?: string; // 如果提交的是銷售人員名稱
}

// 獲取所有產品及庫存
export const getAllProducts = async (): Promise<Product[]> => {
    try {
        const response = await axios.get(`${API_URL}/products`);
        if (Array.isArray(response.data)) {
            // 新增 map 來統一資料格式
            const formattedData = response.data.map((p: any) => ({
                product_id: p.product_id,
                product_name: p.product_name || p.name, // 兼容 name 和 product_name
                product_price: p.product_price || p.price, // 兼容 price 和 product_price
                inventory_id: p.inventory_id || 0, // 提供預設值
                quantity: p.quantity || 0, // 提供預設值
            }));
            return formattedData;
        }
        return []; // 如果返回的不是陣列，返回空陣列
    } catch (error) {
        console.error("獲取產品列表失敗：", error);
        throw error;
    }
};

// 搜尋產品及庫存
export const searchProducts = async (keyword: string): Promise<Product[]> => {
    try {
        const response = await axios.get(`${API_URL}/products/search`, {
            params: { keyword }
        });
        return response.data;
    } catch (error) {
        console.error("搜尋產品失敗：", error);
        throw error;
    }
};

// 新增產品銷售記錄
export const addProductSell = async (data: ProductSellData) => {
    try {
        console.log("提交產品銷售資料:", data);
        const response = await axios.post(`${API_URL}/add`, data);
        console.log("新增產品銷售響應:", response.data);
        return response.data;
    } catch (error) {
        console.error("新增產品銷售失敗：", error);
        throw error;
    }
};

// 獲取所有產品銷售記錄
export const getAllProductSells = async (): Promise<ProductSell[]> => {
    const response = await axios.get(`${API_URL}/list`);
    return response.data as ProductSell[]; // 確保 API 返回的數據符合更新後的 ProductSell 結構
};

// 搜尋產品銷售記錄
export const searchProductSells = async (keyword: string): Promise<ProductSell[]> => {
    const response = await axios.get(`${API_URL}/search`, {
        params: { keyword }
    });
    return response.data;
};

// 根據 ID 獲取產品銷售記錄詳情
export const getProductSellById = async (saleId: number): Promise<ProductSell> => {
    const response = await axios.get(`${API_URL}/detail/${saleId}`);
    return response.data;
};

// 更新產品銷售記錄
export const updateProductSell = async (saleId: number, data: ProductSellData) => {
    return axios.put(`${API_URL}/update/${saleId}`, data);
};

// 刪除產品銷售記錄
export const deleteProductSell = async (saleId: number) => {
    return axios.delete(`${API_URL}/delete/${saleId}`);
};

// 匯出產品銷售記錄
export const exportProductSells = async (): Promise<Blob> => {
    const response = await axios.get(`${API_URL}/export`, {
        responseType: "blob"
    });
    return response.data;
}; 