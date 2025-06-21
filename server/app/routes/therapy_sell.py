from flask import Blueprint, request, jsonify, send_file, session
from app.models.therapy_sell_model import (
    get_all_therapy_sells, search_therapy_sells, 
    insert_many_therapy_sells , update_therapy_sell, delete_therapy_sell,
    get_all_therapy_packages, search_therapy_packages,
    get_all_members, get_all_staff, get_all_stores 
)
from app.middleware import login_required
import pandas as pd
import io
from datetime import datetime
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)


therapy_sell = Blueprint('therapy_sell', __name__)


@therapy_sell.route('/sales', methods=['POST'])
def add_therapy_transaction_route():
    sales_list_from_request = request.json

    if not isinstance(sales_list_from_request, list) or not sales_list_from_request:
        return jsonify({"success": False, "error": "請求數據應為一個包含療程銷售項目的非空陣列"}), 400
    
    try:
        result = insert_many_therapy_sells(sales_list_from_request) # 將解析後的列表傳遞

        if isinstance(result, dict) and result.get("success"):
            return jsonify(result), 201
        elif isinstance(result, dict) and "error" in result:
             # Model 層已經處理了錯誤並返回了包含錯誤訊息的字典
            return jsonify(result), 400 # 或 500，取決於錯誤的嚴重性
        else: 
            return jsonify({"success": False, "error": "伺服器處理時發生未預期的結果格式"}), 500
            
    except Exception as e:
        tb_str = traceback.format_exc() # <--- 獲取完整 Traceback 字串
        return jsonify({"success": False, "error": f"伺服器路由層發生嚴重錯誤: {str(e)}", "traceback": tb_str}), 500


@therapy_sell.route('/packages', methods=['GET'])
def get_packages():
    """獲取所有療程套餐"""
    try:
        result = get_all_therapy_packages()
        return jsonify(result)
    except Exception as e:
        print(f"獲取療程套餐失敗: {e}")
        return jsonify({"error": str(e)}), 500

@therapy_sell.route('/packages/search', methods=['GET'])
def search_packages():
    """搜尋療程套餐"""
    try:
        keyword = request.args.get('keyword', '')
        result = search_therapy_packages(keyword)
        return jsonify(result)
    except Exception as e:
        print(f"搜尋療程套餐失敗: {e}")
        return jsonify({"error": str(e)}), 500

@therapy_sell.route('/sales', methods=['GET'])
@login_required
def get_sales():
    """獲取所有療程銷售紀錄"""
    try:
        # 從 session 獲取用戶的 store_id，如果有的話
        store_id = None
        if 'user' in session and 'store_id' in session['user']:
            store_id = session['user']['store_id']
            
        # 從 URL 參數中獲取 store_id，這會覆蓋 session 中的值
        if request.args.get('store_id'):
            store_id = request.args.get('store_id')
        
        # 檢查用戶是否是管理員，如果是，則允許他們查看所有店鋪的記錄
        is_admin = False
        if 'user' in session and 'is_admin' in session['user']:
            is_admin = session['user']['is_admin']
            
        # 如果用戶不是管理員，必須提供 store_id
        if not is_admin and not store_id:
            return jsonify({"error": "缺少店鋪ID，非管理員必須指定店鋪"}), 400
            
        # 獲取數據
        result = get_all_therapy_sells(store_id if not is_admin else None)
        return jsonify(result)
    except Exception as e:
        print(f"獲取療程銷售失敗: {e}")
        return jsonify({"error": str(e)}), 500

@therapy_sell.route('/sales/search', methods=['GET'])
@login_required
def search_sales():
    """搜尋療程銷售紀錄"""
    try:
        keyword = request.args.get('keyword', '')
        
        # 從 session 獲取用戶的 store_id，如果有的話
        store_id = None
        if 'user' in session and 'store_id' in session['user']:
            store_id = session['user']['store_id']
            
        # 從 URL 參數中獲取 store_id，這會覆蓋 session 中的值
        if request.args.get('store_id'):
            store_id = request.args.get('store_id')
        
        # 檢查用戶是否是管理員，如果是，則允許他們查看所有店鋪的記錄
        is_admin = False
        if 'user' in session and 'is_admin' in session['user']:
            is_admin = session['user']['is_admin']
            
        # 如果用戶不是管理員，必須提供 store_id
        if not is_admin and not store_id:
            return jsonify({"error": "缺少店鋪ID，非管理員必須指定店鋪"}), 400
            
        result = search_therapy_sells(keyword, store_id if not is_admin else None)
        return jsonify(result)
    except Exception as e:
        print(f"搜尋療程銷售失敗: {e}")
        return jsonify({"error": str(e)}), 500

@therapy_sell.route('/sales', methods=['POST'])
@login_required
def create_sale():
    """新增療程銷售紀錄"""
    try:
        data = request.get_json()
        
        # 從 session 獲取用戶的 store_id 和 staff_id
        if 'user' in session:
            if 'store_id' in session['user'] and not data.get('storeId'):
                data['storeId'] = session['user']['store_id']
            if 'staff_id' in session['user'] and not data.get('staffId'):
                data['staffId'] = session['user']['staff_id']
                
        # 驗證必要數據
        if not data.get('memberId'):
            return jsonify({"error": "會員ID不能為空"}), 400
            
        if not data.get('storeId'):
            return jsonify({"error": "店鋪ID不能為空"}), 400
            
        if not data.get('staffId'):
            return jsonify({"error": "銷售人員ID不能為空"}), 400
        
        result = insert_therapy_sell(data)
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result), 201
    except Exception as e:
        print(f"新增療程銷售失敗: {e}")
        return jsonify({"error": str(e)}), 500

'''@therapy_sell.route('/sales/<int:sale_id>', methods=['PUT'])
@login_required
def update_sale(sale_id):
    """更新療程銷售紀錄"""
    try:
        data = request.get_json()
        
        # 從 session 獲取用戶的 store_id 和 staff_id，如果數據中沒有提供的話
        if 'user' in session:
            if 'store_id' in session['user'] and not data.get('storeId'):
                data['storeId'] = session['user']['store_id']
                
        result = update_therapy_sell(sale_id, data)
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        print(f"更新療程銷售失敗: {e}")
        return jsonify({"error": str(e)}), 500'''

@therapy_sell.route('/sales/<int:sale_id>', methods=['DELETE'])
@login_required
def delete_sale(sale_id):
    """刪除療程銷售紀錄"""
    try:
        result = delete_therapy_sell(sale_id)
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        print(f"刪除療程銷售失敗: {e}")
        return jsonify({"error": str(e)}), 500

@therapy_sell.route('/sales/export', methods=['GET'])
@login_required
def export_sales():
    """匯出療程銷售紀錄"""
    try:
        # 從 session 獲取用戶的 store_id
        store_id = None
        if 'user' in session and 'store_id' in session['user']:
            store_id = session['user']['store_id']
            
        # 從 URL 參數中獲取 store_id，這會覆蓋 session 中的值
        if request.args.get('store_id'):
            store_id = request.args.get('store_id')
        
        # 檢查用戶是否是管理員，如果是，則允許他們匯出所有店鋪的記錄
        is_admin = False
        if 'user' in session and 'is_admin' in session['user']:
            is_admin = session['user']['is_admin']
            
        # 如果用戶不是管理員，必須提供 store_id
        if not is_admin and not store_id:
            return jsonify({"error": "缺少店鋪ID，非管理員必須指定店鋪"}), 400
            
        sales = get_all_therapy_sells(store_id if not is_admin else None)
        
        # 檢查是否有銷售記錄
        if not sales or (isinstance(sales, dict) and "error" in sales):
            # 如果沒有銷售記錄或發生錯誤，創建一個空的DataFrame
            df = pd.DataFrame(columns=[
                'Order_ID', 'MemberName', 'PurchaseDate', 'PackageName', 
                'Sessions', 'PaymentMethod', 'StaffName', 'store_name', 'note'
            ])
        else:
            # 創建 DataFrame
            df = pd.DataFrame(sales)
            
            # 確保所有必要的列都存在
            required_columns = [
                'Order_ID', 'MemberName', 'PurchaseDate', 'PackageName', 
                'Sessions', 'PaymentMethod', 'StaffName', 'store_name', 'note'
            ]
            
            # 添加缺失的列
            for column in required_columns:
                if column not in df.columns:
                    df[column] = ''
            
            # 只選擇需要的列
            df = df[required_columns]
        
        # 重命名列為中文
        column_mapping = {
            'Order_ID': '訂單編號',
            'MemberName': '會員姓名',
            'PurchaseDate': '購買日期',
            'PackageName': '療程名稱',
            'Sessions': '金額',
            'PaymentMethod': '付款方式',
            'StaffName': '銷售人員',
            'store_name': '店鋪名稱',
            'note': '備註'
        }
        df = df.rename(columns=column_mapping)
        
        # 寫入 Excel 文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='療程銷售紀錄')
            
            # 自動調整列寬
            worksheet = writer.sheets['療程銷售紀錄']
            for i, col in enumerate(df.columns):
                # 計算列最大寬度
                max_len = max(
                    df[col].astype(str).map(len).max() if not df.empty else 0,
                    len(col)
                ) + 2
                worksheet.set_column(i, i, max_len)
        
        output.seek(0)
        
        # 設置文件名（使用當前日期）
        current_date = datetime.now().strftime("%Y%m%d")
        filename = f"therapy_sells_{current_date}.xlsx"
        
        return send_file(
            output, 
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"匯出療程銷售失敗: {e}")
        return jsonify({"error": str(e)}), 500

@therapy_sell.route('/members', methods=['GET'])
def get_members():
    """獲取所有會員"""
    try:
        result = get_all_members()
        return jsonify(result)
    except Exception as e:
        print(f"獲取會員列表失敗: {e}")
        return jsonify({"error": str(e)}), 500

@therapy_sell.route('/staff', methods=['GET'])
def get_staff():
    """獲取所有員工"""
    try:
        result = get_all_staff()
        return jsonify(result)
    except Exception as e:
        print(f"獲取員工列表失敗: {e}")
        return jsonify({"error": str(e)}), 500

@therapy_sell.route('/stores', methods=['GET'])
def get_stores():
    """獲取所有店鋪"""
    try:
        result = get_all_stores()
        return jsonify(result)
    except Exception as e:
        print(f"獲取店鋪列表失敗: {e}")
        return jsonify({"error": str(e)}), 500 