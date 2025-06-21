from flask import Blueprint, request, jsonify
from app.models.staff_model import (
    get_all_staff,
    search_staff,
    get_staff_by_id,
    create_staff,
    update_staff,
    delete_staff,
    get_store_list,
    get_permission_list,
    get_staff_details
)
from app.middleware import auth_required

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/list", methods=["GET"])
def get_staff_list():
    """獲取所有員工列表"""
    try:
        staff_list = get_all_staff()
        return jsonify(staff_list)
    except Exception as e:
        print(f"獲取員工列表失敗: {e}")
        return jsonify({"error": str(e)}), 500

@staff_bp.route("/search", methods=["GET"])
def search_staff_route():
    """搜尋員工"""
    keyword = request.args.get("keyword", "")
    try:
        staff_list = search_staff(keyword)
        return jsonify(staff_list)
    except Exception as e:
        print(f"搜尋員工失敗: {e}")
        return jsonify({"error": str(e)}), 500

@staff_bp.route("/<int:staff_id>", methods=["GET"])
def get_staff_route(staff_id):
    """獲取單個員工信息"""
    try:
        staff = get_staff_by_id(staff_id)
        if not staff:
            return jsonify({"error": "找不到該員工"}), 404
        return jsonify(staff)
    except Exception as e:
        print(f"獲取員工信息失敗: {e}")
        return jsonify({"error": str(e)}), 500

@staff_bp.route("/details/<int:staff_id>", methods=["GET"])
def get_staff_details_route(staff_id):
    """獲取員工詳細資料"""
    try:
        details = get_staff_details(staff_id)
        if not details:
            return jsonify({"error": "找不到該員工的詳細資料"}), 404
        return jsonify(details)
    except Exception as e:
        print(f"獲取員工詳細資料失敗: {e}")
        return jsonify({"error": str(e)}), 500

@staff_bp.route("/add", methods=["POST"])
@auth_required
def add_staff():
    """新增員工"""
    data = request.json
    try:
        staff_id = create_staff(data)
        if staff_id:
            return jsonify({"message": "員工新增成功", "staff_id": staff_id}), 201
        else:
            return jsonify({"error": "員工新增失敗"}), 400
    except Exception as e:
        print(f"新增員工失敗: {e}")
        return jsonify({"error": str(e)}), 500

@staff_bp.route("/update/<int:staff_id>", methods=["PUT"])
@auth_required
def update_staff_route(staff_id):
    """更新員工信息"""
    data = request.json
    try:
        success = update_staff(staff_id, data)
        if success:
            return jsonify({"message": "員工信息更新成功"}), 200
        else:
            return jsonify({"error": "員工信息更新失敗"}), 400
    except Exception as e:
        print(f"更新員工信息失敗: {e}")
        return jsonify({"error": str(e)}), 500

@staff_bp.route("/delete/<int:staff_id>", methods=["DELETE"])
@auth_required
def delete_staff_route(staff_id):
    """刪除員工"""
    try:
        success = delete_staff(staff_id)
        if success:
            return jsonify({"message": "員工刪除成功"}), 200
        else:
            return jsonify({"error": "員工刪除失敗"}), 400
    except Exception as e:
        print(f"刪除員工失敗: {e}")
        return jsonify({"error": str(e)}), 500

@staff_bp.route("/stores", methods=["GET"])
def get_stores():
    """獲取所有分店"""
    try:
        stores = get_store_list()
        return jsonify(stores)
    except Exception as e:
        print(f"獲取分店列表失敗: {e}")
        return jsonify({"error": str(e)}), 500

@staff_bp.route("/permissions", methods=["GET"])
def get_permissions():
    """獲取所有權限等級"""
    try:
        permissions = get_permission_list()
        return jsonify(permissions)
    except Exception as e:
        print(f"獲取權限列表失敗: {e}")
        return jsonify({"error": str(e)}), 500 