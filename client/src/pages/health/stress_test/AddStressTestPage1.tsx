// ./src/pages/health/stress_test/AddStressTestPage1.tsx
import React, { useState, useEffect } from "react"; // 新增 useState, useEffect
import { Col, Button, Form, Row, Card, InputGroup, FormControl } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { savePage1Answers, saveStressTestUserInfo, getStressTestUserInfo } from "../../../utils/stressTestStorage"; // 新增 saveStressTestUserInfo, getStressTestUserInfo
import Header from "../../../components/Header";
import DynamicContainer from "../../../components/DynamicContainer";
// import { formatDateToChinese, formatGenderToChinese } from "../../../utils/memberUtils"; // 如果不再顯示詳細會員資訊，可能不需要
import useStressTestForm, { Question } from "../../../hooks/useStressTestForm"; // 這個 hook 需要大幅修改

// 問卷問題定義 (保持不變)
const questions: Question[] = [
  { id: "a1", textA: "我對我的行動是果斷而且堅定不移", textB: "我在防衛我的動機時，總會表現極度的熱誠" },
  { id: "a2", textA: "我喜歡非常和諧的狀況", textB: "我喜歡和新朋友見面" },
  { id: "a3", textA: "我喜歡計畫一些未來的事情", textB: "我喜歡根據程序做事情" },
  { id: "a4", textA: "我是個有創造性的人", textB: "我是個富進取心的人" },
  { id: "a5", textA: "我很喜歡友善地對待其他人", textB: "我很喜歡依照細節及規格做事情" },
  { id: "b1", textA: "我總是想尋找一些例外的事情", textB: "我很喜歡想一些替代方案" },
  { id: "b2", textA: "我喜歡有人被我指導", textB: "我喜歡檢查一些事情以求精確" },
  { id: "b3", textA: "我喜歡以新的方式看待一些事情", textB: "我喜歡待在一群人所組成的團體中" },
  { id: "b4", textA: "我把自己看成一個有判意的人", textB: "我在工作上總是力求控制和秩序感" },
  { id: "b5", textA: "我喜歡做一些我感覺到正確的事情", textB: "我喜歡做一些體力勞動的事情" },
];

// 定義使用者輸入資訊的型別
interface StressTestUserInfo {
  name: string;
  position: string;
  testDate: string;
}

const AddStressTestPage1: React.FC = () => {
  const navigate = useNavigate();

  // 從 useStressTestForm hook 獲取狀態和方法
  // 注意：這個 hook 需要被修改以移除 memberId 搜索，並可能需要處理新的 user info
  const {
    // memberId, // 移除
    // setMemberId, // 移除
    // member, // 移除或改變用途
    // searching, // 移除
    error,
    setError, // 保持，用於一般錯誤提示
    formSubmitted, // 保持，用於問卷驗證提示
    answers,
    handleSelect,
    checkUnansweredQuestions,
    getUnansweredCount,
    submitForm // 保持，觸發 formSubmitted 狀態
    // handleSearchMember, // 移除
  } = useStressTestForm({ isPage2: false });

  // 新增 State 管理姓名、職位、檢測日期
  const [userInfo, setUserInfo] = useState<StressTestUserInfo>(() => {
    const savedInfo = getStressTestUserInfo();
    return savedInfo || {
      name: "",
      position: "",
      testDate: new Date().toISOString().split('T')[0] // 預設為今天
    };
  });

  // 當 userInfo 變化時保存到 localStorage
  useEffect(() => {
    saveStressTestUserInfo(userInfo);
  }, [userInfo]);


  const handleUserInfoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setUserInfo(prev => ({ ...prev, [name]: value }));
  };

  const handleNextPage = () => {
    submitForm(); // 觸發問卷的必填提示

    // 1. 檢查姓名、職位、檢測日期是否已填寫
    if (!userInfo.name.trim() || !userInfo.position.trim() || !userInfo.testDate) {
      setError("請填寫姓名、職位及檢測日期");
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }
    setError(""); // 清除之前的錯誤

    // 2. 檢查是否所有問題都已回答 (這部分邏輯來自 hook，保持不變)
    const unansweredQuestions = checkUnansweredQuestions(questions);
    if (unansweredQuestions.length > 0) {
      const firstUnansweredId = `q${unansweredQuestions[0]}_A`;
      const element = document.getElementById(firstUnansweredId);
      if (element) {
        window.scrollTo({ top: element.offsetTop - 100, behavior: 'smooth' });
      } else {
        window.scrollTo({ top: document.getElementById('questionnaire')?.offsetTop || 0, behavior: 'smooth' });
      }
      return;
    }

    // 所有驗證通過，保存使用者資訊和答案到本地存儲並導航到下一頁
    saveStressTestUserInfo(userInfo); // 確保是最新的
    savePage1Answers(answers);
    navigate("/health-data-analysis/stress-test/add/page2");
  };

  const content = (
    <div className="w-100 px-4">
      {/* 上方資訊顯示區域 - 修改為輸入欄位 */}
      <Card className="mb-4">
        <Card.Header className="bg-light"> {/* 調整背景色以符合 Figma */}
          <h5 className="mb-0 text-secondary">受測者資訊</h5> {/* 調整標題和文字顏色 */}
        </Card.Header>
        <Card.Body>
          {error && <div className="alert alert-danger">{error}</div>} {/* 統一錯誤提示 */}
          <Row className="g-3 align-items-center"> {/* 使用 g-3 增加間距 */}
            <Col md={4} sm={6}>
              <Form.Group>
                <Form.Label>姓名</Form.Label>
                <Form.Control
                  type="text"
                  name="name"
                  placeholder="請輸入姓名"
                  value={userInfo.name}
                  onChange={handleUserInfoChange}
                  isInvalid={formSubmitted && !userInfo.name.trim()}
                />
                <Form.Control.Feedback type="invalid">姓名為必填項</Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col md={4} sm={6}>
              <Form.Group>
                <Form.Label>職位</Form.Label>
                <Form.Control
                  type="text"
                  name="position"
                  placeholder="請輸入職位"
                  value={userInfo.position}
                  onChange={handleUserInfoChange}
                  isInvalid={formSubmitted && !userInfo.position.trim()}
                />
                <Form.Control.Feedback type="invalid">職位為必填項</Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col md={4} sm={6}>
              <Form.Group>
                <Form.Label>檢測日期</Form.Label>
                <Form.Control
                  type="date"
                  name="testDate"
                  value={userInfo.testDate}
                  onChange={handleUserInfoChange}
                  isInvalid={formSubmitted && !userInfo.testDate}
                />
                <Form.Control.Feedback type="invalid">檢測日期為必填項</Form.Control.Feedback>
              </Form.Group>
            </Col>
            <Col md={4} sm={6}> {/* Figma 中有 "分數" 欄位，這裡先做個佔位 */}
              <Form.Group>
                <Form.Label>分數</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="-"
                  readOnly
                  disabled
                  className="bg-light" // 使其看起來更像不可編輯
                />
              </Form.Group>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* 移除原本的會員選擇 Card 和 會員詳細資訊顯示 Card */}

      {/* 問卷區域 (保持大部分不變) */}
      <Card id="questionnaire">
        <Card.Header className="bg-info text-white">
          <h5 className="mb-0">壓力測試問卷 (第1頁)</h5>
        </Card.Header>
        <Card.Body>
          {formSubmitted && getUnansweredCount(questions) > 0 && (
            <div className="alert alert-warning" role="alert">
              尚有 {getUnansweredCount(questions)} 個問題未回答，請完成所有問題後再繼續
            </div>
          )}
          <Form>
            {questions.map((q, index) => ( // 新增 index
              <Form.Group className="mb-3 questionnaire-item" key={q.id}> {/* 使用 CSS class questionnaire-item */}
                <Row>
                  <Col xs={12}>
                    <span className="fw-bold">{index + 1}. </span> {/* 顯示題號 */}
                    <Form.Check
                      inline
                      type="radio"
                      label={`（甲）${q.textA}`}
                      name={`q${q.id}`}
                      id={`q${q.id}_A`}
                      checked={answers[q.id] === "A"}
                      onChange={() => handleSelect(q.id, "A")}
                      className="me-3" // 增加右邊間距
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
                  </Col>
                </Row>
                {formSubmitted && !answers[q.id] && (
                  <div className="text-danger small mt-1">* 此題必填</div>
                )}
              </Form.Group>
            ))}
          </Form>
        </Card.Body>
      </Card>

      <div className="d-flex justify-content-end mt-4"> {/* Figma 中只有 "下一頁" */}
        {/* 返回按鈕可以根據需要保留或移除，Figma 中沒有顯示 */}
        {/* <Button 
          variant="secondary" 
          onClick={() => navigate('/health-data-analysis/stress-test')}
          className="me-auto" // 推到最左邊
        >
          返回列表
        </Button> */}
        <Button
          variant="info"
          className="px-5 text-white" // 保持 Bootstrap class
          onClick={handleNextPage}
          style={{backgroundColor: '#00b1c8', borderColor: '#00b1c8'}} // Figma 中的藍色
        >
          下一頁
        </Button>
      </div>
    </div>
  );

  return (
    <div className="d-flex flex-column min-vh-100 bg-white">
      <Header title="新增iPN壓力源測試 1.1.1.4.1.1" />
      <DynamicContainer content={content} className="p-0 align-items-start" />
    </div>
  );
};

export default AddStressTestPage1;