import pandas as pd
import io
import pymysql

from flask import Blueprint, request, jsonify, send_file
from app.config import DB_CONFIG
from app.middleware import auth_required, login_required
from app.models.member_model import (
    get_all_members,
    search_members,
    create_member,
    update_member,
    get_member_by_id,
    check_member_exists,
    get_next_member_code,
    delete_member_and_related_data as delete_member
)
member_bp = Blueprint("member", __name__)

@member_bp.route("/", methods=["GET"])
@login_required
def get_members_root():
    """根路徑處理程序，直接返回所有會員資料"""
    try:
        members = get_all_members()
        return jsonify(members)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@member_bp.route("/list", methods=["GET"])
@login_required
def get_members():
    """獲取所有會員資料"""
    try:
        members = get_all_members()
        return jsonify(members)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@member_bp.route("/search", methods=["GET"])
@login_required
def search_members_route():
    """根據關鍵字搜尋會員"""
    keyword = request.args.get("keyword", "")
    try:
        members = search_members(keyword)
        return jsonify(members)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@member_bp.route("/create", methods=["POST"])
@login_required
def create_member_route():
    """新增會員"""
    data = request.json
    try:
        # 從請求中獲取會員數據，同時支持蛇形命名和駝峰式命名
        member_data = {
            "name": data.get("name"),
            "birthday": data.get("birthday"),
            "address": data.get("address"),
            "phone": data.get("phone"),
            "gender": data.get("gender"),
            "blood_type": data.get("blood_type"),
            "line_id": data.get("line_id"),
            "inferrer_id": data.get("inferrer_id"),
            "occupation": data.get("occupation"),
            "note": data.get("note")
        }
        
        # 調用模型函數創建會員
        create_member(member_data)
        return jsonify({"message": "會員新增成功"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@member_bp.route("/<int:member_id>", methods=["DELETE"])
@login_required
def delete_member_route(member_id):
    """刪除會員及其所有相關資料"""
    try:
        result = delete_member(member_id) # 調用新函數
        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify({"error": result.get("error")}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@member_bp.route("/<int:member_id>", methods=["PUT"])
@login_required
def update_member_route(member_id):
    """更新會員資料"""
    data = request.json
    try:
        # 轉換資料格式以符合模型需求，同時支持蛇形命名和駝峰式命名
        member_data = {
            "name": data.get("name"),
            "birthday": data.get("birthday"),
            "address": data.get("address"),
            "phone": data.get("phone"),
            "gender": data.get("gender"),
            "blood_type": data.get("bloodType") or data.get("blood_type"),
            "line_id": data.get("lineId") or data.get("line_id"),
            "inferrer_id": data.get("inferrerId") or data.get("inferrer_id"),
            "occupation": data.get("occupation"),
            "note": data.get("note")
        }
        update_member(member_id, member_data)
        return jsonify({"message": "會員更新成功"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@member_bp.route("/export", methods=["GET"])
@login_required
def export_members():
    """匯出會員資料為Excel檔案"""
    try:
        members = get_all_members() 
        
        # 使用pandas創建DataFrame
        df = pd.DataFrame(members)
        
        # 中文欄位名稱映射
        column_mapping = {
            'member_id': '會員編號',
            'name': '姓名',
            'birthday': '生日',
            'address': '地址',
            'phone': '電話',
            'gender': '性別',
            'blood_type': '血型',
            'line_id': 'Line ID',
            'inferrer_id': '推薦人編號',
            'occupation': '職業',
            'note': '備註'
        }
        
        # 重命名DataFrame欄位
        df = df.rename(columns=column_mapping)
            
        # 創建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Members')
            
            # 可選：美化Excel
            workbook = writer.book
            worksheet = writer.sheets['Members']
            
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
            download_name='會員資料.xlsx'
        )
    except Exception as e:
        return {"error": str(e)}, 500

@member_bp.route("/check/<member_id>", methods=["GET"])
@login_required
def check_member_exists_route(member_id):
    """檢查會員是否存在"""
    try:
        exists = check_member_exists(member_id)
        return jsonify({"exists": exists})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@member_bp.route("/<member_id>", methods=["GET"])
@login_required
def get_member_route(member_id):
    """根據ID獲取會員資料"""
    try:
        member = get_member_by_id(member_id)
        
        if not member:
            return jsonify({"error": "會員不存在"}), 404
            
        return jsonify(member)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@member_bp.route('/next-code', methods=['GET'])
def get_next_code_route():
    """提供下一個可用的會員編號"""
    try:
        result = get_next_member_code()
        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify({"error": result.get("error", "無法獲取編號")}), 500
    except Exception as e:
        print(f"Error in get_next_code_route: {e}")
        return jsonify({"error": "伺服器內部錯誤"}), 500