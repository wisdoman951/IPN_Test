import io
import xlsxwriter
import json

from flask import Blueprint, request, jsonify, send_file
from app.models.pure_medical_record_model import (
    get_all_pure_records,
    add_pure_record,
    update_pure_record,
    delete_pure_record,
    get_pure_record_by_id,
    get_pure_records_by_member_id,
    export_pure_records
)
from app.middleware import auth_required, login_required

pure_medical_bp = Blueprint("pure-medical-record", __name__)

@pure_medical_bp.route("", methods=["GET"])
@login_required
def list_pure_records():
    """獲取所有淨化健康紀錄"""
    try:
        # 獲取查詢參數
        name = request.args.get("name", "")
        pure_item = request.args.get("pure_item", "")
        staff_name = request.args.get("staff_name", "")
        
        # 構建過濾條件
        filters = {}
        if name:
            filters["name"] = name
        if pure_item:
            filters["pure_item"] = pure_item
        if staff_name:
            filters["staff_name"] = staff_name
            
        # 獲取紀錄
        records = get_all_pure_records(filters if filters else None)
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pure_medical_bp.route("/search", methods=["GET"])
@login_required
def search_pure_records():
    """搜尋淨化健康紀錄"""
    try:
        # 獲取關鍵字
        keyword = request.args.get("keyword", "")
        if not keyword:
            return jsonify([])
            
        # 構建過濾條件，搜尋名字、淨化項目和服務人員
        filters = {
            "name": keyword,
            "pure_item": keyword,
            "staff_name": keyword
        }
        
        # 獲取紀錄
        records = get_all_pure_records(filters)
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pure_medical_bp.route("/filter", methods=["GET"])
@login_required
def filter_pure_records():
    """按條件過濾淨化健康紀錄"""
    try:
        # 獲取過濾條件
        name = request.args.get("name", "")
        pure_item = request.args.get("pure_item", "")
        staff_name = request.args.get("staff_name", "")
        
        # 構建過濾條件
        filters = {}
        if name:
            filters["name"] = name
        if pure_item:
            filters["pure_item"] = pure_item
        if staff_name:
            filters["staff_name"] = staff_name
            
        # 獲取紀錄
        records = get_all_pure_records(filters)
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pure_medical_bp.route("/member/<string:member_id>", methods=["GET"])
@login_required
def get_member_pure_records(member_id):
    """獲取特定會員的淨化健康紀錄"""
    try:
        records = get_pure_records_by_member_id(member_id)
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pure_medical_bp.route("/<int:pure_id>", methods=["GET"])
@login_required
def get_pure_record(pure_id):
    """獲取特定淨化健康紀錄"""
    try:
        record = get_pure_record_by_id(pure_id)
        if not record:
            return jsonify({"error": "找不到該紀錄"}), 404
        return jsonify(record)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pure_medical_bp.route("", methods=["POST"])
@login_required
def create_pure_record():
    """新增淨化健康紀錄"""
    try:
        data = request.get_json()
        
        # 確保必要欄位存在
        if not data.get('member_id'):
            return jsonify({"error": "會員編號不能為空"}), 400
            
        # 輸出接收到的資料（除錯用）
        print("接收到的淨化健康紀錄資料:", json.dumps(data, ensure_ascii=False))
        
        # 調用模型創建記錄
        record_id = add_pure_record(data)
        return jsonify({"success": True, "id": record_id})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"創建淨化健康紀錄時發生錯誤: {e}")
        return jsonify({"error": f"創建淨化健康紀錄時發生錯誤: {str(e)}"}), 500

@pure_medical_bp.route("/<int:pure_id>", methods=["PUT"])
@login_required
def update_record(pure_id):
    """更新淨化健康紀錄"""
    try:
        data = request.get_json()
        
        # 確保記錄存在
        existing_record = get_pure_record_by_id(pure_id)
        if not existing_record:
            return jsonify({"error": "找不到該紀錄"}), 404
            
        # 輸出接收到的資料（除錯用）
        print(f"更新淨化健康紀錄 {pure_id}:", json.dumps(data, ensure_ascii=False))
        
        # 調用模型更新記錄
        success = update_pure_record(pure_id, data)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pure_medical_bp.route("/<int:pure_id>", methods=["DELETE"])
@login_required
def delete_record(pure_id):
    """刪除淨化健康紀錄"""
    try:
        # 確保記錄存在
        existing_record = get_pure_record_by_id(pure_id)
        if not existing_record:
            return jsonify({"error": "找不到該紀錄"}), 404
            
        # 調用模型刪除記錄
        success = delete_pure_record(pure_id)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pure_medical_bp.route("/export", methods=["GET"])
@login_required
def export_records():
    """導出淨化健康紀錄為Excel檔案"""
    try:
        # 獲取導出用的記錄
        records = export_pure_records()
        
        # 創建內存中的輸出流
        output = io.BytesIO()
        
        # 創建工作簿和工作表
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("淨化健康紀錄")
        
        # 設置表頭格式
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#D9EAD3',
            'border': 1
        })
        
        # 設置數據格式
        data_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        # 寫入表頭
        if records and len(records) > 0:
            headers = list(records[0].keys())
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
                worksheet.set_column(col, col, 15)  # 設置列寬
            
            # 寫入數據
            for row, record in enumerate(records, start=1):
                for col, header in enumerate(headers):
                    worksheet.write(row, col, record[header], data_format)
        
        # 關閉工作簿並獲取輸出
        workbook.close()
        output.seek(0)
        
        # 返回 Excel 文件
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            download_name="pure_medical_records.xlsx",
            as_attachment=True
        )
    except Exception as e:
        print(f"導出淨化健康紀錄時發生錯誤: {e}")
        return jsonify({"error": str(e)}), 500 