import React, { useState, useEffect, useRef } from "react";
import { Form, Col, Row } from "react-bootstrap";
import { getMemberById } from "../services/ＭedicalService";
import { calculateAge } from "../utils/memberUtils";

// 定義會員資料類型
interface MemberData {
    member_id: number;
    name: string;
    address: string;
    birthday: string;
    blood_type: string;
    gender: string;
    inferrer_id: number;
    line_id: string;
    note: string;
    occupation: string;
    phone: string;
}

interface MemberColumnProps {
    memberId: string;
    name: string;
    onMemberChange: (memberId: string, name: string, memberData: MemberData | null) => void;
    onError?: (error: string) => void;
}

const MemberColumn: React.FC<MemberColumnProps> = ({ 
    memberId, 
    name, 
    onMemberChange,
    onError,
}) => {
    const [fetchingMember, setFetchingMember] = useState(false);
    const [localMemberId, setLocalMemberId] = useState(memberId);
    const previousMemberIdRef = useRef<string>(memberId);
    const debounceTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const [memberNotFound, setMemberNotFound] = useState(false);
    const [memberData, setMemberData] = useState<MemberData | null>(null);

    // 當 props 中的 memberId 變更時，更新本地狀態
    useEffect(() => {
        if (memberId !== localMemberId) {
            setLocalMemberId(memberId);
        }
    }, [memberId]);

    
    useEffect(() => {
        // 如果 memberId 沒有變化，不執行任何操作
        if (localMemberId === previousMemberIdRef.current || !localMemberId) {
            return;
        }

        // 清除任何現有的 timeout
        if (debounceTimeoutRef.current) {
            clearTimeout(debounceTimeoutRef.current);
        }

        // 設置新的 timeout
        debounceTimeoutRef.current = setTimeout(async () => {
            setFetchingMember(true);
            setMemberNotFound(false);
            
            try {
                previousMemberIdRef.current = localMemberId; // 更新之前查詢的 ID
                
                const member = await getMemberById(localMemberId);
                if (member) {
                    console.log("獲取到的會員資料:", member);
                    setMemberData(member);
                    onMemberChange(localMemberId, member.name, member);
                    setMemberNotFound(false);
                } else {
                    if (onError) onError(`會員編號 ${localMemberId} 不存在，請確認編號是否正確`);
                    setMemberData(null);
                    onMemberChange(localMemberId, "未找到會員 (ID不存在)", null);
                    setMemberNotFound(true);
                }
            } catch (err) {
                console.error("獲取會員資料失敗", err);
                if (onError) onError("獲取會員資料失敗，請確認會員編號是否正確");
                setMemberData(null);
                onMemberChange(localMemberId, "未找到會員 (查詢失敗)", null);
                setMemberNotFound(true);
            } finally {
                setFetchingMember(false);
                debounceTimeoutRef.current = null;
            }
        }, 500);

        // 清理函數
        return () => {
            if (debounceTimeoutRef.current) {
                clearTimeout(debounceTimeoutRef.current);
            }
        };
    }, [localMemberId, onMemberChange, onError]);

    const handleMemberIdChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newMemberId = e.target.value;
        setLocalMemberId(newMemberId);
        
        // 僅當用戶輸入完畢後，才更新父組件的 memberId
        // 減少不必要的狀態更新與渲染
        if (!newMemberId.trim()) {
            setMemberData(null);
            onMemberChange(newMemberId, "", null);
            setMemberNotFound(false);
        }
    };

    return (
        <Row>
            <Col md={6}>
                <Form.Group className="mb-3">
                    <Form.Label>會員編號</Form.Label>
                    <Form.Control
                        type="text"
                        name="memberId"
                        value={localMemberId}
                        onChange={handleMemberIdChange}
                        required
                    />
                    <Form.Control.Feedback type="invalid">
                        請輸入會員編號
                    </Form.Control.Feedback>
                    {fetchingMember && <div className="text-muted">正在獲取會員資料...</div>}
                </Form.Group>
            </Col>
            <Col md={6}>
                <Form.Group className="mb-3">
                    <Form.Label>姓名</Form.Label>
                    <Form.Control
                        type="text"
                        name="name"
                        value={name}
                        disabled={true}
                        style={memberNotFound ? {color: 'red', fontWeight: 'bold'} : {}}
                        required
                    />
                    {memberNotFound && <div className="text-danger">此會員編號不存在，請確認後重新輸入</div>}
                    <Form.Control.Feedback type="invalid">
                        請輸入姓名
                    </Form.Control.Feedback>
                </Form.Group>
            </Col>
        </Row>
    );
};

export default MemberColumn; 