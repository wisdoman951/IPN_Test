# /app/models/staff_model.py
import pymysql
import os
import numpy as np
from app.config import DB_CONFIG
from datetime import datetime

def get_db_connection():
    """取得資料庫連接"""
    try:
        connection = pymysql.connect(
            **DB_CONFIG,
            cursorclass=pymysql.cursors.DictCursor  # 確保返回字典格式數據
        )
        return connection
    except Exception as e:
        print(f"資料庫連接失敗: {e}")
        return None

def get_all_staff():
    """獲取所有員工"""
    connection = get_db_connection()
    staff_list = []
    
    if connection is None:
        print("無法連接到資料庫，請檢查資料庫配置")
        return staff_list
    
    try:
        with connection.cursor() as cursor:
            print("開始查詢員工數據...")
            
            
            # 根據之前的檢測結果使用正確的表名
            query = f"""
            SELECT s.Staff_ID, s.Staff_Name, s.Staff_Phone, s.Staff_Status,
                   s.Staff_Email, s.Staff_Sex, s.Staff_Store, s.Staff_PermissionLevel
            FROM staff s
            ORDER BY s.Staff_ID DESC
            """
            print(f"執行查詢: {query}")
            cursor.execute(query)
            staff_list = cursor.fetchall()
            print(f"查詢到 {len(staff_list)} 條員工記錄")
            
    except Exception as e:
        print(f"獲取所有員工錯誤: {e}")
        print(f"錯誤類型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    finally:
        if connection:
            connection.close()
    
    return staff_list

def search_staff(keyword):
    """搜尋員工"""
    connection = get_db_connection()
    staff_list = []
    
    try:
        with connection.cursor() as cursor:
            query = """
            SELECT s.Staff_ID, s.Staff_Name, s.Staff_Phone, s.Staff_Status,
                   s.Staff_Email, s.Staff_Sex, s.Staff_Store, s.Staff_PermissionLevel
            FROM Staff s
            WHERE s.Staff_ID LIKE %s
               OR s.Staff_Name LIKE %s
               OR s.Staff_Phone LIKE %s
               OR s.Staff_Email LIKE %s
            ORDER BY s.Staff_ID DESC
            """
            param = f"%{keyword}%"
            cursor.execute(query, (param, param, param, param))
            staff_list = cursor.fetchall()
    except Exception as e:
        print(f"搜尋員工錯誤: {e}")
    finally:
        if connection:
            connection.close()
    
    return staff_list

def get_staff_by_id(staff_id):
    """獲取單個員工資料"""
    connection = get_db_connection()
    staff = None
    
    try:
        with connection.cursor() as cursor:
            query = """
            SELECT s.Staff_ID, s.Staff_Name, s.Staff_Phone, s.Staff_Status,
                   s.Staff_Email, s.Staff_Sex, s.Staff_Store, s.Staff_PermissionLevel
            FROM Staff s
            WHERE s.Staff_ID = %s
            """
            cursor.execute(query, (staff_id,))
            staff = cursor.fetchone()
    except Exception as e:
        print(f"獲取員工錯誤: {e}")
    finally:
        if connection:
            connection.close()
    
    return staff

def get_staff_details(staff_id):
    """獲取員工詳細資料包括家庭成員和工作經驗"""
    connection = get_db_connection()
    result = {
        "basic_info": None,
        "family_members": [],
        "work_experience": []
    }
    
    try:
        with connection.cursor() as cursor:
            # 獲取基本資料
            query = """
            SELECT s.*, 
                   DATE_FORMAT(s.Staff_Birthday, '%Y-%m-%d') as Staff_Birthday,
                   DATE_FORMAT(s.Staff_JoinDate, '%Y-%m-%d') as Staff_JoinDate
            FROM Staff s
            WHERE s.Staff_ID = %s
            """
            cursor.execute(query, (staff_id,))
            result["basic_info"] = cursor.fetchone()
            
            # 獲取家庭成員
            query = """
            SELECT * FROM Staff_Family 
            WHERE Staff_ID = %s
            """
            cursor.execute(query, (staff_id,))
            result["family_members"] = cursor.fetchall()
            
            # 獲取工作經驗
            query = """
            SELECT *, 
                   DATE_FORMAT(Work_StartDate, '%Y-%m-%d') as Work_StartDate,
                   DATE_FORMAT(Work_EndDate, '%Y-%m-%d') as Work_EndDate
            FROM Staff_WorkExperience 
            WHERE Staff_ID = %s
            """
            cursor.execute(query, (staff_id,))
            result["work_experience"] = cursor.fetchall()
    except Exception as e:
        print(f"獲取員工詳細資料錯誤: {e}")
    finally:
        if connection:
            connection.close()
    
    return result

def create_staff(data):
    """新增員工"""
    connection = get_db_connection()
    staff_id = None
    
    try:
        with connection.cursor() as cursor:
            # 1. 新增基本資料
            basic_info = data.get("basic_info", {})
            
            # 處理日期格式
            if "Staff_Birthday" in basic_info and basic_info["Staff_Birthday"]:
                basic_info["Staff_Birthday"] = datetime.strptime(basic_info["Staff_Birthday"], "%Y-%m-%d")
            else:
                basic_info["Staff_Birthday"] = None
                
            if "Staff_JoinDate" in basic_info and basic_info["Staff_JoinDate"]:
                basic_info["Staff_JoinDate"] = datetime.strptime(basic_info["Staff_JoinDate"], "%Y-%m-%d")
            else:
                basic_info["Staff_JoinDate"] = datetime.now()
            
            # 插入基本資料
            query = """
            INSERT INTO Staff (
                Staff_Name, Staff_Phone, Staff_Email, Staff_Sex, 
                Staff_Birthday, Staff_Address, Staff_Store, 
                Staff_PermissionLevel, Staff_Salary, Staff_JoinDate,
                Staff_EmergencyContact, Staff_EmergencyPhone,
                Staff_Note, Staff_Status
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            cursor.execute(query, (
                basic_info.get("Staff_Name"),
                basic_info.get("Staff_Phone"),
                basic_info.get("Staff_Email"),
                basic_info.get("Staff_Sex"),
                basic_info.get("Staff_Birthday"),
                basic_info.get("Staff_Address"),
                basic_info.get("Staff_Store"),
                basic_info.get("Staff_PermissionLevel"),
                basic_info.get("Staff_Salary"),
                basic_info.get("Staff_JoinDate"),
                basic_info.get("Staff_EmergencyContact"),
                basic_info.get("Staff_EmergencyPhone"),
                basic_info.get("Staff_Note"),
                basic_info.get("Staff_Status", "在職")
            ))
            
            # 獲取新增員工的ID
            staff_id = connection.insert_id()
            
            # 2. 新增家庭成員
            family_members = data.get("family_members", [])
            if family_members and len(family_members) > 0:
                for member in family_members:
                    query = """
                    INSERT INTO Staff_Family (
                        Staff_ID, Family_Name, Family_Relation, 
                        Family_Phone, Family_Address
                    ) VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (
                        staff_id,
                        member.get("Family_Name"),
                        member.get("Family_Relation"),
                        member.get("Family_Phone"),
                        member.get("Family_Address")
                    ))
            
            # 3. 新增工作經驗
            work_experience = data.get("work_experience", [])
            if work_experience and len(work_experience) > 0:
                for experience in work_experience:
                    # 處理日期格式
                    start_date = None
                    if "Work_StartDate" in experience and experience["Work_StartDate"]:
                        start_date = datetime.strptime(experience["Work_StartDate"], "%Y-%m-%d")
                    
                    end_date = None
                    if "Work_EndDate" in experience and experience["Work_EndDate"]:
                        end_date = datetime.strptime(experience["Work_EndDate"], "%Y-%m-%d")
                    
                    query = """
                    INSERT INTO Staff_WorkExperience (
                        Staff_ID, Work_Company, Work_Position, 
                        Work_StartDate, Work_EndDate, Work_Description
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (
                        staff_id,
                        experience.get("Work_Company"),
                        experience.get("Work_Position"),
                        start_date,
                        end_date,
                        experience.get("Work_Description")
                    ))
            
            connection.commit()
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"新增員工錯誤: {e}")
        staff_id = None
    finally:
        if connection:
            connection.close()
    
    return staff_id

def update_staff(staff_id, data):
    """更新員工資料"""
    connection = get_db_connection()
    success = False
    
    try:
        with connection.cursor() as cursor:
            # 1. 更新基本資料
            basic_info = data.get("basic_info", {})
            if basic_info:
                # 處理日期格式
                if "Staff_Birthday" in basic_info and basic_info["Staff_Birthday"]:
                    basic_info["Staff_Birthday"] = datetime.strptime(basic_info["Staff_Birthday"], "%Y-%m-%d")
                
                if "Staff_JoinDate" in basic_info and basic_info["Staff_JoinDate"]:
                    basic_info["Staff_JoinDate"] = datetime.strptime(basic_info["Staff_JoinDate"], "%Y-%m-%d")
                
                query = """
                UPDATE Staff SET 
                    Staff_Name = %s,
                    Staff_Phone = %s,
                    Staff_Email = %s,
                    Staff_Sex = %s,
                    Staff_Birthday = %s,
                    Staff_Address = %s,
                    Staff_Store = %s,
                    Staff_PermissionLevel = %s,
                    Staff_Salary = %s,
                    Staff_JoinDate = %s,
                    Staff_EmergencyContact = %s,
                    Staff_EmergencyPhone = %s,
                    Staff_Note = %s,
                    Staff_Status = %s
                WHERE Staff_ID = %s
                """
                cursor.execute(query, (
                    basic_info.get("Staff_Name"),
                    basic_info.get("Staff_Phone"),
                    basic_info.get("Staff_Email"),
                    basic_info.get("Staff_Sex"),
                    basic_info.get("Staff_Birthday"),
                    basic_info.get("Staff_Address"),
                    basic_info.get("Staff_Store"),
                    basic_info.get("Staff_PermissionLevel"),
                    basic_info.get("Staff_Salary"),
                    basic_info.get("Staff_JoinDate"),
                    basic_info.get("Staff_EmergencyContact"),
                    basic_info.get("Staff_EmergencyPhone"),
                    basic_info.get("Staff_Note"),
                    basic_info.get("Staff_Status"),
                    staff_id
                ))
            
            # 2. 更新家庭成員 - 先刪除原有記錄，再新增新記錄
            family_members = data.get("family_members", [])
            cursor.execute("DELETE FROM Staff_Family WHERE Staff_ID = %s", (staff_id,))
            
            if family_members and len(family_members) > 0:
                for member in family_members:
                    query = """
                    INSERT INTO Staff_Family (
                        Staff_ID, Family_Name, Family_Relation, 
                        Family_Phone, Family_Address
                    ) VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (
                        staff_id,
                        member.get("Family_Name"),
                        member.get("Family_Relation"),
                        member.get("Family_Phone"),
                        member.get("Family_Address")
                    ))
            
            # 3. 更新工作經驗 - 先刪除原有記錄，再新增新記錄
            work_experience = data.get("work_experience", [])
            cursor.execute("DELETE FROM Staff_WorkExperience WHERE Staff_ID = %s", (staff_id,))
            
            if work_experience and len(work_experience) > 0:
                for experience in work_experience:
                    # 處理日期格式
                    start_date = None
                    if "Work_StartDate" in experience and experience["Work_StartDate"]:
                        start_date = datetime.strptime(experience["Work_StartDate"], "%Y-%m-%d")
                    
                    end_date = None
                    if "Work_EndDate" in experience and experience["Work_EndDate"]:
                        end_date = datetime.strptime(experience["Work_EndDate"], "%Y-%m-%d")
                    
                    query = """
                    INSERT INTO Staff_WorkExperience (
                        Staff_ID, Work_Company, Work_Position, 
                        Work_StartDate, Work_EndDate, Work_Description
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (
                        staff_id,
                        experience.get("Work_Company"),
                        experience.get("Work_Position"),
                        start_date,
                        end_date,
                        experience.get("Work_Description")
                    ))
            
            connection.commit()
            success = True
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"更新員工錯誤: {e}")
    finally:
        if connection:
            connection.close()
    
    return success

def delete_staff(staff_id):
    """刪除員工"""
    connection = get_db_connection()
    success = False
    
    try:
        with connection.cursor() as cursor:
            # 1. 刪除家庭成員
            cursor.execute("DELETE FROM Staff_Family WHERE Staff_ID = %s", (staff_id,))
            
            # 2. 刪除工作經驗
            cursor.execute("DELETE FROM Staff_WorkExperience WHERE Staff_ID = %s", (staff_id,))
            
            # 3. 刪除基本資料
            cursor.execute("DELETE FROM Staff WHERE Staff_ID = %s", (staff_id,))
            
            connection.commit()
            success = True
    except Exception as e:
        if connection:
            connection.rollback()
        print(f"刪除員工錯誤: {e}")
    finally:
        if connection:
            connection.close()
    
    return success

def get_store_list():
    """獲取所有分店列表"""
    connection = get_db_connection()
    store_list = []
    
    try:
        with connection.cursor() as cursor:
            query = """
            SELECT DISTINCT Staff_Store FROM Staff 
            WHERE Staff_Store IS NOT NULL AND Staff_Store != ''
            """
            cursor.execute(query)
            stores = cursor.fetchall()
            store_list = [store["Staff_Store"] for store in stores]
    except Exception as e:
        print(f"獲取分店列表錯誤: {e}")
    finally:
        if connection:
            connection.close()
    
    return store_list

def get_permission_list():
    """獲取所有權限等級列表"""
    connection = get_db_connection()
    permission_list = []
    
    try:
        with connection.cursor() as cursor:
            query = """
            SELECT DISTINCT Staff_PermissionLevel FROM Staff 
            WHERE Staff_PermissionLevel IS NOT NULL AND Staff_PermissionLevel != ''
            """
            cursor.execute(query)
            permissions = cursor.fetchall()
            permission_list = [permission["Staff_PermissionLevel"] for permission in permissions]
    except Exception as e:
        print(f"獲取權限列表錯誤: {e}")
    finally:
        if connection:
            connection.close()
    
    return permission_list 