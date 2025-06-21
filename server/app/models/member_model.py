import pymysql
from app.config import DB_CONFIG
import re

def connect_to_db():
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

def get_all_members():
    conn = connect_to_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT member_id, name, birthday, address, phone, gender, blood_type,
                   line_id, inferrer_id, occupation, note
            FROM member
        """)
        result = cursor.fetchall()
    conn.close()
    return result

def search_members(keyword):
    conn = connect_to_db()
    with conn.cursor() as cursor:
        like = f"%{keyword}%"
        cursor.execute("""
            SELECT member_id, name, birthday, address, phone, gender, blood_type,
                   line_id, inferrer_id, occupation, note
            FROM member
            WHERE name LIKE %s OR phone LIKE %s OR member_id LIKE %s
        """, (like, like, like))
        result = cursor.fetchall()
    conn.close()
    return result

def create_member(data):
    conn = connect_to_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO member (
                name, birthday, address, phone, gender,
                blood_type, line_id, inferrer_id, occupation, note
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("name"),
            data.get("birthday"),
            data.get("address"),
            data.get("phone"),
            data.get("gender"),
            data.get("blood_type"),
            data.get("line_id"),
            data.get("inferrer_id"),
            data.get("occupation"),
            data.get("note")
        ))
    conn.commit()
    conn.close()

def delete_member_and_related_data(member_id: int):
    """
    刪除一個會員及其所有相關的紀錄。
    此操作會在一個資料庫事務中完成。
    """
    conn = None
    # 根據您的資料庫 schema，列出所有直接或間接關聯到 member_id 的表
    # 刪除順序應從最外層的子表開始，最後才是 member 表
    tables_with_member_id = [
        "product_sell",                 # 依賴 member
        "therapy_sell",                 # 依賴 member
        "therapy_record",               # 依賴 member
        "ipn_pure",                     # 依賴 member
        "ipn_stress",                   # 依賴 member
        "medical_record",               # 依賴 member 和 usual_sympton_and_family_history
        "usual_sympton_and_family_history" # 依賴 member
        # 注意：sales_orders 也關聯了 member，如果需要也應加入
        # "sales_order_items", # 如果它直接關聯 member
        # "sales_orders",
    ]

    try:
        conn = connect_to_db()
        conn.begin() # 開始事務

        with conn.cursor() as cursor:
            # 為了避免外鍵問題，我們可以先刪除最高層級的關聯記錄
            # 例如 medical_record 關聯了 usual_sympton_and_family_history
            # 我們應該先刪除 medical_record，再刪除 usual_sympton_and_family_history
            
            # 1. 刪除 medical_record
            cursor.execute("DELETE FROM medical_record WHERE member_id = %s", (member_id,))
            print(f"Deleted from medical_record for member_id: {member_id}")

            # 2. 刪除其他直接關聯的表
            for table in tables_with_member_id:
                # medical_record 已經處理過，跳過
                if table == 'medical_record':
                    continue
                
                # 檢查表是否存在 (可選，但更健壯)
                # cursor.execute("SHOW TABLES LIKE %s", (table,))
                # if cursor.fetchone():
                
                # 檢查表中是否有 member_id 欄位 (可選)
                # cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE 'member_id'")
                # if cursor.fetchone():

                print(f"Deleting from {table} for member_id: {member_id}")
                cursor.execute(f"DELETE FROM `{table}` WHERE member_id = %s", (member_id,))
            
            # 3. 最後，刪除 member 主表中的記錄
            print(f"Deleting from member table for member_id: {member_id}")
            deleted_count = cursor.execute("DELETE FROM member WHERE member_id = %s", (member_id,))

            if deleted_count == 0:
                raise ValueError(f"會員 ID {member_id} 不存在，無法刪除。")

        conn.commit() # 所有刪除操作成功，提交事務
        return {"success": True, "message": f"會員 {member_id} 及其所有相關紀錄已成功刪除。"}
        
    except Exception as e:
        if conn:
            conn.rollback() # 如果任何一步出錯，回滾所有操作
        print(f"--- ERROR Deleting Member {member_id} ---")
        traceback.print_exc()
        return {"success": False, "error": f"刪除會員時發生錯誤: {str(e)}"}
    finally:
        if conn:
            conn.close()

def update_member(member_id, data):
    conn = connect_to_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE member SET
                name=%s, birthday=%s, address=%s, phone=%s, gender=%s,
                blood_type=%s, line_id=%s, inferrer_id=%s, occupation=%s, note=%s
            WHERE member_id = %s
        """, (
            data.get("name"),
            data.get("birthday"),
            data.get("address"),
            data.get("phone"),
            data.get("gender"),
            data.get("blood_type"),
            data.get("line_id"),
            data.get("inferrer_id"),
            data.get("occupation"),
            data.get("note"),
            member_id
        ))
    conn.commit()
    conn.close()

def get_member_by_id(member_id):
    conn = connect_to_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT member_id, name, birthday, address, phone, gender, blood_type,
                   line_id, inferrer_id, occupation, note
            FROM member
            WHERE member_id = %s
        """, (member_id,))
        result = cursor.fetchone()
    conn.close()
    return result

def check_member_exists(member_id):
    conn = connect_to_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM member WHERE member_id = %s", (member_id,))
        result = cursor.fetchone()
    conn.close()
    return result["count"] > 0

def get_next_member_code():
    """查詢資料庫並計算下一個會員編號"""
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            # 查詢最後一筆資料的 member_code
            # ORDER BY member_id DESC 確保拿到的是最新加入的會員
            query = "SELECT member_code FROM member ORDER BY member_id DESC LIMIT 1"
            cursor.execute(query)
            last_member = cursor.fetchone()

            if last_member and last_member.get('member_code'):
                last_code = last_member['member_code']
                # 使用正規表達式提取字首和數字部分
                match = re.match(r'([A-Za-z]*)(\d+)', last_code)
                if match:
                    prefix = match.group(1) # 例如 "M"
                    number_part = match.group(2) # 例如 "010"
                    next_number = int(number_part) + 1
                    # 保持原始的數字寬度（補零）
                    new_code = f"{prefix}{str(next_number).zfill(len(number_part))}"
                else:
                    # 如果格式不符，提供一個預設的 fallback
                    new_code = "M001"
            else:
                # 如果資料庫中沒有任何會員
                new_code = "M001"
            
            return {"success": True, "next_code": new_code}
    except Exception as e:
        print(f"Error getting next member code: {e}")
        return {"success": False, "error": str(e)}
    finally:
        if conn:
            conn.close()

