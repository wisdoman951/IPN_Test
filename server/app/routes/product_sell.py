from flask import Blueprint, request, jsonify, send_file
import pandas as pd
import io
from app.models.product_sell_model import (
    get_all_product_sells, 
    search_product_sells, 
    get_product_sell_by_id,
    insert_product_sell, 
    update_product_sell, 
    delete_product_sell,
    get_all_products_with_inventory,
    search_products_with_inventory,
    export_product_sells
)
from app.middleware import auth_required, admin_required, get_user_from_token

product_sell_bp = Blueprint("product_sell", __name__)

@product_sell_bp.route("/list", methods=["GET"])
@auth_required
def get_sales():
    """獲取所有產品銷售記錄"""
    try:
        # 獲取用戶資訊，包括 store_id
        user = get_user_from_token(request)
        store_id = user.get('store_id') if user else None
        
        # 如果用戶有 store_id，則只返回該店鋪的記錄
        if store_id:
            sales = search_product_sells("", store_id)
        else:
            sales = get_all_product_sells()
            
        return jsonify(sales)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_sell_bp.route("/detail/<int:sale_id>", methods=["GET"])
@auth_required
def get_sale_detail(sale_id):
    """獲取產品銷售記錄詳情"""
    try:
        sale = get_product_sell_by_id(sale_id)
        if not sale:
            return jsonify({"error": "找不到產品銷售記錄"}), 404
        
        # 獲取用戶資訊
        user = get_user_from_token(request)
        
        # 限制只能查看自己商店的記錄
        if user and user.get('store_id') and sale.get('store_id') != user.get('store_id'):
            return jsonify({"error": "無權限查看其他商店的記錄"}), 403
            
        return jsonify(sale)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_sell_bp.route("/search", methods=["GET"])
@auth_required
def search_sales():
    """搜尋產品銷售記錄"""
    keyword = request.args.get("keyword", "")
    try:
        # 獲取用戶資訊，包括 store_id
        user = get_user_from_token(request)
        store_id = user.get('store_id') if user else None
        
        # 根據 store_id 進行搜尋
        sales = search_product_sells(keyword, store_id)
        return jsonify(sales)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_sell_bp.route("/add", methods=["POST"])
@auth_required
def add_sale():
    """新增產品銷售記錄"""
    data = request.json
    try:
        # 獲取用戶資訊，包括 store_id
        user = get_user_from_token(request)
        
        # 合併 user 信息到 data
        if user and user.get("store_id") and not data.get("store_id"):
            data["store_id"] = user.get("store_id")
        
        sale_id = insert_product_sell(data)
        return jsonify({"message": "產品銷售記錄新增成功", "id": sale_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_sell_bp.route("/update/<int:sale_id>", methods=["PUT"])
@auth_required
def update_sale(sale_id):
    """更新產品銷售記錄"""
    data = request.json
    try:
        # 檢查記錄是否存在
        sale = get_product_sell_by_id(sale_id)
        if not sale:
            return jsonify({"error": "找不到產品銷售記錄"}), 404
            
        # 獲取用戶資訊
        user = get_user_from_token(request)
        
        # 限制只能操作自己商店的記錄
        if user and user.get('store_id') and sale.get('store_id') != user.get('store_id'):
            return jsonify({"error": "無權限修改其他商店的記錄"}), 403
            
        update_product_sell(sale_id, data)
        return jsonify({"message": "產品銷售記錄更新成功"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_sell_bp.route("/delete/<int:sale_id>", methods=["DELETE"])
@auth_required
def delete_sale(sale_id):
    """刪除產品銷售記錄"""
    try:
        # 檢查記錄是否存在
        sale = get_product_sell_by_id(sale_id)
        if not sale:
            return jsonify({"error": "找不到產品銷售記錄"}), 404
            
        # 獲取用戶資訊
        user = get_user_from_token(request)
        
        # 限制只能操作自己商店的記錄
        if user and user.get('store_id') and sale.get('store_id') != user.get('store_id'):
            return jsonify({"error": "無權限刪除其他商店的記錄"}), 403
            
        delete_product_sell(sale_id)
        return jsonify({"message": "產品銷售記錄刪除成功"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_sell_bp.route("/products", methods=["GET"])
@auth_required
def get_products():
    """獲取所有產品及庫存"""
    try:
        products = get_all_products_with_inventory()
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_sell_bp.route("/products/search", methods=["GET"])
@auth_required
def search_product():
    """搜尋產品及庫存"""
    keyword = request.args.get("keyword", "")
    try:
        products = search_products_with_inventory(keyword)
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_sell_bp.route("/export", methods=["GET"])
@auth_required
def export_sales():
    """匯出產品銷售紀錄"""
    try:
        # 獲取用戶資訊
        user = get_user_from_token(request)
        store_id = user.get('store_id') if user else None
        
        # 獲取資料
        sales = export_product_sells(store_id)
        
        # 過濾和重命名欄位以適合匯出
        export_data = [{
            '銷售ID': r.get('product_sell_id'),
            '會員ID': r.get('member_id'),
            '會員姓名': r.get('member_name'),
            '商店名稱': r.get('store_name'),
            '產品名稱': r.get('product_name'),
            '產品價格': r.get('product_price'),
            '庫存數量': r.get('quantity'),
            '日期': r.get('date'),
            '折扣': r.get('discount'),
            '最終價格': r.get('final_price'),
            '備註': r.get('note')
        } for r in sales]
        
        # 使用pandas創建DataFrame
        df = pd.DataFrame(export_data)
        
        # 創建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='ProductSales')
            
            # 美化Excel
            workbook = writer.book
            worksheet = writer.sheets['ProductSales']
            
            # 添加標題行格式
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D9EAD3',
                'border': 1
            })
            
            # 應用標題行格式
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # 自動調整列寬
            for i, col in enumerate(df.columns):
                column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, column_width)

        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='產品銷售紀錄.xlsx'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500 