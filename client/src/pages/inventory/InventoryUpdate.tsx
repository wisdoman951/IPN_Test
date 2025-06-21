import React, { useState } from "react";
import { Button, Container, Row, Col, Form, Table } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import IconButton from "../../components/IconButton";

// 定義庫存項目接口
interface InventoryItem {
    id: number;
    name: string;
    category: string;
    currentStock: number;
    supplier: string;
    lastUpdateDate: string;
}

const InventoryUpdate: React.FC = () => {
    const navigate = useNavigate();
    const [searchKeyword, setSearchKeyword] = useState("");
    const [selectedItems, setSelectedItems] = useState<number[]>([]);
    
    // 模擬數據
    const mockInventoryItems: InventoryItem[] = [
        {
            id: 1001,
            name: "精油A",
            category: "精油",
            currentStock: 25,
            supplier: "ABC供應商",
            lastUpdateDate: "2024-05-15"
        },
        {
            id: 1002,
            name: "面膜B",
            category: "面膜",
            currentStock: 50,
            supplier: "優質美容用品",
            lastUpdateDate: "2024-05-12"
        },
        {
            id: 1003,
            name: "按摩油C",
            category: "按摩用品",
            currentStock: 18,
            supplier: "健康生活",
            lastUpdateDate: "2024-05-10"
        },
        {
            id: 1004,
            name: "精華液D",
            category: "保養品",
            currentStock: 30,
            supplier: "美麗肌膚",
            lastUpdateDate: "2024-05-05"
        },
        {
            id: 1005,
            name: "香薰爐E",
            category: "設備",
            currentStock: 7,
            supplier: "ABC供應商",
            lastUpdateDate: "2024-04-28"
        }
    ];
    
    // 處理勾選項目
    const handleCheckboxChange = (id: number) => {
        setSelectedItems(prev => {
            if (prev.includes(id)) {
                return prev.filter(item => item !== id);
            } else {
                return [...prev, id];
            }
        });
    };
    
    // 處理搜尋
    const handleSearch = () => {
        console.log("搜尋關鍵字:", searchKeyword);
        // 實際應用會在這裡進行過濾或API呼叫
    };

    return (
        <div className="d-flex flex-column min-vh-100 bg-white">
            {/* Header */}
            <header className="d-flex justify-content-between align-items-center bg-info px-4 py-3 app-header">
                <h1 className="text-white fw-bold fs-3 m-0">更新庫存數據 1.1.4.3</h1>
                <div className="d-flex gap-3">
                    <IconButton.HomeButton onClick={() => navigate('/')} />
                    <IconButton.CloseButton onClick={() => navigate(-1)} />
                </div>
            </header>

            <Container className="my-4">
                <Col xs={9} className="ms-auto">
                
                {/* 搜尋欄位 */}
                <Row className="align-items-center mb-3">
                    <Col xs="auto">
                        <Form.Label className="fw-semibold">品項</Form.Label>
                    </Col>
                    <Col xs={12} md={4}>
                        <Form.Control 
                            type="text" 
                            placeholder="輸入品項名稱或類別" 
                            value={searchKeyword}
                            onChange={(e) => setSearchKeyword(e.target.value)}
                        />
                    </Col>
                    <Col xs="auto">
                        <Button 
                            variant="info" 
                            className="text-white px-4"
                            onClick={handleSearch}
                        >
                            搜尋
                        </Button>
                    </Col>
                    <Col xs="auto">
                        <Button 
                            onClick={() => navigate("/inventory/inventory-add")} 
                            variant="info" 
                            className="text-white px-4"
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
                                    <th>勾選</th>
                                    <th>品項ID</th>
                                    <th>品項名稱</th>
                                    <th>類別</th>
                                    <th>目前庫存</th>
                                    <th>供應商</th>
                                    <th>最後更新日期</th>
                                    <th>進貨</th>
                                    <th>出貨</th>
                                    <th>借貸/借貨人姓名</th>
                                </tr>
                            </thead>
                            <tbody>
                                {mockInventoryItems.length === 0 ? (
                                    <tr>
                                        <td colSpan={10} className="text-center text-muted py-5">
                                            尚無資料
                                        </td>
                                    </tr>
                                ) : (
                                    mockInventoryItems.map(item => (
                                        <tr key={item.id}>
                                            <td className="text-center">
                                                <Form.Check 
                                                    type="checkbox"
                                                    checked={selectedItems.includes(item.id)}
                                                    onChange={() => handleCheckboxChange(item.id)}
                                                />
                                            </td>
                                            <td className="text-center">{item.id}</td>
                                            <td>{item.name}</td>
                                            <td>{item.category}</td>
                                            <td className="text-center">{item.currentStock}</td>
                                            <td>{item.supplier}</td>
                                            <td>{item.lastUpdateDate}</td>
                                            <td>
                                                <Form.Control 
                                                    type="number" 
                                                    min="0" 
                                                    placeholder="輸入數量"
                                                    size="sm"
                                                />
                                            </td>
                                            <td>
                                                <Form.Control 
                                                    type="number" 
                                                    min="0" 
                                                    max={item.currentStock}
                                                    placeholder="輸入數量"
                                                    size="sm"
                                                />
                                            </td>
                                            <td>
                                                <Form.Control 
                                                    type="text" 
                                                    placeholder="輸入姓名"
                                                    size="sm"
                                                />
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
                        <Button variant="info" className="text-white px-4">報表匯出</Button>
                    </Col>
                    <Col xs="auto">
                        <Button 
                            variant="info" 
                            className="text-white px-4"
                            disabled={selectedItems.length === 0}
                        >
                            刪除
                        </Button>
                    </Col>
                    <Col xs="auto">
                        <Button 
                            variant="info" 
                            className="text-white px-4"
                            disabled={selectedItems.length !== 1}
                        >
                            修改
                        </Button>
                    </Col>
                    <Col xs="auto">
                        <Button variant="info" className="text-white px-4">確認</Button>
                    </Col>
                </Row>
                </Col>
            </Container>
        </div>
    );
};

export default InventoryUpdate;
