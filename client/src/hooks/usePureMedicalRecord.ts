// .\src\hooks\usePureMedicalRecord.ts
import { useState, useEffect, useCallback } from 'react';
import { 
  getAllPureRecords, 
  searchPureRecords, 
  deletePureRecord, 
  exportPureRecords,
  PureMedicalRecord 
} from '../services/PureMedicalRecordService';

/**
 * 淨化健康紀錄 Hook 的返回類型
 */
interface UsePureMedicalRecordReturn {
  records: PureMedicalRecord[];
  loading: boolean;
  error: string | null;
  searchKeyword: string;
  setSearchKeyword: (keyword: string) => void;
  selectedIds: number[];
  handleCheckboxChange: (id: number, checked: boolean) => void;
  handleSearch: () => Promise<void>;
  handleDelete: () => Promise<void>;
  handleExport: () => Promise<void>;
  refreshData: () => Promise<void>;
}

/**
 * 淨化健康紀錄管理 Hook
 * @returns 包含淨化健康紀錄資料和操作方法的對象
 */
export const usePureMedicalRecord = (): UsePureMedicalRecordReturn => {
  const [records, setRecords] = useState<PureMedicalRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchKeyword, setSearchKeyword] = useState<string>("");
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  /**
   * 獲取所有淨化健康紀錄
   */
  const fetchRecords = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getAllPureRecords();
      setRecords(data);
      setError(null);
    } catch (err) {
      console.error("Error fetching pure medical records:", err);
      setError("無法獲取淨化健康紀錄");
    } finally {
      setLoading(false);
    }
  }, []);

  // 初始加載數據
  useEffect(() => {
    fetchRecords();
  }, [fetchRecords]);

  /**
   * 處理搜尋
   */
  const handleSearch = async () => {
    try {
      setLoading(true);
      if (searchKeyword.trim() === "") {
        const data = await getAllPureRecords();
        setRecords(data);
      } else {
        const data = await searchPureRecords(searchKeyword);
        setRecords(data);
      }
      setError(null);
    } catch (err) {
      console.error("Error searching pure medical records:", err);
      setError("搜尋淨化健康紀錄時發生錯誤");
    } finally {
      setLoading(false);
    }
  };

  /**
   * 處理勾選框狀態變更
   */
  const handleCheckboxChange = (id: number, checked: boolean) => {
    if (checked) {
      setSelectedIds([...selectedIds, id]);
    } else {
      setSelectedIds(selectedIds.filter(selectedId => selectedId !== id));
    }
  };

  /**
   * 處理刪除所選紀錄
   */
  const handleDelete = async () => {
    if (selectedIds.length === 0) {
      alert("請至少選擇一筆資料");
      return;
    }

    if (window.confirm(`確定要刪除選取的 ${selectedIds.length} 筆資料嗎？`)) {
      try {
        setLoading(true);
        await Promise.all(selectedIds.map(id => deletePureRecord(id)));
        
        // 刷新資料
        await fetchRecords();
        setSelectedIds([]);
        alert("刪除成功");
      } catch (err) {
        console.error("Error deleting pure medical records:", err);
        setError("刪除淨化健康紀錄時發生錯誤");
      } finally {
        setLoading(false);
      }
    }
  };

  /**
   * 處理匯出
   */
  const handleExport = async () => {
    try {
      setLoading(true);
      const blob = await exportPureRecords();
      
      // 創建下載連結
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = '淨化健康紀錄.xlsx';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Error exporting pure medical records:", err);
      setError("匯出淨化健康紀錄時發生錯誤");
    } finally {
      setLoading(false);
    }
  };

  /**
   * 刷新數據
   */
  const refreshData = async () => {
    await fetchRecords();
  };

  return {
    records,
    loading,
    error,
    searchKeyword,
    setSearchKeyword,
    selectedIds,
    handleCheckboxChange,
    handleSearch,
    handleDelete,
    handleExport,
    refreshData
  };
}; 