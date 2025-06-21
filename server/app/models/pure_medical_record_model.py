import pymysql
from app.config import DB_CONFIG
from datetime import datetime

def connect_to_db():
    """連接到數據庫"""
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

def get_all_pure_records(filters=None):
    """獲取所有淨化健康紀錄
    
    Args:
        filters: 可選的過濾條件，例如 {'name': '張三', 'pure_item': '洗腎', 'staff_name': '李四'}
    
    Returns:
        淨化健康紀錄列表
    """
    try:
        conn = connect_to_db()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 構建 SQL 查詢
        query = """
        SELECT p.ipn_pure_id, p.member_id, m.Name, p.staff_id, s.name as staff_name,
               p.visceral_fat, p.blood_preasure, p.basal_metabolic_rate, 
               p.date, p.body_age, p.height, p.weight, p.bmi, p.pure_item, p.note
        FROM ipn_pure p
        LEFT JOIN member m ON p.member_id = m.member_id
        LEFT JOIN staff s ON p.staff_id = s.staff_id
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

            # 淨化項目過濾
            if 'pure_item' in filters and filters['pure_item']:
                filter_conditions.append("p.pure_item LIKE %s")
                params.append(f"%{filters['pure_item']}%")
                
            # 服務人員過濾
            if 'staff_name' in filters and filters['staff_name']:
                filter_conditions.append("s.name LIKE %s")
                params.append(f"%{filters['staff_name']}%")

            if filter_conditions:
                query += " AND " + " AND ".join(filter_conditions)
        
        # 添加排序，依日期和ID降序排列（最新記錄優先）
        query += " ORDER BY p.date DESC, p.ipn_pure_id DESC"
        
        cursor.execute(query, params if params else None)
        results = cursor.fetchall()
        
        # 格式化日期以返回給前端
        for record in results:
            if record.get('date'):
                record['date'] = record['date'].strftime('%Y-%m-%d')
        
        return results
    except Exception as e:
        print(f"Error in get_all_pure_records: {e}")
        raise e
    finally:
        if conn:
            conn.close()

def add_pure_record(data):
    """添加淨化健康紀錄
    
    Args:
        data: 包含淨化健康紀錄資料的字典
              必須包含 member_id
              可選包含 staff_id, visceral_fat, blood_preasure, basal_metabolic_rate, 
                       date, body_age, weight, bmi, pure_item, note
    
    Returns:
        新記錄的ID
    """
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            # 設置默認日期為當前日期（若未提供）
            if 'date' not in data or not data['date']:
                data['date'] = datetime.now().strftime('%Y-%m-%d')
                
            # 創建新記錄
            cursor.execute(
                """
                INSERT INTO ipn_pure 
                (member_id, staff_id, visceral_fat, blood_preasure, basal_metabolic_rate,
                 date, body_age, height, weight, bmi, pure_item, note)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data.get('member_id'),
                    data.get('staff_id'),
                    data.get('visceral_fat'),
                    data.get('blood_preasure'),
                    data.get('basal_metabolic_rate'),
                    data.get('date'),
                    data.get('body_age'),
                    data.get('height'),
                    data.get('weight'),
                    data.get('bmi'),
                    data.get('pure_item'),
                    data.get('note')
                )
            )
                
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def update_pure_record(pure_id, data):
    """更新淨化健康紀錄
    
    Args:
        pure_id: 淨化健康紀錄ID
        data: 包含更新資料的字典
              可選包含 member_id, staff_id, visceral_fat, blood_preasure, basal_metabolic_rate, 
                       date, body_age, weight, bmi, pure_item, note
    
    Returns:
        成功返回True
    """
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE ipn_pure 
                SET member_id = %s,
                    staff_id = %s,
                    visceral_fat = %s,
                    blood_preasure = %s,
                    basal_metabolic_rate = %s,
                    date = %s,
                    body_age = %s,
                    height = %s,
                    weight = %s,
                    bmi = %s,
                    pure_item = %s,
                    note = %s
                WHERE ipn_pure_id = %s
                """,
                (
                    data.get('member_id'),
                    data.get('staff_id'),
                    data.get('visceral_fat'),
                    data.get('blood_preasure'),
                    data.get('basal_metabolic_rate'),
                    data.get('date'),
                    data.get('body_age'),
                    data.get('height'),
                    data.get('weight'),
                    data.get('bmi'),
                    data.get('pure_item'),
                    data.get('note'),
                    pure_id
                )
            )
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_pure_record(pure_id):
    """刪除淨化健康紀錄
    
    Args:
        pure_id: 淨化健康紀錄ID
        
    Returns:
        成功返回True
    """
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM ipn_pure WHERE ipn_pure_id = %s",
                (pure_id,)
            )
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_pure_record_by_id(pure_id):
    """根據ID獲取淨化健康紀錄
    
    Args:
        pure_id: 淨化健康紀錄ID
        
    Returns:
        淨化健康紀錄詳情
    """
    try:
        conn = connect_to_db()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        query = """
        SELECT p.ipn_pure_id, p.member_id, m.Name, p.staff_id, s.name as staff_name,
               p.visceral_fat, p.blood_preasure, p.basal_metabolic_rate, 
               p.date, p.body_age, p.height, p.weight, p.bmi, p.pure_item, p.note
        FROM ipn_pure p
        LEFT JOIN member m ON p.member_id = m.member_id
        LEFT JOIN staff s ON p.staff_id = s.staff_id
        WHERE p.ipn_pure_id = %s
        """
        
        cursor.execute(query, (pure_id,))
        result = cursor.fetchone()
        
        # 格式化日期
        if result and result.get('date'):
            result['date'] = result['date'].strftime('%Y-%m-%d')
            
        return result
    except Exception as e:
        print(f"Error in get_pure_record_by_id: {e}")
        raise e
    finally:
        if conn:
            conn.close()

def get_pure_records_by_member_id(member_id):
    """獲取特定會員的所有淨化健康紀錄
    
    Args:
        member_id: 會員ID
        
    Returns:
        該會員的淨化健康紀錄列表
    """
    try:
        conn = connect_to_db()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        query = """
        SELECT p.ipn_pure_id, p.member_id, m.Name, p.staff_id, s.name as staff_name,
               p.visceral_fat, p.blood_preasure, p.basal_metabolic_rate, 
               p.date, p.body_age, p.height, p.weight, p.bmi, p.pure_item, p.note
        FROM ipn_pure p
        LEFT JOIN member m ON p.member_id = m.member_id
        LEFT JOIN staff s ON p.staff_id = s.staff_id
        WHERE p.member_id = %s
        ORDER BY p.date DESC, p.ipn_pure_id DESC
        """
        
        cursor.execute(query, (member_id,))
        results = cursor.fetchall()
        
        # 格式化日期
        for record in results:
            if record.get('date'):
                record['date'] = record['date'].strftime('%Y-%m-%d')
        
        return results
    except Exception as e:
        print(f"Error in get_pure_records_by_member_id: {e}")
        raise e
    finally:
        if conn:
            conn.close()

def export_pure_records():
    """導出淨化健康紀錄以供Excel下載
    
    Returns:
        適合Excel導出的記錄列表
    """
    try:
        conn = connect_to_db()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        query = """
        SELECT p.ipn_pure_id as '編號', 
               m.Name as '姓名', 
               s.name as '服務人員',
               p.blood_preasure as '血壓', 
               p.date as '日期', 
               p.height as '身高',
               p.weight as '體重', 
               p.visceral_fat as '內脂肪', 
               p.basal_metabolic_rate as '基礎代謝', 
               p.body_age as '體年齡', 
               p.bmi as 'BMI', 
               p.pure_item as '淨化項目',
               p.note as '備註'
        FROM ipn_pure p
        LEFT JOIN member m ON p.member_id = m.member_id
        LEFT JOIN staff s ON p.staff_id = s.staff_id
        ORDER BY p.date DESC, p.ipn_pure_id DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # 格式化日期
        for record in results:
            if record.get('日期'):
                record['日期'] = record['日期'].strftime('%Y-%m-%d')
        
        return results
    except Exception as e:
        print(f"Error in export_pure_records: {e}")
        raise e
    finally:
        if conn:
            conn.close() 