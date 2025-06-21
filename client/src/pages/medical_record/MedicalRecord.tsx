import React from "react";
import { Button, Form, Row, Col } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import Header from "../../components/Header";
import DynamicContainer from "../../components/DynamicContainer";
import ScrollableTable from "../../components/ScrollableTable";
import { useMedicalRecordManagement, HealthRecordIndex } from "../../hooks/useMedicalRecord";
import { formatMedicalHistory, formatMicroSurgery } from "../../utils/medicalUtils";
import "./medicalRecord.css";

const MedicalRecord: React.FC = () => {
    const navigate = useNavigate();
    const { 
        records, 
        searchValue, 
        setSearchValue, 
        selectedIds, 
        handleCheckboxChange, 
        handleDelete, 
        handleSearch, 
        handleExport,
    } = useMedicalRecordManagement();

    // 定義表格標頭
    const tableHeader = (
        <tr>
            <th>勾選</th>
            <th>姓名</th>
            <th>會員編號</th>
            <th>身高</th>
            <th>體重</th>
            <th>血壓</th>
            <th>病史</th>
            <th>微整型</th>
            <th>備註</th>
        </tr>
    );
    // 新增處理修改按鈕點擊的函數
    const handleEdit = () => {
        if (selectedIds.length === 1) {
            // 將使用者導航到編輯頁面，並帶上紀錄的 ID
            navigate(`/medical-record/edit/${selectedIds[0]}`);
        }
    };
    // 定義表格內容
    const tableBody = (
        records.length > 0 ? (
            records.map((r) => (
                <tr key={r[HealthRecordIndex.ID]}>
                    <td>
                        <Form.Check
                            type="checkbox"
                            checked={selectedIds.includes(r[HealthRecordIndex.ID])}
                            onChange={(e) => handleCheckboxChange(r[HealthRecordIndex.ID], e.target.checked)}
                        />
                    </td>
                    <td>{r[HealthRecordIndex.NAME] || "-"}</td>
                    <td>{r[HealthRecordIndex.MEMBER_ID]}</td>
                    <td>{r[HealthRecordIndex.HEIGHT]}</td>
                    <td>{r[HealthRecordIndex.WEIGHT]}</td>
                    <td>{r[HealthRecordIndex.BLOOD_PRESSURE]}</td>
                    <td>{formatMedicalHistory(r[HealthRecordIndex.MEDICAL_HISTORY])}</td>
                    <td>{formatMicroSurgery(r[HealthRecordIndex.MICRO_SURGERY])}</td>
                    <td>{r[HealthRecordIndex.MICRO_SURGERY_NOTES]}</td>
                </tr>
            ))
        ) : (
            <tr>
                <td colSpan={9} className="text-muted">
                    無資料
                </td>
            </tr>
        )
    );

    // 定義頁面內容
    const content = (
        <div className="w-100">
            {/* 搜索區域 */}
            <div className="search-area mb-4">
                <Row className="align-items-center">
                    <Col md={6} className="mb-3 mb-md-0">
                        <Form.Control
                            type="text"
                            placeholder="姓名/電話/編號"
                            value={searchValue}
                            onChange={(e) => setSearchValue(e.target.value)}
                        />
                    </Col>
                    <Col md={6} className="d-flex justify-content-end gap-2">
                        <Button variant="info" className="text-white" onClick={handleSearch}>搜尋</Button>
                        <Button variant="info" className="text-white" onClick={() => navigate("/medical-record/add-medical-record")}>
                            新增
                        </Button>
                    </Col>
                </Row>
            </div>

            {/* 使用 ScrollableTable 元件 */}
            <ScrollableTable
                tableHeader={tableHeader}
                tableBody={tableBody}
                tableProps={{ bordered: true, hover: true, responsive: true, className: "text-center" }}
            />

            {/* 底部按鈕區域 */}
            <div className="button-area mt-4">
                <Row className="justify-content-end g-3">
                    <Col xs="auto">
                        <Button variant="info" className="text-white" onClick={handleExport}>報表匯出</Button>
                    </Col>
                    <Col xs="auto">
                        <Button variant="info" className="text-white" onClick={handleDelete}>刪除</Button>
                    </Col>
                    <Col xs="auto">
                        {/* 修改此按鈕 */}
                        <Button 
                            variant="info" 
                            className="text-white"
                            onClick={handleEdit}
                            disabled={selectedIds.length !== 1} // <--- 當勾選數量不為 1 時禁用
                        >
                            修改
                        </Button>
                    </Col>
                    <Col xs="auto">
                        <Button variant="info" className="text-white">確認</Button>
                    </Col>
                </Row>
            </div>
        </div>
    );

    return (
        <div className="d-flex flex-column min-vh-100 bg-white">
            {/* 使用 Header 元件 */}
            <Header title="健康檢查紀錄 1.1.1.2" />
            
            {/* 使用 DynamicContainer */}
            <DynamicContainer content={content} className="p-4 align-items-start" />
        </div>
    );
};

export default MedicalRecord;
