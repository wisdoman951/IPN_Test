import React from "react";
import { Button, Container, Row, Col } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import IconButton from "../../components/IconButton";

const BranchBackend: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div className="d-flex flex-column min-vh-100 bg-white">
            {/* Header */}
            <header className="d-flex justify-content-between align-items-center bg-info px-4 py-3 app-header">
                <h1 className="text-white fw-bold fs-3 m-0">分店後台管理系統 (1.1.5)</h1>
                <div className="d-flex gap-3">
                    <IconButton.HomeButton onClick={() => navigate("/")} />
                    <IconButton.CloseButton onClick={() => navigate(-1)} />
                </div>
            </header>

            <Container className="d-flex flex-column justify-content-center" style={{ minHeight: "calc(100vh - 100px)" }}>
                <Col xs={12} md={8} className="ms-auto">
                
                {/* 功能按鈕 */}
                <Row className="justify-content-center g-3">
                    <Col xs={12} sm={6} md={4} className="d-grid">
                        <Button onClick={() => navigate("/backend/staff")} variant="info" size="lg" className="text-white px-4 py-2">員工資料</Button>
                    </Col>
                    <Col xs={12} sm={6} md={4} className="d-grid">
                        <Button variant="info" size="lg" className="text-white px-4 py-2">其他</Button>
                    </Col>
                </Row>
                </Col>
            </Container>
        </div>
    );
};

export default BranchBackend;
