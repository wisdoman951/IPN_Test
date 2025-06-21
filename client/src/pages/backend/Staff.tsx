import React, { useState, useEffect } from "react";
import { Button, Container, Row, Col, Form, Table, Spinner, Modal, Alert } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import IconButton from "../../components/IconButton";
import { getAllStaff, searchStaff, deleteMultipleStaff, Staff as StaffType } from "../../services/StaffService";

// 定義 mock 數據
const MOCK_STAFF_DATA: StaffType[] = [
    { Staff_ID: 1, Staff_Name: "黃怡君", Staff_Phone: "0911111111", Staff_Sex: "女", Staff_Status: "在職", Staff_ID_Number: "A123456789" },
    { Staff_ID: 2, Staff_Name: "陳信宏", Staff_Phone: "0922222222", Staff_Sex: "男", Staff_Status: "在職", Staff_ID_Number: "B234567890" },
    { Staff_ID: 3, Staff_Name: "林佳蓉", Staff_Phone: "0933333333", Staff_Sex: "女", Staff_Status: "在職", Staff_ID_Number: "C345678901" },
    { Staff_ID: 4, Staff_Name: "周柏宇", Staff_Phone: "0944444444", Staff_Sex: "男", Staff_Status: "在職", Staff_ID_Number: "D456789012" },
    { Staff_ID: 5, Staff_Name: "徐書芸", Staff_Phone: "0955555555", Staff_Sex: "女", Staff_Status: "在職", Staff_ID_Number: "E567890123" },
    { Staff_ID: 6, Staff_Name: "吳宗憲", Staff_Phone: "0966666666", Staff_Sex: "男", Staff_Status: "在職", Staff_ID_Number: "F678901234" },
    { Staff_ID: 7, Staff_Name: "楊雅雯", Staff_Phone: "0977777777", Staff_Sex: "女", Staff_Status: "在職", Staff_ID_Number: "G789012345" },
    { Staff_ID: 8, Staff_Name: "張宏志", Staff_Phone: "0988888888", Staff_Sex: "男", Staff_Status: "在職", Staff_ID_Number: "H890123456" },
    { Staff_ID: 9, Staff_Name: "朱雅婷", Staff_Phone: "0999999999", Staff_Sex: "女", Staff_Status: "在職", Staff_ID_Number: "I901234567" },
    { Staff_ID: 10, Staff_Name: "簡志強", Staff_Phone: "0910000000", Staff_Sex: "男", Staff_Status: "在職", Staff_ID_Number: "J012345678" }
];

// 定義員工職位
const STAFF_POSITIONS = {
    1: "芳療師",
    2: "課程顧問",
    3: "美容師",
    4: "櫃檯人員",
    5: "芳療師",
    6: "課程顧問",
    7: "櫃檯人員",
    8: "營運主管",
    9: "美容師",
    10: "店長"
};

const Staff: React.FC = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [staffList, setStaffList] = useState<StaffType[]>([]);
    const [keyword, setKeyword] = useState("");
    const [selectedStaff, setSelectedStaff] = useState<number[]>([]);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    
    // 載入員工數據 - 使用 mock 數據而不是 API
    useEffect(() => {
        fetchStaffList();
    }, []);
    
    // 使用本地 mock 數據而非 API
    const fetchStaffList = async () => {
        try {
            setLoading(true);
            setError("");
            
            // 短暫延遲以模擬 API 呼叫
            setTimeout(() => {
                setStaffList(MOCK_STAFF_DATA);
                setLoading(false);
            }, 500);
        } catch (err) {
            console.error("獲取員工列表時發生錯誤:", err);
            setError("載入員工資料時發生錯誤");
            setStaffList([]);
            setLoading(false);
        }
    };
    
    // 處理搜索 - 在本地 mock 數據中搜索
    const handleSearch = async () => {
        try {
            setLoading(true);
            setError("");
            
            if (keyword.trim() === "") {
                await fetchStaffList();
                return;
            }
            
            // 本地搜索而非 API 呼叫
            setTimeout(() => {
                const filteredStaff = MOCK_STAFF_DATA.filter(staff => 
                    staff.Staff_Name.includes(keyword) || 
                    staff.Staff_Phone?.includes(keyword) ||
                    staff.Staff_ID.toString().includes(keyword) ||
                    staff.Staff_ID_Number?.includes(keyword)
                );
                setStaffList(filteredStaff);
                setLoading(false);
            }, 300);
        } catch (err) {
            console.error("搜尋員工時發生錯誤:", err);
            setError("搜尋員工時發生錯誤");
            setLoading(false);
        }
    };
    
    // 處理勾選
    const handleCheckboxChange = (staffId: number) => {
        setSelectedStaff(prev => {
            if (prev.includes(staffId)) {
                return prev.filter(id => id !== staffId);
            } else {
                return [...prev, staffId];
            }
        });
    };
    
    // 處理全選
    const handleSelectAll = () => {
        if (selectedStaff.length === staffList.length) {
            setSelectedStaff([]);
        } else {
            setSelectedStaff(staffList.map(staff => staff.Staff_ID));
        }
    };
    
    // 處理刪除
    const handleDelete = async () => {
        if (selectedStaff.length === 0) {
            setError("請先選擇要刪除的員工");
            return;
        }
        
        setShowDeleteModal(true);
    };
    
    // 確認刪除
    const confirmDelete = async () => {
        try {
            setLoading(true);
            
            const response = await deleteMultipleStaff(selectedStaff);
            if (response.success) {
                alert("刪除成功");
                setSelectedStaff([]);
                await fetchStaffList();
            } else {
                setError(`刪除失敗: ${response.message}`);
            }
        } catch (err) {
            console.error("刪除員工時發生錯誤:", err);
            setError("刪除員工時發生錯誤");
        } finally {
            setLoading(false);
            setShowDeleteModal(false);
        }
    };
    
    // 處理修改
    const handleEdit = () => {
        if (selectedStaff.length !== 1) {
            setError("請選擇一個員工進行修改");
            return;
        }
        
        navigate(`/backend/edit-staff/${selectedStaff[0]}`);
    };
    
    // 處理匯出報表
    const handleExport = () => {
        alert("匯出功能待實現");
    };

    // 獲取員工職位
    const getStaffPosition = (staffId: number) => {
        return STAFF_POSITIONS[staffId as keyof typeof STAFF_POSITIONS] || "未知";
    };

    return (
        <div className="d-flex flex-column min-vh-100 bg-white">
            {/* Header */}
            <header className="d-flex justify-content-between align-items-center bg-info px-4 py-3 app-header">
                <h1 className="text-white fw-bold fs-3 m-0">分店後台管理-員工資料 (1.1.5.1)</h1>
                <div className="d-flex gap-3">
                    <IconButton.HomeButton onClick={() => navigate('/')} />
                    <IconButton.CloseButton onClick={() => navigate(-1)} />
                </div>
            </header>

            <Container className="my-4">
                <Col xs={9} className="ms-auto">
                
                {/* 錯誤提示 */}
                {error && (
                    <Alert variant="danger" onClose={() => setError("")} dismissible>
                        {error}
                    </Alert>
                )}
                
                {/* 搜尋欄位 */}
                <Row className="align-items-center mb-3">
                    <Col xs="auto">
                        <Form.Label className="fw-semibold">姓名/手機號碼/編號/身分證字號</Form.Label>
                    </Col>
                    <Col xs={12} md={4}>
                        <Form.Control 
                            type="text" 
                            placeholder="輸入關鍵字搜尋" 
                            value={keyword}
                            onChange={(e) => setKeyword(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        />
                    </Col>
                    <Col xs="auto">
                        <Button 
                            variant="info" 
                            className="text-white px-4"
                            onClick={handleSearch}
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <Spinner animation="border" size="sm" />
                                    <span className="ms-2">搜尋中...</span>
                                </>
                            ) : "搜尋"}
                        </Button>
                    </Col>
                    <Col xs="auto">
                        <Button 
                            onClick={() => navigate("/backend/add-staff")} 
                            variant="info" 
                            className="text-white px-4"
                            disabled={loading}
                        >
                            新增
                        </Button>
                    </Col>
                </Row>

                {/* 表格 */}
                <Row>
                    <Col>
                        <Table bordered hover responsive>
                            <thead className="text-center">
                                <tr>
                                    <th>
                                        <Form.Check
                                            type="checkbox"
                                            checked={selectedStaff.length === staffList.length && staffList.length > 0}
                                            onChange={handleSelectAll}
                                            disabled={loading || staffList.length === 0}
                                        />
                                    </th>
                                    <th>編號</th>
                                    <th>姓名</th>
                                    <th>身分證字號</th>
                                    <th>手機號碼</th>
                                    <th>性別</th>
                                    <th>職位</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr>
                                        <td colSpan={7} className="text-center py-4">
                                            <Spinner animation="border" />
                                            <span className="ms-2">加載中...</span>
                                        </td>
                                    </tr>
                                ) : staffList.length === 0 ? (
                                    <tr>
                                        <td colSpan={7} className="text-center text-muted py-5">
                                            尚無資料
                                        </td>
                                    </tr>
                                ) : (
                                    staffList.map(staff => (
                                        <tr key={staff.Staff_ID}>
                                            <td className="text-center">
                                                <Form.Check
                                                    type="checkbox"
                                                    checked={selectedStaff.includes(staff.Staff_ID)}
                                                    onChange={() => handleCheckboxChange(staff.Staff_ID)}
                                                    disabled={loading}
                                                />
                                            </td>
                                            <td className="text-center">{staff.Staff_ID}</td>
                                            <td>{staff.Staff_Name}</td>
                                            <td>{staff.Staff_ID_Number || "-"}</td>
                                            <td>{staff.Staff_Phone || "-"}</td>
                                            <td className="text-center">{staff.Staff_Sex || "-"}</td>
                                            <td className="text-center">
                                                {getStaffPosition(staff.Staff_ID)}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </Table>
                    </Col>
                </Row>

                {/* 下方按鈕 */}
                <Row className="justify-content-center my-4 g-3">
                    <Col xs="auto" className="ms-auto">
                        <Button 
                            variant="info" 
                            className="text-white px-4"
                            onClick={handleExport}
                            disabled={loading || staffList.length === 0}
                        >
                            報表匯出
                        </Button>
                    </Col>
                    <Col xs="auto">
                        <Button 
                            variant="info" 
                            className="text-white px-4"
                            onClick={handleDelete}
                            disabled={loading || selectedStaff.length === 0}
                        >
                            刪除
                        </Button>
                    </Col>
                    <Col xs="auto">
                        <Button 
                            variant="info" 
                            className="text-white px-4"
                            onClick={handleEdit}
                            disabled={loading || selectedStaff.length !== 1}
                        >
                            修改
                        </Button>
                    </Col>
                    <Col xs="auto">
                        <Button 
                            variant="info" 
                            className="text-white px-4"
                            onClick={() => navigate(-1)}
                            disabled={loading}
                        >
                            返回
                        </Button>
                    </Col>
                </Row>
                </Col>
            </Container>
            
            {/* 刪除確認對話框 */}
            <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
                <Modal.Header closeButton>
                    <Modal.Title>確認刪除</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    確定要刪除選定的 {selectedStaff.length} 名員工嗎？此操作無法撤銷。
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={() => setShowDeleteModal(false)} disabled={loading}>
                        取消
                    </Button>
                    <Button variant="danger" onClick={confirmDelete} disabled={loading}>
                        {loading ? (
                            <>
                                <Spinner animation="border" size="sm" />
                                <span className="ms-2">處理中...</span>
                            </>
                        ) : "確定刪除"}
                    </Button>
                </Modal.Footer>
            </Modal>
        </div>
    );
};

export default Staff;
