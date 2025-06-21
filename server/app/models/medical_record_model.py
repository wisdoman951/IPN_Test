import pymysql
import json
from app.config import DB_CONFIG

def connect_to_db():
    return pymysql.connect(**DB_CONFIG)

def get_all_medical_records():
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT 
                mr.medical_record_id, mr.member_id, m.name, mr.height, mr.weight,
                us.HPA_selection, us.meridian_selection, us.neck_and_shoulder_selection, 
                us.anus_selection, us.family_history_selection, us.others,
                CASE WHEN mr.micro_surgery IS NOT NULL THEN 1 ELSE 0 END as micro_surgery, 
                ms.micro_surgery_description
            FROM medical_record mr
            LEFT JOIN member m ON mr.member_id = m.member_id
            LEFT JOIN usual_sympton_and_family_history us ON mr.usual_sympton_and_family_history_id = us.usual_sympton_and_family_history_id
            LEFT JOIN micro_surgery ms ON mr.micro_surgery = ms.micro_surgery_id
            ORDER BY mr.medical_record_id DESC
            """
            cursor.execute(sql)
            records = cursor.fetchall()
            
            # 重新格式化資料以符合前端期望
            formatted_records = []
            for record in records:
                # 組合病史為 JSON 格式
                medical_history = {}
                
                # 解析存儲的JSON資料
                if record[5]:  # HPA_selection
                    try:
                        hpa_list = json.loads(record[5]) if record[5] else []
                        if hpa_list:
                            medical_history["HPA"] = hpa_list
                    except:
                        medical_history["HPA"] = []
                        
                if record[6]:  # meridian_selection
                    try:
                        meridian_list = json.loads(record[6]) if record[6] else []
                        if meridian_list:
                            medical_history["Meridian"] = meridian_list
                    except:
                        medical_history["Meridian"] = []
                        
                if record[7]:  # neck_and_shoulder_selection
                    try:
                        neck_list = json.loads(record[7]) if record[7] else []
                        if neck_list:
                            medical_history["Neck"] = neck_list
                    except:
                        medical_history["Neck"] = []
                        
                if record[8]:  # anus_selection
                    try:
                        anus_list = json.loads(record[8]) if record[8] else []
                        if anus_list:
                            medical_history["Anus"] = anus_list
                    except:
                        medical_history["Anus"] = []
                        
                if record[9]:  # family_history_selection
                    try:
                        family_list = json.loads(record[9]) if record[9] else []
                        if family_list:
                            medical_history["Family"] = family_list
                    except:
                        medical_history["Family"] = []
                        
                # 其他症狀說明
                if record[10] and record[10].strip():
                    medical_history["Others"] = record[10]
                
                medical_history_json = json.dumps(medical_history)
                
                # 建立新的記錄，按照舊格式排列
                formatted_record = (
                    record[0],  # medical_record_id
                    record[1],  # member_id
                    record[2],  # name
                    record[3],  # height
                    record[4],  # weight
                    "",  # 血壓 (暫無對應欄位)
                    medical_history_json,  # 病史
                    record[11],  # micro_surgery
                    record[12] if record[12] else "",  # micro_surgery_description
                )
                formatted_records.append(formatted_record)
                
            return formatted_records
    finally:
        conn.close()

def search_medical_records(keyword):
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT 
                mr.medical_record_id, mr.member_id, m.name, mr.height, mr.weight,
                us.HPA_selection, us.meridian_selection, us.neck_and_shoulder_selection, 
                us.anus_selection, us.family_history_selection, us.others,
                CASE WHEN mr.micro_surgery IS NOT NULL THEN 1 ELSE 0 END as micro_surgery, 
                ms.micro_surgery_description
            FROM medical_record mr
            LEFT JOIN member m ON mr.member_id = m.member_id
            LEFT JOIN usual_sympton_and_family_history us ON mr.usual_sympton_and_family_history_id = us.usual_sympton_and_family_history_id
            LEFT JOIN micro_surgery ms ON mr.micro_surgery = ms.micro_surgery_id
            WHERE 
                m.name LIKE %s OR 
                CAST(mr.member_id AS CHAR) LIKE %s
            ORDER BY mr.medical_record_id DESC
            """
            search_param = f"%{keyword}%"
            cursor.execute(sql, (search_param, search_param))
            records = cursor.fetchall()
            
            # 重新格式化資料以符合前端期望
            formatted_records = []
            for record in records:
                # 組合病史為 JSON 格式
                medical_history = {}
                
                # 解析存儲的JSON資料
                if record[5]:  # HPA_selection
                    try:
                        hpa_list = json.loads(record[5]) if record[5] else []
                        if hpa_list:
                            medical_history["HPA"] = hpa_list
                    except:
                        medical_history["HPA"] = []
                        
                if record[6]:  # meridian_selection
                    try:
                        meridian_list = json.loads(record[6]) if record[6] else []
                        if meridian_list:
                            medical_history["Meridian"] = meridian_list
                    except:
                        medical_history["Meridian"] = []
                        
                if record[7]:  # neck_and_shoulder_selection
                    try:
                        neck_list = json.loads(record[7]) if record[7] else []
                        if neck_list:
                            medical_history["Neck"] = neck_list
                    except:
                        medical_history["Neck"] = []
                        
                if record[8]:  # anus_selection
                    try:
                        anus_list = json.loads(record[8]) if record[8] else []
                        if anus_list:
                            medical_history["Anus"] = anus_list
                    except:
                        medical_history["Anus"] = []
                        
                if record[9]:  # family_history_selection
                    try:
                        family_list = json.loads(record[9]) if record[9] else []
                        if family_list:
                            medical_history["Family"] = family_list
                    except:
                        medical_history["Family"] = []
                        
                # 其他症狀說明
                if record[10] and record[10].strip():
                    medical_history["Others"] = record[10]
                
                medical_history_json = json.dumps(medical_history)
                
                # 建立新的記錄，按照舊格式排列
                formatted_record = (
                    record[0],  # medical_record_id
                    record[1],  # member_id
                    record[2],  # name
                    record[3],  # height
                    record[4],  # weight
                    "",  # 血壓 (暫無對應欄位)
                    medical_history_json,  # 病史
                    record[11],  # micro_surgery
                    record[12] if record[12] else "",  # micro_surgery_description
                )
                formatted_records.append(formatted_record)
                
            return formatted_records
    finally:
        conn.close()

def create_medical_record(data):
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            # 輸出調試訊息
            print(f"接收到的資料: {json.dumps(data, ensure_ascii=False)}")
            
            # 嘗試通過姓名查找會員ID
            if data.get('memberId') and not str(data.get('memberId')).isdigit():
                member_name = data.get('memberId')
                cursor.execute("SELECT member_id FROM member WHERE name = %s", (member_name,))
                member = cursor.fetchone()
                if member:
                    member_id = member[0]
                else:
                    # 如果找不到會員，返回錯誤
                    raise ValueError(f"找不到名為 '{member_name}' 的會員")
            else:
                member_id = data.get('memberId')
                
            print(f"使用會員ID: {member_id}")
            
            # 初始化變量，確保所有情況下都有定義
            hpa_data = []
            meridian_data = []
            neck_shoulder_data = []
            anus_data = []
            family_history_data = []
            others_data = ""
            
            # 解析前端傳來的家族病史資料
            if data.get('familyHistory'):
                try:
                    print(f"解析家族病史資料: {data.get('familyHistory')}")
                    # 解析JSON字串
                    family_history_json = json.loads(data.get('familyHistory'))
                    
                    # 提取家族病史資料
                    if 'familyHistory' in family_history_json:
                        family_history_data = family_history_json.get('familyHistory', [])
                    
                    print(f"解析後的家族病史: {family_history_data}")
                except json.JSONDecodeError as e:
                    print(f"解析家族病史JSON失敗: {e}")
            
            # 優先使用 symptomData 字段
            has_symptom_data = False
            
            # 檢查並解析 symptomData
            if data.get('symptomData'):
                try:
                    print(f"使用 symptomData 解析症狀資料: {data.get('symptomData')}")
                    symptom_json = json.loads(data.get('symptomData'))
                    
                    # 提取各類症狀資料
                    hpa_data = symptom_json.get('HPA', [])
                    meridian_data = symptom_json.get('meridian', [])
                    neck_shoulder_data = symptom_json.get('neckAndShoulder', [])
                    anus_data = symptom_json.get('anus', [])
                    others_data = symptom_json.get('others', '')
                    
                    has_symptom_data = True
                    print(f"解析後的症狀資料: HPA={hpa_data}, 經絡={meridian_data}, 肩頸={neck_shoulder_data}, 腸胃={anus_data}")
                except json.JSONDecodeError as e:
                    print(f"解析 symptomData JSON失敗: {e}")
            
            # 如果沒有 symptomData，嘗試解析 symptom 字段
            symptom_value = data.get('symptom')
            is_symptom_boolean = symptom_value == 1 or symptom_value == '1' or symptom_value == True or symptom_value == 'true'
            
            if not has_symptom_data and symptom_value and not is_symptom_boolean:
                try:
                    print(f"使用 symptom 解析症狀資料: {symptom_value}")
                    # 解析症狀JSON字串
                    symptom_json = json.loads(symptom_value)
                    
                    # 提取各類症狀資料
                    hpa_data = symptom_json.get('HPA', [])
                    meridian_data = symptom_json.get('meridian', [])
                    neck_shoulder_data = symptom_json.get('neckAndShoulder', [])
                    anus_data = symptom_json.get('anus', [])
                    others_data = symptom_json.get('others', '')
                    
                    print(f"解析後的症狀資料: HPA={hpa_data}, 經絡={meridian_data}, 肩頸={neck_shoulder_data}, 腸胃={anus_data}")
                except json.JSONDecodeError as e:
                    print(f"解析症狀JSON失敗: {e}")
            
            # --- 新增 health_status 處理邏輯 ---
            health_status_id = None
            if data.get('healthStatus'):
                health_data = json.loads(data.get('healthStatus'))
                cursor.execute("""
                    INSERT INTO health_status (member_id, health_status_selection, others)
                    VALUES (%s, %s, %s)
                """, (
                    member_id,
                    json.dumps(health_data.get('selectedStates', [])),
                    health_data.get('otherText', '')
                ))
                health_status_id = cursor.lastrowid

            # 先處理常見症狀和家族病史
            usual_symptoms_id = None
            if data.get('symptom') or data.get('symptomData') or data.get('familyHistory') or data.get('restrictedGroup'):
                cursor.execute("""
                INSERT INTO usual_sympton_and_family_history (
                    member_id, HPA_selection, meridian_selection, neck_and_shoulder_selection,
                    anus_selection, family_history_selection, others
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    member_id,
                    json.dumps(hpa_data),
                    json.dumps(meridian_data),
                    json.dumps(neck_shoulder_data),
                    json.dumps(anus_data),
                    json.dumps(family_history_data),
                    others_data
                ))
                conn.commit()
                usual_symptoms_id = cursor.lastrowid
                print(f"創建常見症狀和家族病史記錄，ID: {usual_symptoms_id}")
            
            # 處理微整型資訊
            micro_surgery_id = None
            micro_surgery_flag = False
            cosmeticDesc = data.get('cosmeticDesc', '')
            
            # 檢查微整型標誌，支援多種可能的格式
            if is_symptom_boolean:
                micro_surgery_flag = True
                print("症狀欄位表示有微整")
            elif data.get('cosmeticSurgery') == 'Yes' or data.get('cosmeticSurgery') == 1 or data.get('cosmeticSurgery') == '1':
                micro_surgery_flag = True
                print("整容手術欄位表示有微整")
                
            if micro_surgery_flag:
                cursor.execute("""
                INSERT INTO micro_surgery (
                    micro_surgery_selection, micro_surgery_description
                ) VALUES (%s, %s)
                """, (
                    '有微整型',
                    cosmeticDesc
                ))
                conn.commit()
                micro_surgery_id = cursor.lastrowid
                print(f"創建微整型記錄，ID: {micro_surgery_id}，描述: {cosmeticDesc}")
            
            # 最後創建醫療記錄
            cursor.execute("""
            INSERT INTO medical_record (
                member_id, usual_sympton_and_family_history_id, health_status_id,
                height, weight, remark, micro_surgery
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                member_id,
                usual_symptoms_id,
                health_status_id,
                data.get('height'),
                data.get('weight'),
                data.get('remark'), # <-- 新增 remark
                micro_surgery_id
            ))
            
            conn.commit()
            record_id = cursor.lastrowid
            print(f"創建醫療記錄成功，ID: {record_id}")
            return record_id
    except Exception as e:
        conn.rollback()
        print(f"創建醫療記錄時發生錯誤: {str(e)}")
        raise e
    finally:
        conn.close()

def delete_medical_record(record_id):
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            # 首先獲取關聯的 IDs
            cursor.execute("""
            SELECT usual_sympton_and_family_history_id, micro_surgery
            FROM medical_record
            WHERE medical_record_id = %s
            """, (record_id,))
            
            related_ids = cursor.fetchone()
            if not related_ids:
                return False
                
            usual_sympton_id, micro_surgery_id = related_ids
            
            # 刪除醫療記錄
            cursor.execute("DELETE FROM medical_record WHERE medical_record_id = %s", (record_id,))
            
            # 刪除相關的常見症狀和家族病史記錄
            if usual_sympton_id:
                cursor.execute("""
                DELETE FROM usual_sympton_and_family_history 
                WHERE usual_sympton_and_family_history_id = %s
                """, (usual_sympton_id,))
            
            # 刪除相關的微整型記錄
            if micro_surgery_id:
                cursor.execute("DELETE FROM micro_surgery WHERE micro_surgery_id = %s", (micro_surgery_id,))
            
            conn.commit()
            return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_all_medical_records_for_export():
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT 
                mr.medical_record_id, m.name, mr.member_id, mr.height, mr.weight,
                '',  -- 舊格式的血壓欄位，現在無對應
                CASE WHEN mr.micro_surgery IS NOT NULL THEN '是' ELSE '否' END as micro_surgery,
                ms.micro_surgery_description
            FROM medical_record mr
            LEFT JOIN member m ON mr.member_id = m.member_id
            LEFT JOIN micro_surgery ms ON mr.micro_surgery = ms.micro_surgery_id
            ORDER BY mr.medical_record_id DESC
            """
            cursor.execute(sql)
            records = cursor.fetchall()
            return records
    finally:
        conn.close()

# ----------------- 新增以下函數 -----------------
def get_medical_record_by_id(record_id):
    conn = connect_to_db()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 這個 SQL 查詢現在可以正確運作了
            sql = """
            SELECT 
                mr.medical_record_id,
                mr.member_id,
                m.name,
                mr.height,
                mr.weight,
                mr.remark,
                us.HPA_selection,
                us.meridian_selection,
                us.neck_and_shoulder_selection,
                us.anus_selection,
                us.family_history_selection,
                us.others as symptom_others,
                hs.health_status_selection,
                hs.others as health_status_others,
                ms.micro_surgery_description,
                CASE WHEN mr.micro_surgery IS NOT NULL THEN 'Yes' ELSE 'No' END as cosmetic_surgery
            FROM medical_record mr
            LEFT JOIN member m ON mr.member_id = m.member_id
            LEFT JOIN usual_sympton_and_family_history us ON mr.usual_sympton_and_family_history_id = us.usual_sympton_and_family_history_id
            LEFT JOIN micro_surgery ms ON mr.micro_surgery = ms.micro_surgery_id
            LEFT JOIN health_status hs ON mr.health_status_id = hs.health_status_id
            WHERE mr.medical_record_id = %s
            """
            cursor.execute(sql, (record_id,))
            record = cursor.fetchone()
            
            if not record:
                return None

            # 將分散的症狀和健康狀態資料組合成前端需要的 JSON 結構
            symptom_data = {
                "HPA": json.loads(record.get('HPA_selection') or '[]'),
                "meridian": json.loads(record.get('meridian_selection') or '[]'),
                "neckAndShoulder": json.loads(record.get('neck_and_shoulder_selection') or '[]'),
                "anus": json.loads(record.get('anus_selection') or '[]'),
                "symptomOthers": record.get('symptom_others') or ''
            }
            
            family_history_data = {
                "familyHistory": json.loads(record.get('family_history_selection') or '[]'),
                "familyHistoryOthers": ""
            }

            health_status_data = {
                "selectedStates": json.loads(record.get('health_status_selection') or '[]'),
                "otherText": record.get('health_status_others') or ''
            }

            # 組合最終回傳給前端的物件
            return {
                "memberId": record['member_id'],
                "name": record['name'],
                "height": record['height'],
                "weight": record['weight'],
                "bloodPressure": "",
                "remark": record['remark'], # <-- 確保 remark 被回傳
                "cosmeticSurgery": record['cosmetic_surgery'],
                "cosmeticDesc": record['micro_surgery_description'] or '',
                "symptom": json.dumps(symptom_data),
                "familyHistory": json.dumps(family_history_data),
                "healthStatus": json.dumps(health_status_data)
            }
    finally:
        conn.close()

def update_medical_record(record_id, data):
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            # 1. 獲取此紀錄關聯的 IDs
            cursor.execute("""
                SELECT usual_sympton_and_family_history_id, micro_surgery, health_status_id
                FROM medical_record WHERE medical_record_id = %s
            """, (record_id,))
            related_ids = cursor.fetchone()
            if not related_ids:
                raise ValueError("找不到要更新的紀錄")
            
            usual_symptoms_id, micro_surgery_id, health_status_id = related_ids

            # 2. 更新 usual_sympton_and_family_history 表 (這部分不變)
            symptom_data = json.loads(data.get('symptom', '{}'))
            family_data = json.loads(data.get('familyHistory', '{}'))
            if usual_symptoms_id:
                cursor.execute("""
                    UPDATE usual_sympton_and_family_history SET
                        HPA_selection = %s, meridian_selection = %s, neck_and_shoulder_selection = %s,
                        anus_selection = %s, family_history_selection = %s, others = %s
                    WHERE usual_sympton_and_family_history_id = %s
                """, (
                    json.dumps(symptom_data.get('HPA', [])),
                    json.dumps(symptom_data.get('meridian', [])),
                    json.dumps(symptom_data.get('neckAndShoulder', [])),
                    json.dumps(symptom_data.get('anus', [])),
                    json.dumps(family_data.get('familyHistory', [])),
                    symptom_data.get('symptomOthers', ''),
                    usual_symptoms_id
                ))

            # 3. 更新 health_status 表 (這部分不變)
            health_data = json.loads(data.get('healthStatus', '{}'))
            if health_status_id:
                cursor.execute("""
                    UPDATE health_status SET
                        health_status_selection = %s, others = %s
                    WHERE health_status_id = %s
                """, (
                    json.dumps(health_data.get('selectedStates', [])),
                    health_data.get('otherText', ''),
                    health_status_id
                ))

            # --- 4. 重構後的微整型處理邏輯 ---
            new_micro_surgery_fk_id = micro_surgery_id  # 預設外鍵ID不變
            should_delete_old_micro_surgery = False     # 是否需要刪除舊紀錄的旗標

            if data.get('cosmeticSurgery') == 'Yes':
                if micro_surgery_id:
                    # 情況 A: 從 'Yes' 改為 'Yes' -> 更新描述
                    cursor.execute("UPDATE micro_surgery SET micro_surgery_description = %s WHERE micro_surgery_id = %s",
                                   (data.get('cosmeticDesc', ''), micro_surgery_id))
                else:
                    # 情況 B: 從 'No' 改為 'Yes' -> 新增記錄
                    cursor.execute("INSERT INTO micro_surgery (micro_surgery_description) VALUES (%s)", (data.get('cosmeticDesc', '')))
                    new_micro_surgery_fk_id = cursor.lastrowid
            else:  # cosmeticSurgery is 'No'
                if micro_surgery_id:
                    # 情況 C: 從 'Yes' 改為 'No' -> 準備刪除舊記錄，並將外鍵設為 NULL
                    new_micro_surgery_fk_id = None
                    should_delete_old_micro_surgery = True
            
            # --- 5. 更新 medical_record 主表 ---
            # 這次更新會先解除或設定對 micro_surgery 的參考
            cursor.execute("""
                UPDATE medical_record SET
                    height = %s, weight = %s, remark = %s, micro_surgery = %s
                WHERE medical_record_id = %s
            """, (
                data.get('height'),
                data.get('weight'),
                data.get('remark'),
                new_micro_surgery_fk_id,  # 可能是舊ID, 新ID, 或 NULL
                record_id
            ))

            # --- 6. 如果需要，現在可以安全地刪除舊的 micro_surgery 記錄 ---
            if should_delete_old_micro_surgery:
                cursor.execute("DELETE FROM micro_surgery WHERE micro_surgery_id = %s", (micro_surgery_id,))

            conn.commit()
            return True
            
    except Exception as e:
        conn.rollback()
        # 重新引發異常，以便上層可以捕捉到
        raise e
    finally:
        conn.close()
