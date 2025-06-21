import pymysql
from app.config import DB_CONFIG
from datetime import datetime

def connect_to_db():
    """連接到數據庫"""
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

def get_all_stress_tests(filters=None):
    """獲取所有壓力測試記錄"""
    try:
        conn = connect_to_db()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 構建 SQL 查詢
        query = """
        SELECT s.ipn_stress_id, s.member_id, m.Name, 
               s.a_score, s.b_score, s.c_score, s.d_score,
               (s.a_score + s.b_score + s.c_score + s.d_score) AS total_score
        FROM ipn_stress s
        LEFT JOIN member m ON s.member_id = m.member_id
        WHERE 1=1
        """
        
        # 添加過濾條件
        params = []
        if filters:
            filter_conditions = []

            # 名字過濾
            if 'name' in filters and filters['name']:
                filter_conditions.append("m.Name LIKE %s")
                params.append(f"%{filters['name']}%")

            # 會員ID過濾
            if 'member_id' in filters and filters['member_id']:
                filter_conditions.append("s.member_id = %s")
                params.append(filters['member_id'])

            if filter_conditions:
                query += " AND " + " AND ".join(filter_conditions)
        
        # 添加排序
        query += " ORDER BY s.ipn_stress_id DESC"
        
        cursor.execute(query, params if params else None)
        results = cursor.fetchall()
        
        return results
    except Exception as e:
        print(f"Error in get_all_stress_tests: {e}")
        raise e
    finally:
        if conn:
            conn.close()

def add_stress_test(member_id, scores):
    """添加壓力測試記錄
    
    Args:
        member_id: 會員ID
        scores: 包含a_score, b_score, c_score, d_score的字典
    """
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            # 創建新記錄
            cursor.execute(
                """
                INSERT INTO ipn_stress 
                (member_id, a_score, b_score, c_score, d_score)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    member_id, 
                    scores.get('a_score', 0), 
                    scores.get('b_score', 0), 
                    scores.get('c_score', 0), 
                    scores.get('d_score', 0)
                )
            )
                
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def update_stress_test(stress_id, scores):
    """更新壓力測試記錄
    
    Args:
        stress_id: 壓力測試ID
        scores: 包含a_score, b_score, c_score, d_score的字典
    """
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE ipn_stress 
                SET a_score = %s,
                    b_score = %s,
                    c_score = %s,
                    d_score = %s
                WHERE ipn_stress_id = %s
                """,
                (
                    scores.get('a_score', 0),
                    scores.get('b_score', 0),
                    scores.get('c_score', 0),
                    scores.get('d_score', 0),
                    stress_id
                )
            )
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_stress_test(stress_id):
    """刪除壓力測試記錄"""
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ipn_stress WHERE ipn_stress_id = %s",
                (stress_id,)
            )
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_stress_test_by_id(stress_id):
    """根據ID獲取壓力測試記錄"""
    try:
        conn = connect_to_db()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        query = """
        SELECT s.ipn_stress_id, s.member_id, m.Name, 
               s.a_score, s.b_score, s.c_score, s.d_score,
               (s.a_score + s.b_score + s.c_score + s.d_score) AS total_score
        FROM ipn_stress s
        LEFT JOIN member m ON s.member_id = m.member_id
        WHERE s.ipn_stress_id = %s
        """
        
        cursor.execute(query, (stress_id,))
        result = cursor.fetchone()
        
        return result
    except Exception as e:
        print(f"Error in get_stress_test_by_id: {e}")
        raise e
    finally:
        if conn:
            conn.close()

def get_stress_tests_by_member_id(member_id):
    """獲取特定會員的所有壓力測試記錄"""
    try:
        conn = connect_to_db()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        query = """
        SELECT s.ipn_stress_id, s.member_id, m.Name, 
               s.a_score, s.b_score, s.c_score, s.d_score,
               (s.a_score + s.b_score + s.c_score + s.d_score) AS total_score
        FROM ipn_stress s
        LEFT JOIN member m ON s.member_id = m.member_id
        WHERE s.member_id = %s
        ORDER BY s.ipn_stress_id DESC
        """
        
        cursor.execute(query, (member_id,))
        results = cursor.fetchall()
        
        return results
    except Exception as e:
        print(f"Error in get_stress_tests_by_member_id: {e}")
        raise e
    finally:
        if conn:
            conn.close() 