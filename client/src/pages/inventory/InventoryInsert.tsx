import React, { useEffect, useState } from "react";
import { Container, Row, Col, Form, Button } from "react-bootstrap";
import { getAllProducts, getSaleCategories } from "../../services/ProductSellService";
import { useNavigate } from "react-router-dom";

interface Product {
  product_id: number;
  product_name: string;
  product_price: number;
  inventory_id: number;
  quantity: number;
  sale_category?: string;
}

const InventoryInsert = () => {
  const navigate = useNavigate();
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [formData, setFormData] = useState({
    product_id: "",
    category: "",
    date: "",
    note: ""
  });

  useEffect(() => {
    getAllProducts().then((res) => {
      console.log("產品資料:", res);
      setProducts(res);
    });

    getSaleCategories().then((res) => {
      console.log("類別資料:", res);
      setCategories(res);
    });
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = () => {
    const payload = {
      product_id: formData.product_id,
      category: formData.category,
      date: formData.date,
      note: formData.note
    };
    console.log("送出 payload：", payload);
    alert("模擬送出成功！");
  };

  return (
    <Container
  className="mt-4"
  style={{ marginLeft: "200px", paddingRight: "30px", maxWidth: "calc(100% - 220px)" }}
>
      <h4 className="text-info fw-bold mb-4">新增庫存資料 1.1.4.3.1</h4>
      <Form>
        <Row className="mb-3">
          <Col xs={12} md={6}>
            <Form.Group controlId="product_id">
              <Form.Label>品項</Form.Label>
              <Form.Select
                name="product_id"
                value={formData.product_id}
                onChange={handleChange}
              >
                <option value="">-- 選擇品項 --</option>
                {products.map((p) => (
                  <option key={p.product_id} value={p.product_id}>
                    [{p.product_id}] {p.product_name}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>

          <Col xs={12} md={6}>
            <Form.Group controlId="category">
              <Form.Label>類別</Form.Label>
              <Form.Select
                name="category"
                value={formData.category}
                onChange={handleChange}
              >
                <option value="">-- 選擇類別 --</option>
                {categories.map((cat, idx) => (
                  <option key={`cat-${idx}`} value={cat}>
                    {cat}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
        </Row>

        <Row className="mb-3">
          <Col xs={12} md={6}>
            <Form.Group controlId="date">
              <Form.Label>進貨日期</Form.Label>
              <Form.Control
                type="date"
                name="date"
                value={formData.date}
                onChange={handleChange}
              />
            </Form.Group>
          </Col>

          <Col xs={12} md={6}>
            <Form.Group controlId="note">
              <Form.Label>備註</Form.Label>
              <Form.Control
                type="text"
                name="note"
                value={formData.note}
                onChange={handleChange}
              />
            </Form.Group>
          </Col>
        </Row>

        <Row className="text-center g-2">
          <Col xs={12} md={2} className="ms-auto">
            <Button variant="info" className="w-100 text-white" onClick={handleSubmit}>
              確認
            </Button>
          </Col>
        </Row>
      </Form>
    </Container>
  );
};

export default InventoryInsert;
