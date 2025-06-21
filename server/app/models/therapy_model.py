import pymysql
from app.config import DB_CONFIG

def connect_to_db():
    """連接到數據庫"""
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

# ==== 療程紀錄功能 ====
def get_remaining_sessions(member_id, therapy_id):
    """計算會員特定療程的剩餘次數
    
    Args:
        member_id: 會員ID
        therapy_id: 療程ID
        
    Returns:
        int: 剩餘次數
    """
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            # 計算購買總量
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) as total_purchased
                FROM therapy_sell
                WHERE member_id = %s AND therapy_id = %s
            """, (member_id, therapy_id))
            total_purchased = cursor.fetchone()['total_purchased']
            
            # 計算已使用量
            cursor.execute("""
                SELECT COUNT(*) as total_used
                FROM therapy_record
                WHERE member_id = %s AND therapy_id = %s
            """, (member_id, therapy_id))
            total_used = cursor.fetchone()['total_used']
            
            return total_purchased - total_used
    finally:
        conn.close()

def get_all_therapy_records():
    """獲取所有療程紀錄，不受店鋪限制
    
    返回:
        列表包含以下欄位:
        - therapy_record_id: 療程ID
        - member_id: 會員ID
        - member_name: 會員姓名
        - store_id: 店鋪ID
        - store_name: 店鋪名稱
        - staff_id: 員工ID
        - staff_name: 員工姓名(服務人員)
        - date: 療程日期
        - note: 備註
        - therapy_id: 療程ID
        - package_name: 療程方案名稱
        - therapy_content: 療程內容
        - remaining_sessions: 剩餘次數
    """
    conn = connect_to_db()
    with conn.cursor() as cursor:
        query = """
            SELECT 
                tr.therapy_record_id, 
                m.member_id, 
                m.name as member_name, 
                s.store_id,
                s.store_name as store_name,
                st.staff_id,
                st.name as staff_name,
                tr.date,
                tr.note,
                tr.therapy_id,
                t.name as package_name,
                t.content as therapy_content
            FROM therapy_record tr
            LEFT JOIN member m ON tr.member_id = m.member_id
            LEFT JOIN store s ON tr.store_id = s.store_id
            LEFT JOIN staff st ON tr.staff_id = st.staff_id
            LEFT JOIN therapy t ON tr.therapy_id = t.therapy_id
            ORDER BY tr.date DESC, tr.therapy_record_id DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()
        
        # 處理日期格式並計算剩餘次數
        for record in result:
            if record.get('date'):
                record['date'] = record['date'].strftime('%Y-%m-%d')
            if record.get('member_id') and record.get('therapy_id'):
                record['remaining_sessions'] = get_remaining_sessions(
                    record['member_id'], 
                    record['therapy_id']
                )
                
    conn.close()
    return result

def get_therapy_records_by_store(store_id):
    """獲取特定店鋪的療程紀錄"""
    conn = connect_to_db()
    with conn.cursor() as cursor:
        query = """
            SELECT 
                tr.therapy_record_id, 
                m.member_id, 
                m.name as member_name, 
                s.store_id,
                s.store_name as store_name,
                st.staff_id,
                st.name as staff_name,
                tr.date,
                tr.note,
                tr.therapy_id,
                t.name as package_name,
                t.content as therapy_content
            FROM therapy_record tr
            LEFT JOIN member m ON tr.member_id = m.member_id
            LEFT JOIN store s ON tr.store_id = s.store_id
            LEFT JOIN staff st ON tr.staff_id = st.staff_id
            LEFT JOIN therapy t ON tr.therapy_id = t.therapy_id
            WHERE tr.store_id = %s
            ORDER BY tr.date DESC, tr.therapy_record_id DESC
        """
        cursor.execute(query, (store_id,))
        result = cursor.fetchall()
        
        # 處理日期格式並計算剩餘次數
        for record in result:
            if record.get('date'):
                record['date'] = record['date'].strftime('%Y-%m-%d')
            if record.get('member_id') and record.get('therapy_id'):
                record['remaining_sessions'] = get_remaining_sessions(
                    record['member_id'], 
                    record['therapy_id']
                )
                
    conn.close()
    return result

def search_therapy_records(keyword, store_id=None):
    """搜尋療程紀錄"""
    conn = connect_to_db()
    with conn.cursor() as cursor:
        like = f"%{keyword}%"
        
        if store_id:
            # 如果提供store_id，僅搜尋該store的記錄
            query = """
                SELECT 
                    tr.therapy_record_id, 
                    m.member_id, 
                    m.name as member_name, 
                    s.store_id,
                    s.store_name as store_name,
                    st.staff_id,
                    st.name as staff_name,
                    tr.date,
                    tr.note,
                    tr.therapy_id,
                    t.name as package_name,
                    t.content as therapy_content
                FROM therapy_record tr
                LEFT JOIN member m ON tr.member_id = m.member_id
                LEFT JOIN store s ON tr.store_id = s.store_id
                LEFT JOIN staff st ON tr.staff_id = st.staff_id
                LEFT JOIN therapy t ON tr.therapy_id = t.therapy_id
                WHERE tr.store_id = %s 
                AND (m.name LIKE %s OR CAST(m.member_id AS CHAR) LIKE %s OR st.name LIKE %s OR tr.note LIKE %s)
                ORDER BY tr.date DESC, tr.therapy_record_id DESC
            """
            cursor.execute(query, (store_id, like, like, like, like))
        else:
            # 如果沒有提供store_id，搜尋所有記錄
            query = """
                SELECT 
                    tr.therapy_record_id, 
                    m.member_id, 
                    m.name as member_name, 
                    s.store_id,
                    s.store_name as store_name,
                    st.staff_id,
                    st.name as staff_name,
                    tr.date,
                    tr.note,
                    tr.therapy_id,
                    t.name as package_name,
                    t.content as therapy_content
                FROM therapy_record tr
                LEFT JOIN member m ON tr.member_id = m.member_id
                LEFT JOIN store s ON tr.store_id = s.store_id
                LEFT JOIN staff st ON tr.staff_id = st.staff_id
                LEFT JOIN therapy t ON tr.therapy_id = t.therapy_id
                WHERE m.name LIKE %s OR CAST(m.member_id AS CHAR) LIKE %s OR st.name LIKE %s OR tr.note LIKE %s
                ORDER BY tr.date DESC, tr.therapy_record_id DESC
            """
            cursor.execute(query, (like, like, like, like))
            
        result = cursor.fetchall()
        
        # 處理日期格式並計算剩餘次數
        for record in result:
            if record.get('date'):
                record['date'] = record['date'].strftime('%Y-%m-%d')
            if record.get('member_id') and record.get('therapy_id'):
                record['remaining_sessions'] = get_remaining_sessions(
                    record['member_id'], 
                    record['therapy_id']
                )
                
    conn.close()
    return result

def get_therapy_record_by_id(record_id):
    """獲取單一療程紀錄"""
    conn = connect_to_db()
    with conn.cursor() as cursor:
        query = """
            SELECT 
                tr.therapy_record_id, 
                m.member_id, 
                m.name as member_name, 
                s.store_id,
                s.store_name as store_name,
                st.staff_id,
                st.name as staff_name,
                tr.date,
                tr.note,
                tr.therapy_id,
                t.name as package_name,
                t.content as therapy_content
            FROM therapy_record tr
            LEFT JOIN member m ON tr.member_id = m.member_id
            LEFT JOIN store s ON tr.store_id = s.store_id
            LEFT JOIN staff st ON tr.staff_id = st.staff_id
            LEFT JOIN therapy t ON tr.therapy_id = t.therapy_id
            WHERE tr.therapy_record_id = %s
        """
        cursor.execute(query, (record_id,))
        result = cursor.fetchone()
        
        # 處理日期格式並計算剩餘次數
        if result:
            if result.get('date'):
                result['date'] = result['date'].strftime('%Y-%m-%d')
            if result.get('member_id') and result.get('therapy_id'):
                result['remaining_sessions'] = get_remaining_sessions(
                    result['member_id'], 
                    result['therapy_id']
                )
            
    conn.close()
    return result

def insert_therapy_record(data):
    """新增療程紀錄"""
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            query = """
                INSERT INTO therapy_record (
                    member_id, store_id, staff_id, date, note
                ) VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                data.get("member_id"),
                data.get("store_id"),
                data.get("staff_id"),
                data.get("date"),
                data.get("note")
            )
            cursor.execute(query, values)
            
            # 獲取新增記錄的ID
            record_id = conn.insert_id()
            
        conn.commit()
        return record_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def update_therapy_record(record_id, data):
    """更新療程紀錄"""
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            query = """
                UPDATE therapy_record
                SET member_id = %s, 
                    store_id = %s, 
                    staff_id = %s, 
                    date = %s, 
                    note = %s
                WHERE therapy_record_id = %s
            """
            values = (
                data.get("member_id"),
                data.get("store_id"),
                data.get("staff_id"),
                data.get("date"),
                data.get("note"),
                record_id
            )
            cursor.execute(query, values)
            
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_therapy_record(record_id):
    """刪除療程紀錄"""
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            query = "DELETE FROM therapy_record WHERE therapy_record_id = %s"
            cursor.execute(query, (record_id,))
            
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def export_therapy_records(store_id=None):
    """匯出療程紀錄（可選擇性根據商店ID過濾）"""
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            if store_id:
                query = """
                    SELECT tr.therapy_record_id, 
                           m.member_id, 
                           m.name as member_name, 
                           s.name as store_name,
                           st.name as staff_name,
                           tr.date,
                           tr.note
                    FROM therapy_record tr
                    LEFT JOIN member m ON tr.member_id = m.member_id
                    LEFT JOIN store s ON tr.store_id = s.store_id
                    LEFT JOIN staff st ON tr.staff_id = st.staff_id
                    WHERE tr.store_id = %s
                    ORDER BY tr.date DESC, tr.therapy_record_id DESC
                """
                cursor.execute(query, (store_id,))
            else:
                query = """
                    SELECT tr.therapy_record_id, 
                           m.member_id, 
                           m.name as member_name, 
                           s.name as store_name,
                           st.name as staff_name,
                           tr.date,
                           tr.note
                    FROM therapy_record tr
                    LEFT JOIN member m ON tr.member_id = m.member_id
                    LEFT JOIN store s ON tr.store_id = s.store_id
                    LEFT JOIN staff st ON tr.staff_id = st.staff_id
                    ORDER BY tr.date DESC, tr.therapy_record_id DESC
                """
                cursor.execute(query)
                
            result = cursor.fetchall()
            
            # 處理日期格式
            for record in result:
                if record.get('日期'):
                    record['日期'] = record['日期'].strftime('%Y-%m-%d')
                    
        return result
    except Exception as e:
        raise e
    finally:
        conn.close()

# ==== 療程銷售功能 ====
def get_all_therapy_sells():
    """獲取所有療程銷售"""
    conn = connect_to_db()
    with conn.cursor() as cursor:
        query = """
            SELECT ts.Order_ID, m.Member_ID, m.Name as MemberName, ts.PurchaseDate, 
                   tp.TherapyContent as PackageName, ts.Sessions, 
                   ts.PaymentMethod, s.Name as StaffName, ts.SaleCategory,
                   ts.Staff_ID, ts.TherapyCode
            FROM therapySell ts
            LEFT JOIN member m ON ts.Member_ID = m.Member_ID
            LEFT JOIN staff s ON ts.Staff_ID = s.Staff_ID
            LEFT JOIN therapypackage tp ON ts.TherapyCode = tp.TherapyCode
            ORDER BY ts.PurchaseDate DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()
    conn.close()
    return result

def search_therapy_sells(keyword):
    """搜尋療程銷售"""
    conn = connect_to_db()
    with conn.cursor() as cursor:
        query = """
            SELECT ts.Order_ID, m.Member_ID, m.Name as MemberName, ts.PurchaseDate, 
                   tp.TherapyContent as PackageName, ts.Sessions, 
                   ts.PaymentMethod, s.Name as StaffName, ts.SaleCategory,
                   ts.Staff_ID, ts.TherapyCode
            FROM therapySell ts
            LEFT JOIN member m ON ts.Member_ID = m.Member_ID
            LEFT JOIN staff s ON ts.Staff_ID = s.Staff_ID
            LEFT JOIN therapypackage tp ON ts.TherapyCode = tp.TherapyCode
            WHERE m.Name LIKE %s OR m.Member_ID LIKE %s OR s.Name LIKE %s
            ORDER BY ts.PurchaseDate DESC
        """
        like = f"%{keyword}%"
        cursor.execute(query, (like, like, like))
        result = cursor.fetchall()
    conn.close()
    return result

def insert_therapy_sell(data, test_mode=False):
    """新增療程銷售"""
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            if test_mode:
                # 暫時禁用外鍵檢查（僅用於測試）
                cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            
            query = """
                INSERT INTO therapySell (
                    Member_ID, PurchaseDate, TherapyCode, Sessions,
                    PaymentMethod, TransferCode, CardNumber, Staff_ID, SaleCategory
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                data.get("memberId"),
                data.get("purchaseDate"),
                data.get("therapyPackageId"),
                data.get("sessions"),
                data.get("paymentMethod"),
                data.get("transferCode"),
                data.get("cardNumber"),
                data.get("staffId"),
                data.get("saleCategory")
            )
            cursor.execute(query, values)
            
            if test_mode:
                # 重新啟用外鍵檢查
                cursor.execute("SET FOREIGN_KEY_CHECKS=1")
                
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def update_therapy_sell(sale_id, data):
    """更新療程銷售"""
    conn = connect_to_db()
    with conn.cursor() as cursor:
        query = """
            UPDATE therapySell
            SET Member_ID = %s, PurchaseDate = %s, TherapyCode = %s,
                Sessions = %s, PaymentMethod = %s, TransferCode = %s,
                CardNumber = %s, Staff_ID = %s, SaleCategory = %s
            WHERE Order_ID = %s
        """
        values = (
            data.get("memberId"),
            data.get("purchaseDate"),
            data.get("therapyPackageId"),
            data.get("sessions"),
            data.get("paymentMethod"),
            data.get("transferCode"),
            data.get("cardNumber"),
            data.get("staffId"),
            data.get("saleCategory"),
            sale_id
        )
        cursor.execute(query, values)
    conn.commit()
    conn.close()

def delete_therapy_sell(sale_id):
    """刪除療程銷售"""
    conn = connect_to_db()
    with conn.cursor() as cursor:
        query = "DELETE FROM therapySell WHERE Order_ID = %s"
        cursor.execute(query, (sale_id,))
    conn.commit()
    conn.close()
