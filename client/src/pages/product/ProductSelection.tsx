import React, { useState, useEffect } from "react";
import { Button, Container, Row, Col, Form, Table } from "react-bootstrap";
import { useNavigate, useLocation } from "react-router-dom";
import Header from "../../components/Header";
import DynamicContainer from "../../components/DynamicContainer";
import { getAllProducts } from "../../services/ProductSellService";

interface Product {
  product_id: number;
  product_name: string;
  product_price: number;
  inventory_id: number;
  quantity: number;
}

interface SelectedProduct {
  product_id: number;
  name: string;
  price: number;
  quantity: number;
  inventory_id: number;
}

const ProductSelection: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProducts, setSelectedProducts] = useState<SelectedProduct[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchKeyword, setSearchKeyword] = useState("");
  const [selectedProduct, setSelectedProduct] = useState<number | "">("");

  // 載入產品資料
  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      try {
        const data = await getAllProducts();
        setProducts(data);
      } catch (err) {
        console.error("載入產品資料失敗：", err);
        setError("載入產品資料失敗");
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();

    // 如果從編輯頁面帶有已選擇的產品
    const state = location.state as { selectedProducts?: SelectedProduct[] };
    if (state?.selectedProducts) {
      setSelectedProducts(state.selectedProducts);
    } else {
      // 預設至少有一個空項目
      addNewItem();
    }
  }, [location]);

  // 計算總價
  const calculateTotal = () => {
    return selectedProducts.reduce((total, item) => total + item.price * item.quantity, 0);
  };

  // 添加新的項目
  const addNewItem = () => {
    setSelectedProducts([...selectedProducts, { product_id: 0, name: "", price: 0, quantity: 1, inventory_id: 0 }]);
  };

  // 移除項目
  const removeItem = (index: number) => {
    const newSelectedProducts = [...selectedProducts];
    newSelectedProducts.splice(index, 1);
    setSelectedProducts(newSelectedProducts);
  };

  // 更新選擇的產品
  const updateSelectedProduct = (index: number, productId: number) => {
    const product = products.find(p => p.product_id === productId);
    if (!product) return;

    const newSelectedProducts = [...selectedProducts];
    newSelectedProducts[index] = {
      ...newSelectedProducts[index],
      product_id: product.product_id,
      name: product.product_name,
      price: product.product_price,
      inventory_id: product.inventory_id
    };
    setSelectedProducts(newSelectedProducts);
  };

  // 更新數量
  const updateQuantity = (index: number, quantity: number) => {
    if (quantity < 1) return;
    
    const newSelectedProducts = [...selectedProducts];
    newSelectedProducts[index] = {
      ...newSelectedProducts[index],
      quantity
    };
    setSelectedProducts(newSelectedProducts);
  };

  // 確認選擇
  const confirmSelection = () => {
    // 過濾掉未選產品的項目
    const validProducts = selectedProducts.filter(item => item.product_id !== 0);
    
    // 如果沒有有效選擇，顯示錯誤
    if (validProducts.length === 0) {
      setError("請選擇至少一項產品");
      return;
    }
    
    // 設置產品數據到localStorage，以確保它可以被AddProductSell獲取
    localStorage.setItem('selectedProducts', JSON.stringify(validProducts));
    localStorage.setItem('productTotalAmount', calculateTotal().toString());
    
    // 返回前一頁
    navigate(-1 as any);
  };

  // 主要內容
  const content = (
    <Container className="my-4">
      {error && <div className="alert alert-danger">{error}</div>}
      
      <Row className="mb-4">
        <Col>
          <h5>選擇產品</h5>
          <p className="text-muted">請選擇要購買的產品並設定數量</p>
        </Col>
      </Row>

      <Row className="mb-3">
        <Col md={6}>
          <Form.Group>
            <Form.Label>產品搜尋</Form.Label>
            <Form.Control 
              type="text" 
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              placeholder="輸入產品名稱進行搜尋"
            />
          </Form.Group>
        </Col>
        <Col md={6} className="d-flex align-items-end">
          <Button 
            variant="info" 
            className="text-white"
            disabled={loading}
            onClick={() => {}}
          >
            搜尋
          </Button>
        </Col>
      </Row>

      <Table bordered className="mt-4">
        <thead>
          <tr>
            <th style={{width: "40%"}}>產品名稱</th>
            <th style={{width: "20%"}}>單價</th>
            <th style={{width: "20%"}}>數量</th>
            <th style={{width: "15%"}}>小計</th>
            <th style={{width: "5%"}}></th>
          </tr>
        </thead>
        <tbody>
          {selectedProducts.map((item, index) => (
            <tr key={index}>
              <td>
                <Form.Select 
                  value={item.product_id || ""}
                  onChange={(e) => updateSelectedProduct(index, Number(e.target.value))}
                >
                  <option value="">請選擇產品</option>
                  {products.filter(p => 
                    searchKeyword ? p.product_name.includes(searchKeyword) : true
                  ).map(product => (
                    <option key={product.product_id} value={product.product_id}>
                      {product.product_name}
                    </option>
                  ))}
                </Form.Select>
              </td>
              <td className="align-middle text-end">
                {item.price ? `NT$ ${item.price.toLocaleString()}` : "-"}
              </td>
              <td>
                <Form.Control
                  type="number"
                  min="1"
                  value={item.quantity}
                  onChange={(e) => updateQuantity(index, parseInt(e.target.value) || 1)}
                />
              </td>
              <td className="align-middle text-end">
                {item.price ? `NT$ ${(item.price * item.quantity).toLocaleString()}` : "-"}
              </td>
              <td className="text-center">
                <Button 
                  variant="danger" 
                  size="sm"
                  onClick={() => removeItem(index)}
                  disabled={selectedProducts.length <= 1}
                >
                  <i className="bi bi-trash"></i>
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={5}>
              <Button 
                variant="info" 
                className="text-white w-100"
                onClick={addNewItem}
              >
                新增產品項目
              </Button>
            </td>
          </tr>
          <tr>
            <th colSpan={3} className="text-end">總計金額：</th>
            <th colSpan={2} className="text-end">NT$ {calculateTotal().toLocaleString()}</th>
          </tr>
        </tfoot>
      </Table>

      <Row className="mt-4">
        <Col className="d-flex justify-content-end gap-3">
          <Button 
            variant="secondary" 
            onClick={() => navigate(-1 as any)}
          >
            取消
          </Button>
          <Button 
            variant="info" 
            className="text-white"
            onClick={confirmSelection}
          >
            確認選擇
          </Button>
        </Col>
      </Row>
    </Container>
  );

  return (
    <>
      <Header title="選擇產品" />
      <DynamicContainer content={content} />
    </>
  );
};

export default ProductSelection; 