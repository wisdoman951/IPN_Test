import { useState } from "react";
import { Button, Form, Row, Col, Container, Alert } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import Header from "../../components/Header";
import DynamicContainer from "../../components/DynamicContainer";
import MemberColumn from "../../components/MemberColumn";
import { addTherapyRecord } from "../../services/TherapyService";
import { getTodayDateString, validateTherapyRecord } from "../../utils/therapyUtils";

interface MemberData {
    member_id: number;
    name: string;
    // 其他會員數據
}

const AddTherapyRecord = () => {
    const navigate = useNavigate();
    const [error, setError] = useState<string | null>(null);
    const [memberDetails, setMemberDetails] = useState<MemberData | null>(null);
    const [loading, setLoading] = useState(false);

    const [form, setForm] = useState({
        memberId: "",
        memberName: "",
        remainingSessions: "",
        treatmentDate: getTodayDateString(),
        plan: "", // 現階段沒有送出，可日後加強
        therapist: "",
        product: "",
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setForm({ ...form, [name]: value });
    };

    const handleMemberChange = (memberId: string, name: string, memberData: MemberData | null) => {
        setForm(prev => ({
            ...prev,
            memberId,
            memberName: name
        }));
        setMemberDetails(memberData);
        
        // 當找到有效會員，清除錯誤訊息
        if (memberData && error && error.includes('會員')) {
            setError(null);
        }
    };

    const handleError = (errorMessage: string) => {
        setError(errorMessage);
    };

    const handleSubmit = async () => {
        // 使用驗證工具函數進行驗證
        const validationError = validateTherapyRecord({
            member_id: form.memberId,
            date: form.treatmentDate,
            staff_id: form.therapist
        });
        
        if (validationError) {
            setError(validationError);
            return;
        }
        
        // 額外的驗證
        if (form.memberName.includes('未找到會員')) {
            setError("請輸入有效的會員資料");
            return;
        }

        try {
            setLoading(true);
            await addTherapyRecord({
                member_id: parseInt(form.memberId),
                date: form.treatmentDate,
                staff_id: parseInt(form.therapist),
                note: `產品ID: ${form.product}, 剩餘療程: ${form.remainingSessions}, 方案: ${form.plan}`
            });

            alert("新增成功！");
            navigate("/therapy-record"); // 導回療程紀錄列表頁
        } catch (error) {
            console.error("新增失敗：", error);
            setError("新增療程紀錄時發生錯誤");
        } finally {
            setLoading(false);
        }
    };

    // 渲染表單內容
    const content = (
        <Container className="py-4">
            <Form>
                {error && (
                    <Alert variant="danger" dismissible onClose={() => setError(null)}>
                        {error}
                    </Alert>
                )}
                
                {/* 使用MemberColumn組件替代原本的會員ID和姓名欄位 */}
                <MemberColumn 
                    memberId={form.memberId}
                    name={form.memberName}
                    onMemberChange={handleMemberChange}
                    onError={handleError}
                />
                
                <Row>
                    <Col md={6}>
                        <Form.Group className="mb-3">
                            <Form.Label>療程剩餘數</Form.Label>
                            <Form.Control
                                type="text"
                                name="remainingSessions"
                                value={form.remainingSessions}
                                onChange={handleChange}
                            />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>療程日期</Form.Label>
                            <Form.Control
                                type="date"
                                name="treatmentDate"
                                value={form.treatmentDate}
                                onChange={handleChange}
                                required
                            />
                        </Form.Group>
                    </Col>
                    <Col md={6}>
                        <Form.Group className="mb-3">
                            <Form.Label>方案</Form.Label>
                            <Form.Control
                                type="text"
                                name="plan"
                                value={form.plan}
                                onChange={handleChange}
                            />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>療癒師（ID）</Form.Label>
                            <Form.Control
                                type="text"
                                name="therapist"
                                value={form.therapist}
                                onChange={handleChange}
                                required
                            />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label>產品（ID）</Form.Label>
                            <Form.Control
                                type="text"
                                name="product"
                                value={form.product}
                                onChange={handleChange}
                            />
                        </Form.Group>
                    </Col>
                </Row>
                <div className="d-flex gap-3 mt-4">
                    <div className="d-flex gap-3 ms-auto">
                        <Button 
                            variant="info" 
                            className="text-white" 
                            onClick={handleSubmit}
                            disabled={loading}
                        >
                            {loading ? "處理中..." : "確認"}
                        </Button>
                        <Button 
                            variant="secondary" 
                            onClick={() => navigate(-1)}
                            disabled={loading}
                        >
                            取消
                        </Button>
                        <Button 
                            variant="outline-info" 
                            onClick={() => window.print()}
                            disabled={loading}
                        >
                            列印
                        </Button>
                    </div>
                </div>
            </Form>
        </Container>
    );

    return (
        <>
            <Header title="新增療程紀錄 1.1.1.3.1" />
            <DynamicContainer content={content} />
        </>
    );
};

export default AddTherapyRecord;
