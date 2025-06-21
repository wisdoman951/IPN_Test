// ./src/pages/therapy/AddTherapySell.tsx
import React, { useState, useEffect, useCallback } from "react";
import { Button, Container, Form, Row, Col, Card, Alert, Spinner, InputGroup, ListGroup } from "react-bootstrap";
import { useNavigate, useLocation } from "react-router-dom"; // 新增 useLocation
import Header from "../../components/Header";
import DynamicContainer from "../../components/DynamicContainer";
import MemberColumn from "../../components/MemberColumn";
// import TitlePrice from "../../components/TitlePrice"; // 將直接顯示總價
import {
    addTherapySell,
    getAllStores,
    AddTherapySellPayload,
    TherapyPackage as TherapyPackageBaseType,
    StaffMember as StaffMemberType,
    Store as StoreType,
    // 從 TherapySellService 匯入 PackageInSelection (如果在服務檔案中定義並導出)
    // 或者在本地定義，如我之前建議的
} from "../../services/TherapySellService";
import { getStoreId } from "../../services/LoginService";
import { getStaffMembers } from "../../services/TherapySellService";

// 與 TherapyPackageSelection.tsx 中 PackageInSelection 結構一致，用於 localStorage 傳遞
interface TherapyPackageWithSessions extends TherapyPackageBaseType {
  userSessions: string;
}

// AddTherapySell.tsx 內部管理的已選套餐，包含計算後的價格資訊
interface SelectedTherapyPackageUIData extends TherapyPackageWithSessions {
  itemOriginalTotal: number;
  calculatedItemDiscount: number;
  calculatedItemFinalPrice: number;
}


interface MemberData {
    member_id: number;
    name: string;
}

const therapyPaymentMethodDisplayMap: { [key: string]: string } = { "現金": "Cash", "信用卡": "CreditCard", "轉帳": "Transfer", "行動支付": "MobilePayment", "其他": "Others" };
const therapySaleCategoryDisplayMap: { [key: string]: string } = { "銷售": "Sell", "贈送": "Gift", "折扣": "Discount", "票卷": "Ticket" };
const paymentMethodOptions = Object.keys(therapyPaymentMethodDisplayMap);
const saleCategoryOptions = Object.keys(therapySaleCategoryDisplayMap);


const AddTherapySell: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation(); // <--- 使用 useLocation
    const [loading, setLoading] = useState(false);
    const [optionsLoading, setOptionsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [formSubmitted, setFormSubmitted] = useState(false);

    const userStoreId = (() => { try { const id = localStorage.getItem('store_id'); return id ? Number(id) : undefined; } catch (e) { return undefined; } })();
    
    const [memberId, setMemberId] = useState<string>("");
    const [memberName, setMemberName] = useState<string>("");
    const [storeId, setStoreId] = useState<string>(userStoreId ? userStoreId.toString() : "");
    const [staffId, setStaffId] = useState<string>("");
    const [purchaseDate, setPurchaseDate] = useState(new Date().toISOString().split("T")[0]);
    
    const [selectedTherapyPackages, setSelectedTherapyPackages] = useState<SelectedTherapyPackageUIData[]>([]);
    
    const [paymentMethod, setPaymentMethod] = useState<string>(paymentMethodOptions[0] || "");
    const [salesCategory, setSalesCategory] = useState<string>(saleCategoryOptions[0] || "");
    const [transferCode, setTransferCode] = useState("");
    const [cardNumber, setCardNumber] = useState("");
    const [discountPercentInput, setDiscountPercentInput] = useState<string>("0");
    const [note, setNote] = useState("");
    
    const [therapiesOriginalTotal, setTherapiesOriginalTotal] = useState<number>(0);
    const [orderFinalPrice, setOrderFinalPrice] = useState<number>(0);
    const [selectedStaffId, setSelectedStaffId] = useState<string>("");
    const [staffList, setStaffList] = useState<StaffMemberType[]>([]);
    const [storeList, setStoreList] = useState<StoreType[]>([]);

    useEffect(() => {
        const currentStoreIdVal = getStoreId();
        if (currentStoreIdVal) setStoreId(currentStoreIdVal);
        else setError("無法獲取當前門市資訊，請重新登入。");

        const fetchData = async () => {
            setOptionsLoading(true);
            try {
                const [staffRes, storesRes] = await Promise.all([
                    getStaffMembers(),
                    getAllStores()
                ]);

                if (staffRes.success && staffRes.data) {
                    setStaffList(staffRes.data);
                    if (staffRes.data.length > 0 && !localStorage.getItem('addTherapySellFormState')?.includes('"staffId":"')) {
                         setSelectedStaffId(staffRes.data[0].staff_id.toString());
                    }
                } else { setError(prev => `${prev || ''}\n銷售人員載入失敗: ${staffRes.error}`.trim());}

                if (storesRes.success && storesRes.data) {
                    setStoreList(storesRes.data);
                    if (userStoreId === undefined && storesRes.data.length > 0 && !storeId) {
                        setStoreId(storesRes.data[0].store_id.toString());
                    } else if (userStoreId !== undefined) {
                        setStoreId(userStoreId.toString());
                    }
                } else { setError(prev => `${prev || ''}\n店家列表載入失敗: ${storesRes.error}`.trim());}

            } catch (err) {
                console.error("獲取下拉數據失敗:", err);
                setError("無法載入頁面選項。");
            } finally {
                setOptionsLoading(false);
            }
        };
        fetchData();
    }, []); // 移除 userStoreId，它在組件首次渲染時已確定

        // useEffect 用於從 localStorage 恢復狀態 和 處理從選擇頁返回的數據
    useEffect(() => {
        const formStateData = localStorage.getItem('addTherapySellFormState');
        const newlySelectedPkgsData = localStorage.getItem('newlySelectedTherapyPackagesWithSessions');

        let shouldProcessLocalStorage = false;
        if (location.state?.therapyPackagesUpdated) { // 檢查標記
            shouldProcessLocalStorage = true;
            // 清除標記，避免下次刷新時誤觸
            navigate(location.pathname, { replace: true, state: {} }); 
        } else if (!selectedTherapyPackages.length && !formSubmitted) { 
            // 或者在初次載入且沒有已選套餐時也嘗試恢復 (避免覆蓋用戶正在編輯的內容)
            // 這裡的條件可能需要根據您的具體需求微調
            shouldProcessLocalStorage = true;
        }


        if (shouldProcessLocalStorage) {
            let initialPackagesForUI: SelectedTherapyPackageUIData[] = [];
            let restoredDiscount = discountPercentInput; // 預設為當前 state，避免不必要的覆蓋
            let formState: any = {};

            if (formStateData) {
                try { formState = JSON.parse(formStateData); } 
                catch (e) { console.error("解析 addTherapySellFormState 失敗", e); }
            }

            // 只在 formStateData 存在且是初次恢復時（或特定條件下）才恢復這些欄位
            // 避免從選擇頁返回時覆蓋掉已有的會員等資訊
            if (formStateData && !newlySelectedPkgsData) { // 表示不是從選擇頁剛回來，而是常規的狀態恢復
                if (formState.memberId) setMemberId(formState.memberId);
                if (formState.memberName) setMemberName(formState.memberName);
                if (formState.staffId) setStaffId(formState.staffId);
                if (formState.purchaseDate) setPurchaseDate(formState.purchaseDate);
                if (formState.paymentMethod) setPaymentMethod(formState.paymentMethod);
                if (formState.salesCategory) setSalesCategory(formState.salesCategory);
                if (formState.transferCode) setTransferCode(formState.transferCode);
                if (formState.cardNumber) setCardNumber(formState.cardNumber);
                if (formState.discountPercent) restoredDiscount = formState.discountPercent;
                if (formState.note) setNote(formState.note);
            }


            if (newlySelectedPkgsData) {
                try {
                    const pkgsFromSelection = JSON.parse(newlySelectedPkgsData) as PackageInSelection[];
                    initialPackagesForUI = pkgsFromSelection.map(pkg => ({
                        ...pkg,
                        userSessions: pkg.userSessions || "1",
                        itemOriginalTotal: (pkg.TherapyPrice || 0) * (Number(pkg.userSessions || 1)),
                        calculatedItemDiscount: 0,
                        calculatedItemFinalPrice: (pkg.TherapyPrice || 0) * (Number(pkg.userSessions || 1)),
                    }));
                    localStorage.removeItem('newlySelectedTherapyPackagesWithSessions');
                    setSelectedTherapyPackages(initialPackagesForUI); // 直接設定新選擇的
                } catch (e) { console.error("解析 newlySelectedPkgsData 失敗", e); }
            } else if (formState.selectedTherapyPackages && Array.isArray(formState.selectedTherapyPackages) && initialPackagesForUI.length === 0) {
                // 如果沒有新選擇，但 formState 中有，則恢復 formState 中的
                initialPackagesForUI = formState.selectedTherapyPackages.map((pkg: any) => ({
                    /* ... 轉換 ... */
                }));
                setSelectedTherapyPackages(initialPackagesForUI);
            }

            setDiscountPercentInput(restoredDiscount);
            if(formStateData) localStorage.removeItem('addTherapySellFormState');
        }
    // 依賴 location.state 以便在從選擇頁返回時觸發
    // 移除 selectedTherapyPackages 以避免因其內部計算欄位更新導致的循環
    }, [location.state, navigate]);


       // **修改點 1：當 selectedTherapyPackages 內部 (主要是 userSessions) 改變時，重新計算 therapiesOriginalTotal**
    useEffect(() => {
        let currentOriginalTotal = 0;
        selectedTherapyPackages.forEach(pkg => {
            const sessions = Number(pkg.userSessions) || 0;
            const therapyPrice = pkg.TherapyPrice || 0;
            currentOriginalTotal += therapyPrice * sessions;
        });
        setTherapiesOriginalTotal(currentOriginalTotal);
    }, [selectedTherapyPackages]); // 依賴整個 selectedTherapyPackages 陣列的引用或深層比較 (下方有更佳解)
    // 更佳的依賴: selectedTherapyPackages.map(p => `${p.therapy_id}-${p.userSessions}`).join(',')
    // 但由於我們在下一個 useEffect 中會更新 selectedTherapyPackages 的內部項目，
    // 所以這裡的依賴保持為 [selectedTherapyPackages] 可能會更好理解，由下一個 effect 觸發最終更新。


    // **修改點 2：當 therapiesOriginalTotal 或 discountPercentInput 改變時，計算最終價格並更新每個套餐的分攤折扣**
    useEffect(() => {
        const numDiscountPercent = Number(discountPercentInput) || 0;
        const totalOrderDiscountAmount = parseFloat((therapiesOriginalTotal * (numDiscountPercent / 100)).toFixed(2));
        setOrderFinalPrice(parseFloat((therapiesOriginalTotal - totalOrderDiscountAmount).toFixed(2)));

        // 更新每個套餐的分攤折扣和最終價格
        setSelectedTherapyPackages(prevPackages => {
            // 如果原始總價為0，則每個品項折扣也為0
            if (therapiesOriginalTotal === 0) {
                return prevPackages.map(pkg => {
                    const itemOriginal = (pkg.TherapyPrice || 0) * (Number(pkg.userSessions) || 0);
                    return {
                        ...pkg,
                        itemOriginalTotal: itemOriginal,
                        calculatedItemDiscount: 0,
                        calculatedItemFinalPrice: itemOriginal,
                    };
                });
            }

            // 否則，按比例分攤
            let cumulativeDiscountApplied = 0;
            const updatedPackages = prevPackages.map((pkg, index, arr) => {
                const sessions = Number(pkg.userSessions) || 0;
                const itemOriginalTotal = (pkg.TherapyPrice || 0) * sessions;
                let apportionedDiscount;

                if (index === arr.length - 1) { // 最後一項取剩餘折扣，避免浮點數誤差累積
                    apportionedDiscount = parseFloat((totalOrderDiscountAmount - cumulativeDiscountApplied).toFixed(2));
                } else {
                    const proportion = therapiesOriginalTotal > 0 ? itemOriginalTotal / therapiesOriginalTotal : 0;
                    apportionedDiscount = parseFloat((totalOrderDiscountAmount * proportion).toFixed(2));
                    cumulativeDiscountApplied += apportionedDiscount;
                }
                
                const itemFinal = parseFloat((itemOriginalTotal - apportionedDiscount).toFixed(2));
                return { 
                    ...pkg, 
                    itemOriginalTotal: itemOriginalTotal,
                    calculatedItemDiscount: apportionedDiscount, 
                    calculatedItemFinalPrice: itemFinal 
                };
            });
            // 檢查新舊陣列是否有實際變化才更新，避免不必要的重渲染 (淺比較)
            // 這裡的比較可能不夠深，但可以作為一層優化
            if (JSON.stringify(prevPackages) !== JSON.stringify(updatedPackages)) {
                return updatedPackages;
            }
            return prevPackages;
        });
    }, [therapiesOriginalTotal, discountPercentInput]); // 依賴這兩個計算出來的值



    const handleMemberChange = (id: string, name: string) => { setMemberId(id); setMemberName(name); setError(null); };
    const handleMemberError = (msg: string) => setError(msg);
    const openTherapyPackageSelection = () => {
        const formState = {
            memberId, memberName, storeId, staffId, purchaseDate,
            paymentMethod, salesCategory, transferCode, cardNumber, discountPercent: discountPercentInput, note,
            selectedTherapyPackages // 保存當前已選套餐和其堂數、計算的價格等
        };
        localStorage.setItem('addTherapySellFormState', JSON.stringify(formState));
        navigate('/therapy-package-selection');
    };
    const handlePrint = () => { window.print(); };
    const handlePackageSessionsChange = (therapy_id: number, newUserSessions: string) => {
        const sessionsNum = Math.max(1, parseInt(newUserSessions) || 1).toString(); // 至少為1
        setSelectedTherapyPackages(prev =>
            prev.map(pkg => pkg.therapy_id === therapy_id ? { ...pkg, userSessions: sessionsNum } : pkg)
        );
    };
    const removeSelectedPackage = (therapy_id: number) => {
        setSelectedTherapyPackages(prev => prev.filter(pkg => pkg.therapy_id !== therapy_id));
    };

const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormSubmitted(true);
    setError(null);
    setSuccess(null);

    const today = new Date(); today.setHours(0,0,0,0);
    const selectedPurchaseDate = new Date(purchaseDate); selectedPurchaseDate.setHours(0,0,0,0);
    if (selectedPurchaseDate > today) { setError("購買日期不能選擇未來日期。"); return; }
    if (!storeId) { setError("無法獲取門市資訊，請重新登入。"); return; }
    if (!memberId || !memberName) { setError("請選擇會員並確認姓名。"); return; }
    if (selectedTherapyPackages.length === 0) { setError("請選擇至少一項療程套餐。"); return; }
    let allSessionsValid = true;
    for (const pkg of selectedTherapyPackages) {
        if (!pkg.userSessions || Number(pkg.userSessions) <= 0) {
            setError(`請為套餐「${pkg.TherapyName || pkg.TherapyContent}」輸入有效的堂數 (至少為1)。`);
            allSessionsValid = false; break;
        }
    }
    if (!allSessionsValid) return;
    if (!paymentMethod) { setError("請選擇付款方式。"); return; }
    if (!staffId) { setError("請選擇銷售人員。"); return; }
    if (!salesCategory) { setError("請選擇銷售類別。"); return; }
    const discountP = Number(discountPercentInput);
    if (isNaN(discountP) || discountP < 0 || discountP > 100) { setError("折扣百分比必須是 0 到 100 之間的數字。"); return; }
    // orderFinalPrice 已在 useEffect 中計算，這裡可以簡單檢查非負
    if (orderFinalPrice < 0 && therapiesOriginalTotal > 0) { // 允許總價為0的贈品單
            setError("應收金額低於零，請檢查。"); 
            return;
    }
    // 最終金額通常不需要在此處再次驗證，因為它是計算得出的
    // if (orderFinalPrice < 0) { setError("應收金額低於零，請檢查。"); return;}

    setLoading(true);
    try {
        const paymentMethodForDB = therapyPaymentMethodDisplayMap[paymentMethod] || paymentMethod;
        const saleCategoryForDB = therapySaleCategoryDisplayMap[salesCategory] || salesCategory;

        // ***** 準備一個包含所有銷售項目的陣列 *****
        const therapySalesToSubmit: AddTherapySellPayload[] = [];

        for (const pkg of selectedTherapyPackages) {
            // 從 pkg (SelectedTherapyPackageUIData) 中獲取已計算好的價格資訊
            // 假設 therapy_sell 表儲存的是每個療程項目的單價、數量、折扣金額、最終價格
            const therapySaleItem: AddTherapySellPayload = {
                memberId: parseInt(memberId),
                storeId: parseInt(storeId),
                staffId: parseInt(staffId),
                purchaseDate,
                therapy_id: pkg.therapy_id,
                amount: Number(pkg.userSessions),        // 該套餐的堂數
                paymentMethod: paymentMethodForDB,
                saleCategory: saleCategoryForDB,
                note: note || undefined, // 整筆訂單共用一個備註
                transferCode: paymentMethod === "轉帳" ? transferCode : undefined,
                cardNumber: paymentMethod === "信用卡" ? cardNumber : undefined,
                
                // 價格資訊：
                // unit_price: pkg.TherapyPrice, // 該套餐的原始單價
                // discount_amount: pkg.calculatedItemDiscount, // 該套餐分攤到的折扣金額
                // final_price: pkg.calculatedItemFinalPrice,   // 該套餐的最終支付價格
                
                // 或者，如果後端期望的是整筆訂單的折扣百分比，然後自己計算每個項目的價格：
                discount: Number(discountPercentInput) || 0, // 整筆訂單的折扣百分比
                // 在這種情況下，後端 insert_therapy_sell 需要根據 therapy_id 查到單價，
                // 然後結合 amount 和 discount (百分比) 來計算並儲存 unit_price, discount_amount, final_price
            };
            therapySalesToSubmit.push(therapySaleItem);
        }

        if (therapySalesToSubmit.length > 0) {
            console.log("Submitting batch therapy sell data:", therapySalesToSubmit);
            const response = await addTherapySell(therapySalesToSubmit); // <<-- 傳送陣列
            console.log(therapySalesToSubmit)

            if (response.success) {
                // ... (成功後的處理，與上一版類似：清除localStorage, 重置表單, 導航) ...
                localStorage.removeItem('addTherapySellFormState');
                localStorage.removeItem('newlySelectedTherapyPackagesWithSessions');
                setSuccess("療程銷售已全部成功新增！2秒後返回列表。");
                // ... (重置表單 state) ...
                setTimeout(() => navigate("/therapy-sell"), 2000);
            } else {
                setError(response.error || "新增療程銷售失敗，部分或全部項目可能未成功。");
            }
        } else {
            setError("沒有可提交的銷售品項。"); // 理論上不會到這裡，因為前面有檢查 selectedTherapyPackages.length
        }
        console.log(therapySalesToSubmit)
    } catch (err: any) {
        console.error("新增療程銷售失敗 (handleSubmit):", err);
        setError(err.response?.data?.error || err.message || "新增療程銷售時發生未知錯誤。");
    } finally {
        setLoading(false);
    }
};  
    const content = (
        <Container className="my-4">
            {error && <Alert variant="danger" dismissible onClose={() => setError(null)}>{error}</Alert>}
            {success && <Alert variant="success">{success}</Alert>}
            
            <Form onSubmit={handleSubmit} noValidate>
                <p className="text-muted mb-4">新增銷售療程時自動帶出會員編號，姓名，療程及價格</p>
                <Row className="g-3">
                    {/* --- 左欄 --- */}
                    <Col md={6}>
                        <Form.Group className="mb-3">
                            <Form.Label>購買人姓名</Form.Label>
                            <MemberColumn memberId={memberId} name={memberName} onMemberChange={handleMemberChange} onError={handleMemberError} triggerSearchOnMount={false} />
                            {formSubmitted && !memberName && <div className="d-block invalid-feedback">請選擇購買會員</div>}
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Label>購買品項 (療程套餐)</Form.Label>
                            <div className="d-flex gap-2 mb-2">
                                <div className="flex-grow-1 p-2 text-muted" style={{ border: "1px solid #ced4da", borderRadius: "0.25rem", minHeight: "38px" }}>
                                    已選 {selectedTherapyPackages.length} 項套餐 (點「選取」可增減)
                                </div>
                                <Button variant="info" className="text-white align-self-start px-3" onClick={openTherapyPackageSelection} disabled={loading || optionsLoading}>
                                    選取套餐
                                </Button>
                            </div>
                            <Form.Text muted>可複選，跳出新視窗選取，並在下方設定各套餐堂數。</Form.Text>
                            
                            {selectedTherapyPackages.length > 0 && (
                                <Card className="mt-2">
                                    <Card.Header as="h6">已選套餐與堂數設定</Card.Header>
                                    <ListGroup variant="flush" style={{maxHeight: '200px', overflowY: 'auto'}}>
                                        {selectedTherapyPackages.map((pkg, index) => (
                                            <ListGroup.Item key={pkg.therapy_id || index} className="py-2">
                                                <Row className="align-items-center gx-2">
                                                    <Col xs={12} sm={6} className="mb-2 mb-sm-0">
                                                        <div>{pkg.TherapyContent || pkg.TherapyName}</div>
                                                        <small className="text-muted">單價: NT$ {pkg.TherapyPrice.toLocaleString()}</small>
                                                    </Col>
                                                    <Col xs={8} sm={4}>
                                                        <InputGroup size="sm">
                                                            <InputGroup.Text>堂數:</InputGroup.Text>
                                                            <Form.Control
                                                                type="number"
                                                                min="1"
                                                                value={pkg.userSessions}
                                                                onChange={(e) => handlePackageSessionsChange(pkg.therapy_id, e.target.value)}
                                                                placeholder="堂數"
                                                            />
                                                        </InputGroup>
                                                    </Col>
                                                    <Col xs={4} sm={2} className="text-end">
                                                        <Button variant="outline-danger" size="sm" onClick={() => removeSelectedPackage(pkg.therapy_id)}>移除</Button>
                                                    </Col>
                                                </Row>
                                                {formSubmitted && (!pkg.userSessions || Number(pkg.userSessions) <= 0) && <div className="text-danger small mt-1">請為此套餐輸入有效堂數</div>}
                                            </ListGroup.Item>
                                        ))}
                                    </ListGroup>
                                </Card>
                            )}
                             {formSubmitted && selectedTherapyPackages.length === 0 && <div className="text-danger d-block small mt-1">請選擇購買品項</div>}
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Label>付款方式</Form.Label>
                            <Form.Select value={paymentMethod} onChange={(e) => {setPaymentMethod(e.target.value); if (e.target.value !== "信用卡") setCardNumber(""); if (e.target.value !== "轉帳") setTransferCode("");}} required disabled={loading}>
                                {paymentMethodOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                            </Form.Select>
                            <Form.Text muted>下拉式：現金、轉帳(輸入末五碼)、信用卡(輸入卡號後五碼)、行動支付。</Form.Text>
                        </Form.Group>

                        {paymentMethod === "信用卡" && ( <Form.Group className="mb-3"><Form.Label>卡號後五碼</Form.Label><Form.Control type="text" maxLength={5} pattern="\d*" value={cardNumber} onChange={(e) => setCardNumber(e.target.value.replace(/\D/g,'').slice(0,5))} placeholder="請輸入信用卡號後五碼" /></Form.Group>)}
                        {paymentMethod === "轉帳" && ( <Form.Group className="mb-3"><Form.Label>轉帳帳號末五碼</Form.Label><Form.Control type="text" maxLength={5} pattern="\d*" value={transferCode} onChange={(e) => setTransferCode(e.target.value.replace(/\D/g,'').slice(0,5))} placeholder="請輸入轉帳帳號末五碼" /></Form.Group>)}

                        <Form.Group className="mb-3">
                            <Form.Label>銷售類別</Form.Label>
                            <Form.Select value={salesCategory} onChange={(e) => setSalesCategory(e.target.value)} required disabled={loading}>
                                {saleCategoryOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                            </Form.Select>
                            <Form.Text muted>下拉式：銷售、贈品、折扣、預購、暫借，需連動後台系統。</Form.Text>
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Label>總價 (折扣後)</Form.Label>
                            <Form.Control type="text" value={`NT$ ${orderFinalPrice.toLocaleString()}`} readOnly disabled className="bg-light text-end"/>
                        </Form.Group>

                         <Form.Group className="mb-3">
                            <Form.Label>應收</Form.Label>
                            <Form.Control type="text" value={`NT$ ${orderFinalPrice.toLocaleString()}`} readOnly disabled className="bg-light text-end"/>
                        </Form.Group>
                      </Col>

                      {/* --- 右欄 --- */}
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>購買日期</Form.Label>
                          <Form.Control type="date" value={purchaseDate} max={new Date().toISOString().split("T")[0]} onChange={(e) => setPurchaseDate(e.target.value)} required disabled={loading}/>
                          <Form.Text muted>選擇購買日期。會跳出日曆，無法選取未來日期。</Form.Text>
                        </Form.Group>

                        <Form.Group className="mb-3">
                          <Form.Label>價錢 (原始總計)</Form.Label>
                          <Form.Control type="text" value={`NT$ ${therapiesOriginalTotal.toLocaleString()}`} readOnly disabled className="bg-light text-end" />
                          <Form.Text muted>自動帶出所有選取套餐的原始總價，價格固定不能修改。</Form.Text>
                        </Form.Group>
                        
                        <Form.Group className="mb-3">
                          <Form.Label>銷售人員</Form.Label>
                          <Form.Select value={staffId} onChange={(e) => setStaffId(e.target.value)} required disabled={loading || optionsLoading}>
                            <option value="">{optionsLoading ? "載入中..." : "請選擇銷售人員"}</option>
                            {staffList.map((s) => ( <option key={s.staff_id} value={s.staff_id.toString()}>{s.name}</option> ))}
                          </Form.Select>
                          <Form.Text muted>下拉式：連動各店後台系統、報表。</Form.Text>
                          {formSubmitted && !staffId && <div className="text-danger d-block small mt-1">請選擇銷售人員</div>}
                        </Form.Group>

                        <Form.Group className="mb-3">
                          <Form.Label>備註</Form.Label>
                          <Form.Control as="textarea" rows={3} value={note} onChange={(e) => setNote(e.target.value)} placeholder="不須必填" disabled={loading} />
                          <Form.Text muted>不須必填。</Form.Text>
                        </Form.Group>

                        <Form.Group className="mb-3">
                          <Form.Label>整筆訂單折價 (%)</Form.Label>
                          <InputGroup>
                            <Form.Control
                                type="number" min="0" max="100" step="any"
                                value={discountPercentInput}
                                onChange={(e) => setDiscountPercentInput(e.target.value)}
                                placeholder="輸入折扣百分比 (0-100)"
                                disabled={loading}
                            />
                            <InputGroup.Text>%</InputGroup.Text>
                          </InputGroup>
                        </Form.Group>
                      </Col>
                </Row>

                <Row className="mt-4">
                    <Col className="d-flex justify-content-end gap-2">
                        <Button variant="primary" type="submit" disabled={loading || optionsLoading}>
                            {loading ? <><Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" /> 處理中...</> : "確認"}
                        </Button>
                        <Button variant="secondary" onClick={() => {
                            localStorage.removeItem('addTherapySellFormState');
                            localStorage.removeItem('newlySelectedTherapyPackagesWithSessions');
                            navigate("/therapy-sell");
                        }} disabled={loading}>
                            取消
                        </Button>
                        <Button variant="outline-secondary" onClick={handlePrint} disabled={loading}>
                            列印
                        </Button>
                    </Col>
                </Row>
            </Form>
        </Container>
    );

    return (
        <>
            <Header title="新增銷售療程 1.1.3.1" />
            <DynamicContainer content={content} className="p-0" /> {/* 讓 Container 控制 padding */}
        </>
    );
};
export default AddTherapySell;