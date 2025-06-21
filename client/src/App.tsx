import React, { useEffect } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import { setupAxiosInterceptors } from "./services/AuthUtils";
import ProtectedRoute from "./components/ProtectedRoute";

// 匯入分頁
import Home from "./pages/Home";
import Login from "./pages/Login";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";

// Member
import MamberManagement from "./pages/member/MemberManagement";
import MemberInfo from "./pages/member/MemberInfo";
import AddMember from "./pages/member/AddMember"
import EditMember from "./pages/member/EditMember";

// Medical Record
import MedicalRecord from "./pages/medical_record/MedicalRecord";
import AddMedicalRecord from "./pages/medical_record/AddMedicalRecord";
import AddFamilyMedicalHistoryForm from "./pages/medical_record/AddFamilyMedicalHistory";
import UsualSymptomsAndFamilyHistory from "./pages/medical_record/UsualSymptomsAndFamilyHistory";

// Health
import HealthDataAnalysis from "./pages/health/HealthDataAnalysis";
import StressTest from "./pages/health/stress_test/StressTest";
import AddStressTestPage1 from "./pages/health/stress_test/AddStressTestPage1";
import AddStressTestPage2 from "./pages/health/stress_test/AddStressTestPage2";
import HealthRecord from "./pages/health/pure_medical_record/PureMedicalRecord";
import AddPureMedicalRecord from "./pages/health/pure_medical_record/AddPureMedicalRecord";

// Therapy
import TherapyRecord from "./pages/therapy/TherapyRecord";
import AddTherapyRecord from "./pages/therapy/AddTherapyRecord";
import TherapySell from "./pages/therapy/TherapySell";
import AddTherapySell from "./pages/therapy/AddTherapySell";
import TherapyPackageSelection from "./pages/therapy/TherapyPackageSelection";

// Product
import ProductSell from "./pages/product/ProductSell";
import AddProductSell from "./pages/product/AddProductSell";
import ProductSelection from "./pages/product/ProductSelection";
import EditProductSell from './pages/product/EditProductSell'; 

// Inventory
import InventoryManagement from "./pages/inventory/InventoryManagement";
import InventorySearch from "./pages/inventory/InventorySearch";
import InventoryAnalysis from "./pages/inventory/InventoryAnalysis";
import InventoryUpdate from "./pages/inventory/InventoryUpdate";
import AddInventory from "./pages/inventory/AddInventory";
import InventoryNotification from "./pages/inventory/InventoryNotification";
// Backend
import BranchBackend from "./pages/backend/BranchBackend";
import Staff from "./pages/backend/Staff";
import AddStaff from "./pages/backend/AddStaff";

// 帳務管理
import FinanceDashboard from './pages/finance/FinanceDashboard'; 
import AddSalesOrder from './pages/finance/AddSalesOrder';     
import ItemSelection from './pages/finance/ItemSelection';
import SalesOrderList from './pages/finance/SalesOrderList';

// 匯入Component
import Sidebar from "./components/Siderbar/Sidebar";

// 添加全局樣式
import "./global.css";

const App: React.FC = () => {
    const location = useLocation();
    const isLoginPage = (location.pathname === "/");
    
    // Set up axios interceptors for authentication
    useEffect(() => {
        setupAxiosInterceptors();
    }, []);
    
    // 登入頁面不顯示側邊欄，直接返回
    if (isLoginPage) {
        return (
            <div className="app-container">
                <Routes>
                    <Route path="/" element={<Login />} />
                </Routes>
            </div>
        );
    }
    
    // 其他頁面使用側邊欄佈局
    return (
        <div className="app-layout">
            <Sidebar />
            <div className="main-content">
                <Routes>
                    <Route path="/forgot-password" element={<ForgotPassword />} />
                    <Route path="/reset-password" element={<ResetPassword />} />
                    <Route path="/home" element={<ProtectedRoute element={<Home />} />} />

                    {/* Member */}
                    <Route path="/member-management" element={<ProtectedRoute element={<MamberManagement />} />} />
                    <Route path="/member-info" element={<ProtectedRoute element={<MemberInfo />} />} />
                    <Route path="/add-member" element={<ProtectedRoute element={<AddMember />} />} />
                    <Route path="/member-info/edit/:memberId" element={<ProtectedRoute element={<EditMember />} />} />

                    {/* Medical Record */}
                    <Route path="/medical-record" element={<ProtectedRoute element={<MedicalRecord />} />} />
                    <Route path="/medical-record/add" element={<ProtectedRoute element={<AddMedicalRecord />} />} />
                    <Route path="/medical-record/add-medical-record" element={<ProtectedRoute element={<AddMedicalRecord />} />} />
                    <Route path="/medical-record/add-family-medical-history" element={<ProtectedRoute element={<AddFamilyMedicalHistoryForm />} />} />
                    <Route path="/medical-record/symptoms-and-history" element={<ProtectedRoute element={<UsualSymptomsAndFamilyHistory />} />} />
                    <Route path="/medical-record/edit/:id" element={<AddMedicalRecord />} />

                    {/* Therapy Record */}
                    <Route path="/therapy-record" element={<ProtectedRoute element={<TherapyRecord />} />} />
                    <Route path="/therapy-record/add-therapy-record" element={<ProtectedRoute element={<AddTherapyRecord />} />} />

                    {/* Therapy Sell */}
                    <Route path="/therapy-sell" element={<ProtectedRoute element={<TherapySell />} />} />
                    <Route path="/therapy-sell/add" element={<ProtectedRoute element={<AddTherapySell />} />} />
                    
                    <Route path="/therapy-package-selection" element={<ProtectedRoute element={<TherapyPackageSelection />} />} />

                    {/* Product */}
                    <Route path="/product-sell" element={<ProtectedRoute element={<ProductSell />} />} />
                    <Route path="/add-product-sell" element={<ProtectedRoute element={<AddProductSell />} />} />
                    <Route path="/product-selection" element={<ProtectedRoute element={<ProductSelection />} />} />
                    <Route path="/product-sell/edit/:sellId" element={<EditProductSell />} />

                    {/* Inventory */}
                    <Route path="/inventory" element={<ProtectedRoute element={<InventoryManagement />} />} />
                    <Route path="/inventory/inventory-search" element={<ProtectedRoute element={<InventorySearch />} />} />
                    <Route path="/inventory/inventory-analysis" element={<ProtectedRoute element={<InventoryAnalysis />} />} />
                    <Route path="/inventory/inventory-update" element={<ProtectedRoute element={<InventoryUpdate />} />} />
                    <Route path="/inventory/inventory-add" element={<ProtectedRoute element={<AddInventory />} />} />
                    <Route path="/inventory/inventory-notification" element={<ProtectedRoute element={<InventoryNotification />} />} />
                    
                    {/* Backend - Admin Only */}
                    <Route path="/backend" element={<ProtectedRoute element={<BranchBackend />} adminOnly={true} />} />
                    <Route path="/backend/staff" element={<ProtectedRoute element={<Staff />} adminOnly={true} />} />
                    <Route path="/backend/add-staff" element={<ProtectedRoute element={<AddStaff />} adminOnly={true} />} />
                
                    {/* Health */}
                    <Route path="/health-data-analysis" element={<ProtectedRoute element={<HealthDataAnalysis />} />} />
                    <Route path="/health-data-analysis/stress-test" element={<ProtectedRoute element={<StressTest />} />} />
                    <Route path="/health-data-analysis/stress-test/add/page1" element={<ProtectedRoute element={<AddStressTestPage1 />} />} />
                    <Route path="/health-data-analysis/stress-test/add/page2" element={<ProtectedRoute element={<AddStressTestPage2 />} />} />
                    <Route path="/health-data-analysis/pure-medical-record" element={<ProtectedRoute element={<HealthRecord />} />} />
                    <Route path="/health-data-analysis/add-pure-medical-record" element={<ProtectedRoute element={<AddPureMedicalRecord />} />} />

                    {/* 帳務管理 */}
                    <Route path="/finance" element={<FinanceDashboard />} />
                    <Route path="/finance/sales/list" element={<SalesOrderList />} />
                    <Route path="/finance/sales/add" element={<AddSalesOrder />} />
                    <Route path="/finance/item-selection" element={<ItemSelection />} />
                    {/* 未來修改銷售單的路由 */}
                    {/* <Route path="/finance/sales/edit/:orderId" element={<EditSalesOrder />} /> */}
                    {/* ... */}

                </Routes>
            </div>
        </div>
    );
};

export default App;
