/**
 * 認證與用戶信息相關的工具函數
 */

/**
 * 獲取當前用戶的商店ID
 * 如果用戶未登錄或沒有商店信息，返回默認值1（可根據需求調整）
 */
export const getStoreId = (): number => {
    try {
        // 嘗試從本地存儲獲取用戶信息
        const userInfo = localStorage.getItem('userInfo');
        if (userInfo) {
            const userData = JSON.parse(userInfo);
            if (userData && userData.store_id) {
                return userData.store_id;
            }
        }
        
        // 如果無法獲取用戶商店ID，使用默認值
        // 在實際生產環境中，應該有更好的處理機制
        console.warn("無法從本地存儲獲取商店ID，使用默認值 1");
        return 1;
    } catch (error) {
        console.error("獲取商店ID時出錯:", error);
        return 1; // 出錯時返回默認值
    }
};

/**
 * 獲取當前用戶的認證令牌
 */
export const getAuthToken = (): string | null => {
    try {
        return localStorage.getItem('token');
    } catch (error) {
        console.error("獲取認證令牌時出錯:", error);
        return null;
    }
};

/**
 * 檢查用戶是否已登錄
 */
export const isLoggedIn = (): boolean => {
    return !!getAuthToken();
}; 