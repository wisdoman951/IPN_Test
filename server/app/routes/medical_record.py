import io
import xlsxwriter
import json

from flask import Blueprint, request, jsonify, send_file
from app.models.medical_record_model import (
    get_all_medical_records,
    search_medical_records,
    create_medical_record,
    delete_medical_record,
    get_all_medical_records_for_export,
    get_medical_record_by_id,
    update_medical_record
)

medical_bp = Blueprint("medical", __name__)

@medical_bp.route("/list", methods=["GET"])
def list_medical_records():
    try:
        records = get_all_medical_records()
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@medical_bp.route("/search", methods=["GET"])
def search_medical():
    keyword = request.args.get("keyword", "")
    try:
        result = search_medical_records(keyword)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@medical_bp.route("/create", methods=["POST"])
def create():
    try:
        data = request.get_json()
        
        # 確保必要欄位存在
        if not data.get('memberId'):
            return jsonify({"error": "會員編號不能為空"}), 400
            
        # 輸出接收到的資料（除錯用）
        print("接收到的資料:", json.dumps(data, ensure_ascii=False))
        
        # 調用 model 創建記錄
        record_id = create_medical_record(data)
        return jsonify({"success": True, "id": record_id})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"創建醫療記錄時發生錯誤: {e}")
        return jsonify({"error": f"創建醫療記錄時發生錯誤: {str(e)}"}), 500

@medical_bp.route("/delete/<int:record_id>", methods=["DELETE"])
def delete(record_id):
    try:
        success = delete_medical_record(record_id)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "記錄不存在"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@medical_bp.route("/export", methods=["GET"])
def export_medical_records():
    try:
        records = get_all_medical_records_for_export()
        
        # 創建內存中的輸出流
        output = io.BytesIO()
        
        # 創建工作簿和工作表
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("健康檢查紀錄")
        
        # 定義標題行
        headers = ["序號", "姓名", "會員編號", "身高", "體重", "血壓", "微整型", "微整型描述"]
        
        # 寫入標題
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # 寫入數據
        for row, record in enumerate(records, start=1):
            for col, value in enumerate(record):
                # 跳過第一個欄位 (medical_record_id)，直接使用行號作為序號
                if col == 0:
                    worksheet.write(row, col, row)
                else:
                    # 其他欄位往後偏移1個位置
                    worksheet.write(row, col, value if value is not None else "")
        
        # 關閉工作簿並獲取輸出
        workbook.close()
        output.seek(0)
        
        # 返回 Excel 文件
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            download_name="medical_records.xlsx",
            as_attachment=True
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------- 新增以下路由 -----------------
@medical_bp.route("/<int:record_id>", methods=["GET"])
def get_record(record_id):
    try:
        record = get_medical_record_by_id(record_id)
        if record:
            return jsonify(record)
        else:
            return jsonify({"error": "記錄不存在"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------- 新增以下路由 -----------------
@medical_bp.route("/update/<int:record_id>", methods=["PUT"])
def update(record_id):
    try:
        data = request.get_json()
        success = update_medical_record(record_id, data)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "更新失敗"}), 400
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"更新醫療記錄時發生錯誤: {e}")
        return jsonify({"error": f"更新醫療記錄時發生錯誤: {str(e)}"}), 500
