import React from "react";
import { Button, Form, Card, Alert } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import Header from "../../../components/Header";
import DynamicContainer from "../../../components/DynamicContainer";
import useStressTestForm, { Question } from "../../../hooks/useStressTestForm";

// 問卷問題定義
const questions: Question[] = [
  { id: "c1", textA: "我總是預期最好的事情會發生", textB: "我喜歡用有系統的方法做事情" },
  { id: "c2", textA: "我喜歡想像各種事物的可能性", textB: "我喜歡做一個強勢的人" },
  { id: "c3", textA: "我對與別人合作總是感到自在", textB: "我總是有一些獨立的思考" },
  { id: "c4", textA: "我總是以熱誠及友善對待別人", textB: "我對自己的方向總是精力充沛" },
  { id: "c5", textA: "如果我信仰某種理由 我可能會慷慨性我的興趣", textB: "我喜歡以有秩序的方式做事" },
  { id: "d1", textA: "我喜歡想一些新點子", textB: "我總是以充滿興奮及精力的方式做事情" },
  { id: "d2", textA: "我喜歡和別人談話", textB: "我喜歡依照特定程序" },
  { id: "d3", textA: "我是個謹慎的人", textB: "我喜歡完成一些事情" },
  { id: "d4", textA: "我喜歡處於一種可以行動的狀況", textB: "我常常表現體貼和同情的心態" },
  { id: "d5", textA: "我喜歡和陌生人交談", textB: "我喜歡在大多數的情況下發號施令" },
];

const AddStressTestPage2: React.FC = () => {
  const navigate = useNavigate();
  
  // 使用增強版的 useStressTestForm hook，指定為第2頁
  const {
    memberId,
    member,
    error,
    submitting,
    answers,
    handleSelect,
    handleSubmit
  } = useStressTestForm({ isPage2: true });

  // 提交表單
  const onSubmit = () => {
    handleSubmit(questions);
  };

  // 準備 DynamicContainer 的內容
  const content = (
    <div className="w-100 px-4">
      {error && <Alert variant="danger">{error}</Alert>}
      
      {/* 會員信息提示 */}
      {memberId && (
        <Alert variant="info" className="mb-4">
          正在為會員 {member ? member.Name : "載入中..."} (ID: {memberId}) 進行壓力測試
        </Alert>
      )}
      
      {/* 問卷區域 */}
      <Card>
        <Card.Header className="bg-info text-white">
          <h5 className="mb-0">壓力測試問卷 (第2頁)</h5>
        </Card.Header>
        <Card.Body>
          <Form>
            {questions.map((q) => (
              <Form.Group className="mb-3" key={q.id}>
                <Form.Label className="fw-bold">
                  {q.id}.{" "}
                  <Form.Check
                    inline
                    type="radio"
                    label={`（甲）${q.textA}`}
                    name={`q${q.id}`}
                    id={`q${q.id}_A`}
                    checked={answers[q.id] === "A"}
                    onChange={() => handleSelect(q.id, "A")}
                  />
                  <Form.Check
                    inline
                    type="radio"
                    label={`（乙）${q.textB}`}
                    name={`q${q.id}`}
                    id={`q${q.id}_B`}
                    checked={answers[q.id] === "B"}
                    onChange={() => handleSelect(q.id, "B")}
                  />
                </Form.Label>
              </Form.Group>
            ))}
          </Form>
        </Card.Body>
      </Card>

      {/* Bottom Navigation */}
      <div className="d-flex justify-content-between mt-4">
        <Button 
          variant="secondary" 
          onClick={() => navigate("/health-data-analysis/stress-test/add/page1")}
          disabled={submitting}
          className="px-5"
        >
          上一頁
        </Button>
        <Button 
          variant="info" 
          className="px-5 text-white"
          onClick={onSubmit}
          disabled={submitting}
        >
          {submitting ? "提交中..." : "送出"}
        </Button>
      </div>
    </div>
  );

  return (
    <div className="d-flex flex-column min-vh-100 bg-white">
      {/* 使用標準 Header 組件 */}
      <Header title="新增 iPN 壓力源測試 1.1.1.4.1.1.2" />
      
      {/* 使用 DynamicContainer 包裝內容 */}
      <DynamicContainer content={content} className="p-0 align-items-start" />
    </div>
  );
};

export default AddStressTestPage2;
