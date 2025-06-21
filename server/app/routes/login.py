from flask import Blueprint, request, jsonify, make_response
from app.models.login_model import find_store_by_account, update_store_password, get_all_stores
import secrets
import time
import jwt
from datetime import datetime, timedelta
from app.config import JWT_SECRET_KEY, JWT_EXPIRATION

login_bp = Blueprint("auth", __name__)

# 儲存重置密碼的 token
password_reset_tokens = {}  # { token: { account, expiry } }

# 為所有其他響應添加適當的 CORS 頭
@login_bp.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers.set('Access-Control-Allow-Origin', origin)
    else:
        response.headers.set('Access-Control-Allow-Origin', '*')
    
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Store-ID, X-Store-Level, Accept, Origin')
    response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.set('Access-Control-Max-Age', '600')
    response.headers.set('Access-Control-Allow-Credentials', 'true')
    return response

@login_bp.route("", methods=["POST", "OPTIONS"])
def login():
    # 處理 OPTIONS 請求
    if request.method == "OPTIONS":
        print("處理 OPTIONS 請求")
        response = make_response()
        # 添加 CORS 標頭
        origin = request.headers.get('Origin')
        if origin:
            response.headers.set('Access-Control-Allow-Origin', origin)
        else:
            response.headers.set('Access-Control-Allow-Origin', '*')
        
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Store-ID, X-Store-Level, Accept, Origin')
        response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.set('Access-Control-Max-Age', '600')
        response.headers.set('Access-Control-Allow-Credentials', 'true')
        # 設置正確的 OPTIONS 響應狀態碼和 Content-Type
        response.headers.set('Content-Type', 'text/plain')
        return response, 200
    
    # 處理 POST 請求
    print("接收到登錄請求:", request.json)
    try:
        data = request.json
        if not data:
            return jsonify({"error": "無效的請求格式"}), 400
            
        account = data.get("account")
        password = data.get("password")

        if not account or not password:
            return jsonify({"error": "請輸入帳號與密碼"}), 400

        store = find_store_by_account(account)
        if not store:
            return jsonify({"error": "查無此帳號"}), 404

        if store["password"] != password:
            return jsonify({"error": "密碼錯誤"}), 401

        # 判斷商店級別
        store_level = "總店" if store["permission"] == "admin" else "分店"

        # 生成JWT令牌
        payload = {
            'store_id': store["store_id"],
            'store_level': store_level,
            'store_name': store["store_name"],
            'permission': store["permission"],
            'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION)  # 使用配置中的過期時間
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

        # 創建響應
        response_data = {
            "message": "登入成功",
            "token": token,
            "store_id": store["store_id"],
            "store_level": store_level,
            "store_name": store["store_name"],
            "permission": store["permission"],
            "account": account 
        }
        
        print("返回登錄成功響應:", response_data)
        response = jsonify(response_data)
        
        # 添加 CORS 標頭
        origin = request.headers.get('Origin')
        if origin:
            response.headers.set('Access-Control-Allow-Origin', origin)
        else:
            response.headers.set('Access-Control-Allow-Origin', '*')
        
        return response, 200
    except Exception as e:
        print("登入處理異常:", str(e))
        return jsonify({"error": f"處理請求失敗: {str(e)}"}), 500

@login_bp.route("/request-password-reset", methods=["POST"])
def request_password_reset():
    """請求重設密碼（管理員功能）"""
    data = request.json
    account = data.get("account")

    if not account:
        return jsonify({"error": "請輸入帳號"}), 400

    store = find_store_by_account(account)
    if not store:
        return jsonify({"error": "查無此帳號"}), 404

    # 產生重設 token，有效期為 1 小時
    token = secrets.token_urlsafe(32)
    expiry = int(time.time()) + 3600  # 一小時後過期
    
    password_reset_tokens[token] = {
        "account": account,
        "expiry": expiry
    }

    # 在實際應用中，這裡應該發送郵件通知管理員或相關人員
    # 為了測試，我們這裡直接返回 token
    return jsonify({
        "message": "重設密碼連結已產生",
        "token": token,
        "expires_in": "1小時"
    }), 200

@login_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """處理忘記密碼請求"""
    data = request.json
    account = data.get("account")

    if not account:
        return jsonify({"error": "請輸入帳號"}), 400

    store = find_store_by_account(account)
    if not store:
        return jsonify({"error": "查無此帳號"}), 404

    # 產生重設 token，有效期為 1 小時
    token = secrets.token_urlsafe(32)
    expiry = int(time.time()) + 3600  # 一小時後過期
    
    password_reset_tokens[token] = {
        "account": account,
        "expiry": expiry
    }

    # 在實際應用中，這裡應該發送郵件通知使用者
    # 為了測試，我們這裡直接返回 token
    return jsonify({
        "message": "重設密碼連結已產生",
        "token": token,
        "expires_in": "1小時"
    }), 200

@login_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """重設密碼"""
    data = request.json
    token = data.get("token")
    account = data.get("account")
    new_password = data.get("newPassword")

    if not token or not new_password or not account:
        return jsonify({"error": "缺少必要參數"}), 400

    token_data = password_reset_tokens.get(token)
    if not token_data:
        return jsonify({"error": "無效的重設連結"}), 400

    # 檢查 token 是否過期
    current_time = int(time.time())
    if current_time > token_data["expiry"]:
        # 移除過期的 token
        password_reset_tokens.pop(token, None)
        return jsonify({"error": "重設連結已過期"}), 400

    # 確認 token 對應的帳號是否正確
    if token_data["account"] != account:
        return jsonify({"error": "帳號與重設連結不匹配"}), 400

    store = find_store_by_account(account)
    if not store:
        return jsonify({"error": "帳號已不存在"}), 404

    # 更新密碼
    try:
        update_store_password(account, new_password)
        
        # 密碼更新成功，移除 token
        password_reset_tokens.pop(token, None)
        
        return jsonify({
            "message": "密碼更新成功",
        }), 200
    except Exception as e:
        return jsonify({"error": f"密碼更新失敗: {str(e)}"}), 500

@login_bp.route("/refresh-token", methods=["POST"])
def refresh_token():
    """刷新 JWT 令牌"""
    # 獲取認證頭信息
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "未提供有效的令牌"}), 401
    
    old_token = auth_header.split(' ')[1]
    
    try:
        # 驗證舊令牌
        payload = jwt.decode(old_token, JWT_SECRET_KEY, algorithms=['HS256'])
        
        # 生成新令牌（更新過期時間）
        new_payload = {
            'store_id': payload['store_id'],
            'store_level': payload['store_level'],
            'store_name': payload['store_name'],
            'permission': payload['permission'],
            'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION)  # 使用配置中的過期時間
        }
        
        new_token = jwt.encode(new_payload, JWT_SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            "message": "令牌刷新成功",
            "token": new_token,
            "store_id": payload['store_id'],
            "store_level": payload['store_level'],
            "store_name": payload['store_name'],
            "permission": payload['permission']
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "令牌已過期，請重新登入"}), 401
    except (jwt.InvalidTokenError, Exception) as e:
        return jsonify({"error": f"無效的令牌: {str(e)}"}), 401

@login_bp.route("/stores", methods=["GET"])
def get_stores():
    """獲取所有商店信息"""
    try:
        stores = get_all_stores()
        return jsonify(stores), 200
    except Exception as e:
        return jsonify({"error": f"獲取商店信息失敗: {str(e)}"}), 500

@login_bp.route("/check", methods=["GET"])
def check_auth():
    """檢查認證狀態"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"authenticated": False, "error": "未提供有效的令牌"}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        # 驗證令牌
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        
        return jsonify({
            "authenticated": True,
            "store_id": payload['store_id'],
            "store_level": payload['store_level'],
            "store_name": payload['store_name'],
            "permission": payload['permission'] 
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({"authenticated": False, "error": "令牌已過期，請重新登入"}), 401
    except (jwt.InvalidTokenError, Exception) as e:
        return jsonify({"authenticated": False, "error": f"無效的令牌: {str(e)}"}), 401
