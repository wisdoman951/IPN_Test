// client/src/pages/member/MemberInfo.tsx (修改版)

import React from "react"; // 您提供的程式碼中缺少這行，補上
import { Button, Row, Col, Form, Container, Spinner } from "react-bootstrap"; // 新增 Container 和 Spinner
import { useNavigate } from "react-router-dom";
import Header from "../../components/Header";
import DynamicContainer from "../../components/DynamicContainer";
import ScrollableTable from "../../components/ScrollableTable";
import { formatGregorianBirthday, formatGender, calculateAge } from "../../utils/memberUtils";
import { useMemberManagement } from "../../hooks/useMemberManagement";
import "./memberInfo.css";

const MemberInfo: React.FC = () => {
    const navigate = useNavigate();
    const { 
        members, 
        loading, // 假設您的 hook 返回 loading 狀態
        error,   // 假設您的 hook 返回 error 狀態
        keyword, 
        setKeyword, 
        selectedMemberIds, 
        handleCheckboxChange, 
        handleDelete, 
        handleSearch, 
        handleExport 
    } = useMemberManagement();
    
    // 定義表格標頭
    const tableHeader = (
        <tr>
            <th style={{ width: '50px' }}>勾選</th>
            <th>姓名</th>
            <th>編號</th>
            <th>生日</th>
            <th>年齡</th>
            <th>住址</th>
            <th>電話</th>
            <th>性別</th>
            <th>血型</th>
            <th>Line ID</th>
            <th>介紹人</th>
            <th>備註</th>
        </tr>
    );
    
    // 定義表格內容
    const tableBody = loading ? (
        <tr><td colSpan={12} className="text-center py-5"><Spinner animation="border" variant="info" /></td></tr>
    ) : error ? (
        <tr><td colSpan={12} className="text-center text-danger py-5">{error}</td></tr>
    ) : members.length > 0 ? (
        members.map((member) => (
            <tr key={member.Member_ID}>
                <td className="text-center align-middle"> {/* 垂直居中 */}
                    <Form.Check 
                        type="checkbox" 
                        id={`member-${member.Member_ID}`}
                        checked={selectedMemberIds.includes(member.Member_ID)} // 確保 Member_ID 是 number 或 string，與 selectedMemberIds 類型一致
                        onChange={(e) => handleCheckboxChange(member.Member_ID, e.target.checked)}
                    />
                </td>
                <td className="align-middle">{member.Name}</td>
                {/* 假設 Member_ID 是從資料庫來的數字 ID，而 member_code 是 M001 格式的編號 */}
                <td className="align-middle">{member.member_code || String(member.Member_ID).padStart(4, '0')}</td>
                <td className="align-middle">{formatGregorianBirthday(member.Birth, 'YYYY/MM/DD')}</td>
                <td className="align-middle">{calculateAge(member.Birth)}</td>
                <td className="align-middle">{member.Address}</td>
                <td className="align-middle">{member.Phone}</td>
                <td className="align-middle">{formatGender(member.Gender)}</td>
                <td className="align-middle">{member.BloodType}</td>
                <td className="align-middle">{member.LineID}</td>
                <td className="align-middle">{member.Referrer}</td>
                <td className="align-middle">{member.Note}</td>
            </tr>
        ))
    ) : (
        <tr><td colSpan={12} className="text-center text-muted py-5">尚無資料</td></tr>
    );
    
    // 新增：處理修改按鈕的點擊事件
    const handleEdit = () => {
        // 再次確認是否剛好只選取了一項
        if (selectedMemberIds.length === 1) {
            const memberToEditId = selectedMemberIds[0];
            // 導航到我們之前建立的編輯頁面，並將會員ID作為URL參數
            navigate(`/member-info/edit/${memberToEditId}`);
        } else {
            alert("請選擇一筆要修改的資料。");
        }
    };
    
    // 定義頁面內容
    const content = (
        <div className="w-100">
            {/* 搜索區域 */}
            <Container className="my-4"> {/* 使用 Container 來統一邊距 */}
                <Row className="align-items-center">
                    <Col xs={12} md={6} className="mb-3 mb-md-0">
                        <Form.Control
                            type="text"
                            placeholder="姓名/電話/編號"
                            value={keyword}
                            onChange={(e) => setKeyword(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        />
                    </Col>
                    <Col
                        xs={12}
                        md={6}
                        className="d-flex justify-content-end gap-2" // gap-2
                    >
                        <Button
                            variant="info"
                            className="text-white px-4"
                            onClick={handleSearch}
                            disabled={loading}
                        >
                            {loading ? <Spinner as="span" size="sm" /> : "搜尋"}
                        </Button>
                        <Button
                            onClick={() => navigate("/add-member")}
                            variant="success" // 使用不同顏色區分
                            className="text-white px-4"
                            disabled={loading}
                        >
                            新增
                        </Button>
                    </Col>
                </Row>
            </Container>

            {/* 使用可滾動表格組件 */}
            <Container>
                <ScrollableTable
                    tableHeader={tableHeader}
                    tableBody={tableBody}
                    tableProps={{ bordered: true, hover: true }}
                    height="calc(100vh - 350px)" // 根據實際佈局調整高度
                />
            </Container>

            {/* 底部按鈕區域 */}
            <Container className="my-4">
                <Row className="justify-content-end g-3">
                    <Col xs="auto">
                        <Button variant="outline-primary" onClick={handleExport} disabled={loading || members.length === 0}>
                            報表匯出
                        </Button>
                    </Col>
                    <Col xs="auto">
                        <Button variant="danger" className="text-white" onClick={handleDelete} disabled={loading || selectedMemberIds.length === 0}>
                            刪除
                        </Button>
                    </Col>
                    <Col xs="auto">
                        {/* ***** 主要修改點 ***** */}
                        <Button 
                            variant="warning" // 修改按鈕樣式以示區別
                            className="text-dark"
                            onClick={handleEdit} // <--- 綁定事件處理函數
                            disabled={loading || selectedMemberIds.length !== 1} // <--- 設定禁用條件
                        >
                            修改
                        </Button>
                        {/* ***** 結束修改 ***** */}
                    </Col>
                    <Col xs="auto">
                        <Button variant="secondary" onClick={() => navigate("/member-management")}> {/* 假設返回會員管理主頁 */}
                            確認
                        </Button>
                    </Col>
                </Row>
            </Container>
        </div>
    );
    
    return (
        <div className="d-flex flex-column min-vh-100 bg-light">
            <Header title="會員基本資料 1.1.1.1" />
            <DynamicContainer content={content} className="align-items-start p-0" />
        </div>
    );
};

export default MemberInfo;