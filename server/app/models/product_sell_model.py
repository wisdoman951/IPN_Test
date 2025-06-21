# \app\models\product_sell_model.py
import pymysql
from app.config import DB_CONFIG

def connect_to_db():
    """連接到數據庫"""
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

def get_all_product_sells():
    """獲取所有產品銷售紀錄 - 已更新查詢以匹配新表結構"""
    conn = connect_to_db()
    with conn.cursor() as cursor:
        query = """
            SELECT 
                ps.product_sell_id, 
                ps.member_id, 
                m.name as member_name, 
                ps.store_id,
                st.store_name as store_name,  -- 從 store 表獲取店家名稱
                ps.product_id,
                p.name as product_name,       -- 從 product 表獲取產品名稱
                ps.quantity,                  -- 從 product_sell 表獲取銷售數量
                ps.unit_price,                -- 從 product_sell 表獲取銷售單價
                ps.discount_amount,           -- 從 product_sell 表獲取折扣金額
                ps.final_price,               -- 從 product_sell 表獲取最終價格
                ps.payment_method,            -- 從 product_sell 表獲取付款方式
                sf.name as staff_name,        -- 從 staff 表獲取銷售人員名稱
                ps.sale_category,             -- 從 product_sell 表獲取銷售類別
                ps.date,
                ps.note
            FROM product_sell ps
            LEFT JOIN member m ON ps.member_id = m.member_id
            LEFT JOIN store st ON ps.store_id = st.store_id     -- JOIN store 表
            LEFT JOIN product p ON ps.product_id = p.product_id -- JOIN product 表
            LEFT JOIN staff sf ON ps.staff_id = sf.staff_id     -- JOIN staff 表
            ORDER BY ps.date DESC, ps.product_sell_id DESC -- 建議增加一個排序條件以確保順序穩定
        """
        cursor.execute(query)
        result = cursor.fetchall()
    conn.close()
    return result

def get_product_sell_by_id(sell_id: int): # 建議加上型別提示
    """根據ID獲取產品銷售紀錄 - 已更新查詢"""
    conn = None
    try:
        conn = connect_to_db()
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    ps.product_sell_id, 
                    ps.member_id, 
                    m.name AS member_name, 
                    ps.store_id,
                    st.store_name AS store_name,
                    ps.product_id,
                    p.name AS product_name,
                    ps.quantity,
                    ps.unit_price,        -- 銷售時的單價
                    ps.discount_amount,   -- 折扣金額
                    ps.final_price,       -- 最終價格
                    ps.payment_method,
                    sf.staff_id AS staff_id,     -- 獲取 staff_id
                    sf.name AS staff_name,   -- 銷售人員名稱
                    ps.sale_category,
                    ps.date,              -- 資料庫中是 DATE 型別
                    ps.note
                FROM product_sell ps
                LEFT JOIN member m ON ps.member_id = m.member_id
                LEFT JOIN store st ON ps.store_id = st.store_id
                LEFT JOIN product p ON ps.product_id = p.product_id
                LEFT JOIN staff sf ON ps.staff_id = sf.staff_id
                WHERE ps.product_sell_id = %s
            """
            cursor.execute(query, (sell_id,))
            result = cursor.fetchone()
        
        return result 
    except Exception as e:
        print(f"Error in get_product_sell_by_id for ID {sell_id}: {e}")
        raise e # 重新拋出，讓 Flask 路由處理
    finally:
        if conn:
            conn.close()
def insert_product_sell(data: dict):
    """新增產品銷售紀錄 - 已更新以符合新表結構"""
    conn = None # 初始化 conn
    try:
        conn = connect_to_db()
        with conn.cursor() as cursor:
            query = """
                INSERT INTO product_sell (
                    member_id, staff_id, store_id, product_id, 
                    date, quantity, unit_price, discount_amount, final_price, 
                    payment_method, sale_category, note
                ) VALUES (
                    %(member_id)s, %(staff_id)s, %(store_id)s, %(product_id)s, 
                    %(date)s, %(quantity)s, %(unit_price)s, %(discount_amount)s, %(final_price)s,
                    %(payment_method)s, %(sale_category)s, %(note)s
                )
            """
            
            values_dict = {
                "member_id": data.get("member_id"),
                "staff_id": data.get("staff_id"),
                "store_id": data.get("store_id"),
                "product_id": data.get("product_id"),
                "date": data.get("date"),
                "quantity": data.get("quantity"),
                "unit_price": data.get("unit_price"),
                "discount_amount": data.get("discount_amount", 0.00),
                "final_price": data.get("final_price"),
                "payment_method": data.get("payment_method", '現金'),
                "sale_category": data.get("sale_category"),
                "note": data.get("note")
            }
            
            # 簡單的必需欄位檢查 (可以做得更完善)
            required_fields = ["member_id", "store_id", "product_id", "date", "quantity", "unit_price", "final_price", "payment_method", "staff_id", "sale_category"]
            for field in required_fields:
                if values_dict.get(field) is None:
                    raise ValueError(f"欄位 '{field}' 是必需的，但未在提交的資料中提供。")

            cursor.execute(query, values_dict)
            sell_id = conn.insert_id()
            
            # --- 更新庫存的邏輯 ---
            product_id_sold = data.get("product_id")
            store_id_of_sale = data.get("store_id")
            quantity_sold = data.get("quantity")

            if product_id_sold is not None and store_id_of_sale is not None and quantity_sold is not None:
                # 減少庫存 (傳入負數)
                update_inventory_after_sale(product_id_sold, store_id_of_sale, -abs(int(quantity_sold)), cursor)
            else:
                print(f"警告：新增銷售 {sell_id} 時，缺少用於更新庫存的 product_id, store_id, 或 quantity。")

        conn.commit()
        return sell_id
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error in insert_product_sell: {e}") # 打印更詳細的錯誤
        raise e
    finally:
        if conn:
            conn.close()

def update_inventory_quantity(product_id: int, store_id: int, quantity_change: int, cursor: pymysql.cursors.DictCursor):
    """
    更新指定產品在指定店家的庫存數量。

    參數:
        product_id (int): 要更新庫存的產品 ID。
        store_id (int): 產品所在的店家 ID。
        quantity_change (int): 庫存的變動量。
                                 正數表示增加庫存 (例如，取消銷售或退貨)。
                                 負數表示減少庫存 (例如，產生銷售)。
        cursor (pymysql.cursors.DictCursor): 外部傳入的資料庫游標，用於事務控制。

    假設:
    - `inventory` 表中有 `product_id`, `store_id`, `quantity` 欄位。
    - `quantity` 欄位代表該產品在該店家的當前總庫存水平。
    - 我們將更新符合 `product_id` 和 `store_id` 的最新一條 `inventory` 記錄。
      (如果一個 product/store 組合只有一條庫存記錄，則 `ORDER BY ... LIMIT 1` 不是必需的，
       但如果有多條，則需要明確更新哪一條，或您的 inventory 表結構應確保唯一性)。

    注意: 
    如果您的 `inventory` 表是作為一個「庫存異動日誌」來設計的（記錄每一次的 stock_in/stock_out），
    那麼這個函數的邏輯應該是 INSERT 一條新的異動記錄，而不是 UPDATE 現有記錄的 quantity。
    目前的實現是基於「直接更新總庫存量」的假設。
    """
    if not all([isinstance(product_id, int), isinstance(store_id, int), isinstance(quantity_change, int)]):
        raise TypeError("product_id, store_id, and quantity_change must be integers.")
    if quantity_change == 0:
        print(f"Inventory quantity change is zero for product_id={product_id}, store_id={store_id}. No update performed.")
        return True # 數量未變，無需更新

    # 根據您的 inventory 表結構，這個 UPDATE 語句可能需要調整
    # 特別是 WHERE 子句如何精確定位到要更新的庫存記錄
    update_query = """
        UPDATE inventory
        SET quantity = quantity + (%s)  -- 直接增減庫存總量
        WHERE product_id = %s AND store_id = %s
    """
    # 為了更安全，如果您的 inventory 表 (product_id, store_id) 不是唯一鍵，
    # 且您確實想更新最新的那條，再取消 ORDER BY ... LIMIT 1 的註解，
    # 否則，如果有多條符合 product_id 和 store_id 的記錄，它們都會被更新，這可能不是預期的。
    # 這裡我們先假設 (product_id, store_id) 能大致定位到要更新的庫存。
    
    try:
        print(f"Attempting to update inventory: product_id={product_id}, store_id={store_id}, change={quantity_change}")
        
        # 先檢查庫存記錄是否存在，以及更新後的庫存是否會變為負數 (如果您的業務邏輯不允許負庫存)
        # select_query = "SELECT quantity FROM inventory WHERE product_id = %s AND store_id = %s ORDER BY inventory_id DESC LIMIT 1"
        # cursor.execute(select_query, (product_id, store_id))
        # current_inventory = cursor.fetchone()
        # if current_inventory and (current_inventory['quantity'] + quantity_change < 0):
        #     raise ValueError(f"Insufficient stock for product_id {product_id} at store_id {store_id}.")

        affected_rows = cursor.execute(update_query, (quantity_change, product_id, store_id))
        
        if affected_rows == 0:
            # 如果沒有找到記錄來更新，這是一個問題。
            # 可能表示該產品在該店家還沒有庫存記錄，或者 product_id/store_id 不正確。
            # 根據您的業務邏輯，這裡可能需要：
            # 1. 拋出錯誤 (如下面的例子)
            # 2. 創建一個新的庫存記錄 (如果允許的話)
            # 3. 靜默失敗或記錄警告
            print(f"Warning: No inventory record found to update for product_id={product_id}, store_id={store_id} when applying change {quantity_change}. Inventory might be unmanaged for this combination or IDs are incorrect.")
            # raise ValueError(f"No inventory record to update for product_id {product_id} at store_id {store_id}")
        
        print(f"Inventory update for product_id={product_id}, store_id={store_id}: {affected_rows} row(s) affected by quantity change of {quantity_change}.")
        return affected_rows > 0 # 或者可以返回 True/False 表示是否成功
        
    except Exception as e:
        print(f"Error in update_inventory_quantity for product_id={product_id}, store_id={store_id}: {e}")
        # 確保錯誤被重新拋出，以便調用它的函數 (如 insert_product_sell) 中的事務可以回滾
        raise

def update_product_sell(sell_id: int, data: dict):
    """更新產品銷售紀錄 - 已更新以符合新表結構和庫存邏輯"""
    conn = None
    try:
        conn = connect_to_db()
        with conn.cursor() as cursor:
            # 1. 獲取原始銷售記錄的 product_id, quantity, store_id 以便後續比較庫存
            cursor.execute(
                "SELECT product_id, quantity, store_id FROM product_sell WHERE product_sell_id = %s",
                (sell_id,)
            )
            original_sell = cursor.fetchone()
            if not original_sell:
                raise ValueError(f"找不到指定的原始銷售記錄 ID: {sell_id}")

            original_product_id = original_sell['product_id']
            original_quantity = original_sell['quantity']
            original_store_id = original_sell['store_id']

            # 準備更新的欄位列表和對應的值
            fields_to_update = []
            values_to_update = []
            
            # 這些是 product_sell 表中允許從前端 data 更新的欄位
            allowed_fields_from_data = [
                "member_id", "staff_id", "store_id", "product_id", "date", 
                "quantity", "unit_price", "discount_amount", "final_price", 
                "payment_method", "sale_category", "note"
            ]

            for field in allowed_fields_from_data:
                if field in data and data.get(field) is not None: # 確保 data 中有此欄位且值不是 None
                    fields_to_update.append(f"`{field}` = %s") # 使用反引號保護欄位名
                    values_to_update.append(data.get(field))
            
            if not fields_to_update:
                print(f"銷售記錄 {sell_id} 沒有需要更新的欄位。")
                if conn: conn.close()
                return True # 沒有需要更新的欄位

            update_query = f"""
                UPDATE product_sell
                SET {', '.join(fields_to_update)}
                WHERE product_sell_id = %s
            """
            values_to_update.append(sell_id)
            
            print(f"Executing update query: {update_query} with params: {tuple(values_to_update)}")
            cursor.execute(update_query, tuple(values_to_update))

            # 2. 處理庫存調整
            # 從 data 中獲取更新後的值，如果 data 中沒有，則使用 original_sell 的值
            new_product_id = int(data.get("product_id", original_product_id))
            new_quantity = int(data.get("quantity", original_quantity))
            # 假設 store_id 在編輯銷售記錄時不輕易改變，如果允許改變，則也從 data.get 獲取
            new_store_id = int(data.get("store_id", original_store_id)) 

            inventory_adjusted = False
            # 只有當產品ID、數量或商店ID實際發生變化時才調整庫存
            if (new_product_id != original_product_id or 
                new_quantity != original_quantity or 
                new_store_id != original_store_id):
                
                print(f"需要調整庫存：原({original_product_id}, q:{original_quantity}, s:{original_store_id}) -> 新({new_product_id}, q:{new_quantity}, s:{new_store_id})")

                # a. 將原銷售的產品數量加回原店家庫存
                update_inventory_after_sale(original_product_id, original_store_id, original_quantity, cursor) # 加回正數
                print(f"庫存調整：原產品 {original_product_id} 在店家 {original_store_id} 加回數量 {original_quantity}")
                
                # b. 將新銷售的產品數量從新店家庫存中扣除
                update_inventory_after_sale(new_product_id, new_store_id, -new_quantity, cursor) # 扣除負數
                print(f"庫存調整：新產品 {new_product_id} 在店家 {new_store_id} 扣除數量 {new_quantity}")
                inventory_adjusted = True
            
            conn.commit()
            print(f"銷售記錄 {sell_id} 更新成功。庫存是否調整: {inventory_adjusted}")
            return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error in update_product_sell for ID {sell_id}: {e}")
        raise e # 將錯誤重新拋出，以便 Flask 路由可以捕獲
    finally:
        if conn:
            conn.close()
def delete_product_sell(sell_id):
    """刪除產品銷售紀錄"""
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            # 獲取要刪除的記錄以還原庫存
            cursor.execute(
                "SELECT inventory_id FROM product_sell WHERE product_sell_id = %s",
                (sell_id,)
            )
            sell = cursor.fetchone()
            
            if not sell:
                raise ValueError("找不到指定的銷售記錄")
            
            query = "DELETE FROM product_sell WHERE product_sell_id = %s"
            cursor.execute(query, (sell_id,))
            
            # 恢復庫存數量
            update_inventory_quantity(sell["inventory_id"], 1)
            
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def update_inventory_after_sale(product_id: int, store_id: int, quantity_change: int, cursor: pymysql.cursors.DictCursor):
    update_query = """
        UPDATE inventory 
        SET quantity = quantity + (%s) 
        WHERE product_id = %s AND store_id = %s
        ORDER BY inventory_id DESC LIMIT 1 
    """
    try:
        print(f"Attempting to update inventory: product_id={product_id}, store_id={store_id}, change={quantity_change}")
        affected_rows = cursor.execute(update_query, (quantity_change, product_id, store_id))
        if affected_rows == 0:
            # 如果沒有找到對應的庫存記錄來更新，這裡的處理方式很重要。
            # 1. 可能是該產品在該店家還沒有庫存記錄 -> 是否應該自動創建一個？
            # 2. 或者是 product_id 或 store_id 不正確。
            # 3. 如果 inventory 表是交易日誌，那麼這裡應該是 INSERT 新記錄，而不是 UPDATE。
            print(f"Warning: No inventory record found to update for product_id={product_id}, store_id={store_id}. Stock might be unmanaged or new for this combination.")
            # 根據您的業務邏輯，這裡可能需要拋出錯誤，或者創建新的庫存條目。
            # 例如: raise ValueError(f"No inventory record for product {product_id} at store {store_id}")
        print(f"Inventory update for product_id={product_id}, store_id={store_id}: {affected_rows} row(s) affected.")
    except Exception as e:
        print(f"Error in update_inventory_after_sale for product_id={product_id}, store_id={store_id}: {e}")
        raise # 將錯誤重新拋出，以便外層事務可以 rollback

def update_product_sell(sell_id: int, data: dict):
    """更新產品銷售紀錄 - 已更新以符合新表結構和庫存邏輯"""
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            # 1. 獲取原始銷售記錄的 product_id, quantity, store_id, staff_id
            cursor.execute(
                "SELECT product_id, quantity, store_id, staff_id FROM product_sell WHERE product_sell_id = %s",
                (sell_id,)
            )
            original_sell = cursor.fetchone()
            if not original_sell:
                raise ValueError(f"找不到指定的銷售記錄 ID: {sell_id}")

            original_product_id = original_sell['product_id']
            original_quantity = original_sell['quantity']
            original_store_id = original_sell['store_id'] # 假設 store_id 通常不變，如果變更則庫存調整更複雜
            # original_staff_id = original_sell['staff_id'] # 如果需要比較

            # 準備更新的欄位列表和對應的值
            fields_to_update = []
            values_to_update = []

            # 根據 data 字典動態構建 SET 子句
            # 確保 data 中的 key 與資料庫欄位名一致
            # 這些是 product_sell 表中允許更新的欄位
            allowed_fields = [
                "member_id", "staff_id", "store_id", "product_id", "date", 
                "quantity", "unit_price", "discount_amount", "final_price", 
                "payment_method", "sale_category", "note"
            ]

            for field in allowed_fields:
                if field in data: # 只有當 data 中提供了該欄位時才更新
                    fields_to_update.append(f"{field} = %s")
                    values_to_update.append(data.get(field))
            
            if not fields_to_update:
                conn.close()
                return True # 沒有需要更新的欄位

            query = f"""
                UPDATE product_sell
                SET {', '.join(fields_to_update)}
                WHERE product_sell_id = %s
            """
            values_to_update.append(sell_id)
            
            cursor.execute(query, tuple(values_to_update))

            # 2. 處理庫存調整
            new_product_id = int(data.get("product_id", original_product_id))
            new_quantity = int(data.get("quantity", original_quantity))
            new_store_id = int(data.get("store_id", original_store_id)) # 假設 store_id 也可能變更

            inventory_adjusted = False
            if new_product_id != original_product_id or new_quantity != original_quantity or new_store_id != original_store_id:
                # 產品、數量或店家有變更，需要調整庫存
                # a. 將原銷售的產品數量加回原店家庫存
                update_inventory_quantity(original_product_id, original_store_id, original_quantity, cursor) # 加回正數
                print(f"庫存調整：原產品 {original_product_id} 在店家 {original_store_id} 加回數量 {original_quantity}")
                
                # b. 將新銷售的產品數量從新店家庫存中扣除
                update_inventory_quantity(new_product_id, new_store_id, -new_quantity, cursor) # 扣除負數
                print(f"庫存調整：新產品 {new_product_id} 在店家 {new_store_id} 扣除數量 {new_quantity}")
                inventory_adjusted = True
            
            conn.commit()
            print(f"銷售記錄 {sell_id} 更新成功。庫存是否調整: {inventory_adjusted}")
            return True
    except Exception as e:
        conn.rollback()
        print(f"Error in update_product_sell for ID {sell_id}: {e}")
        raise e
    finally:
        if conn:
            conn.close()

def delete_product_sell(sell_id: int):
    """刪除產品銷售紀錄 - 已更新庫存邏輯"""
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            # 1. 獲取要刪除的記錄的 product_id, quantity, store_id 以便還原庫存
            cursor.execute(
                "SELECT product_id, quantity, store_id FROM product_sell WHERE product_sell_id = %s",
                (sell_id,)
            )
            sell_to_delete = cursor.fetchone()
            
            if not sell_to_delete:
                raise ValueError(f"找不到指定的銷售記錄 ID: {sell_id}")
            
            product_id_to_restore = sell_to_delete['product_id']
            quantity_to_restore = sell_to_delete['quantity']
            store_id_to_restore = sell_to_delete['store_id']

            # 2. 刪除銷售記錄
            query = "DELETE FROM product_sell WHERE product_sell_id = %s"
            affected_rows = cursor.execute(query, (sell_id,))
            
            if affected_rows == 0:
                 # 雖然上面已經檢查過，但多一層防護
                raise ValueError(f"嘗試刪除銷售記錄 ID: {sell_id} 失敗，記錄可能已被刪除。")

            # 3. 恢復庫存數量
            update_inventory_quantity(product_id_to_restore, store_id_to_restore, quantity_to_restore, cursor) # 加回正數
            print(f"庫存調整：產品 {product_id_to_restore} 在店家 {store_id_to_restore} 加回數量 {quantity_to_restore} (因銷售記錄 {sell_id} 刪除)")
            
            conn.commit()
            print(f"銷售記錄 {sell_id} 刪除成功。")
            return True
    except Exception as e:
        conn.rollback()
        print(f"Error in delete_product_sell for ID {sell_id}: {e}")
        raise e
    finally:
        if conn:
            conn.close()

def get_all_products_with_inventory():
    """獲取所有產品及其在 inventory 表中的記錄 (可能每個產品有多條 inventory 記錄)"""
    conn = connect_to_db()
    with conn.cursor() as cursor:
        # 這個查詢會返回每個產品，以及它在 inventory 表中所有相關的記錄
        # 如果您只想知道每個產品的「總庫存」，您需要修改此查詢或 inventory 表的結構
        query = """
            SELECT 
                p.product_id, 
                p.name as product_name, 
                p.price as product_price,
                i.inventory_id,
                i.quantity as inventory_quantity, -- 重命名以區分銷售數量
                i.store_id,
                s.store_name
            FROM product p
            LEFT JOIN inventory i ON p.product_id = i.product_id
            LEFT JOIN store s ON i.store_id = s.store_id
            ORDER BY p.name, i.store_id, i.date DESC 
        """
        cursor.execute(query)
        result = cursor.fetchall()
    conn.close()
    return result

def search_products_with_inventory(keyword):
    """搜尋產品及其庫存信息 (邏輯同上)"""
    conn = connect_to_db()
    with conn.cursor() as cursor:
        like = f"%{keyword}%"
        query = """
            SELECT 
                p.product_id, 
                p.name as product_name, 
                p.price as product_price,
                i.inventory_id,
                i.quantity as inventory_quantity,
                i.store_id,
                s.store_name
            FROM product p
            LEFT JOIN inventory i ON p.product_id = i.product_id
            LEFT JOIN store s ON i.store_id = s.store_id
            WHERE p.name LIKE %s OR p.code LIKE %s -- 假設也可以按產品代碼搜尋
            ORDER BY p.name, i.store_id, i.date DESC
        """
        cursor.execute(query, (like, like))
        result = cursor.fetchall()
    conn.close()
    return result

def export_product_sells(store_id=None):
    """匯出產品銷售記錄（可選擇性根據商店ID過濾）- 更新查詢"""
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            base_query = """
                SELECT 
                    ps.product_sell_id, 
                    ps.member_id, 
                    m.name as member_name, 
                    ps.store_id,
                    st.store_name as store_name,
                    ps.product_id,
                    p.name as product_name,
                    ps.quantity,
                    ps.unit_price,
                    ps.discount_amount,
                    ps.final_price,        -- 直接使用 final_price
                    ps.payment_method,
                    sf.name as staff_name,
                    ps.sale_category,
                    DATE_FORMAT(ps.date, '%Y-%m-%d') as date, -- 格式化日期
                    ps.note
                FROM product_sell ps
                LEFT JOIN member m ON ps.member_id = m.member_id
                LEFT JOIN store st ON ps.store_id = st.store_id
                LEFT JOIN product p ON ps.product_id = p.product_id
                LEFT JOIN staff sf ON ps.staff_id = sf.staff_id
            """
            params = []
            if store_id:
                query = base_query + " WHERE ps.store_id = %s ORDER BY ps.date DESC, ps.product_sell_id DESC"
                params.append(store_id)
            else:
                query = base_query + " ORDER BY ps.date DESC, ps.product_sell_id DESC"
            
            cursor.execute(query, tuple(params))
            result = cursor.fetchall()
        return result # 假設匯出邏輯在 Flask 路由中處理 Excel/CSV 生成
    except Exception as e:
        print(f"Error in export_product_sells: {e}")
        raise e
    finally:
        if conn:
            conn.close()

def search_product_sells(keyword, store_id=None):
    """搜尋產品銷售紀錄 - 已更新查詢以匹配新表結構"""
    conn = connect_to_db()
    with conn.cursor() as cursor:
        like_keyword = f"%{keyword}%"

        # 基礎查詢，選取所有需要的欄位
        # 注意：這裡的 SELECT 列表也需要與您最新的 product_sell 表結構和前端期望一致
        query_select_list = """
            SELECT 
                ps.product_sell_id, 
                ps.member_id, 
                m.name as member_name, 
                ps.store_id,
                st.store_name as store_name,
                ps.product_id,
                p.name as product_name,
                ps.quantity,
                ps.unit_price,
                ps.discount_amount,
                ps.final_price,
                ps.payment_method,
                sf.name as staff_name,
                ps.sale_category,
                DATE_FORMAT(ps.date, '%%Y-%%m-%%d') as date, -- <--- 修改這裡，使用 %%
                ps.note
            FROM product_sell ps
            LEFT JOIN member m ON ps.member_id = m.member_id
            LEFT JOIN store st ON ps.store_id = st.store_id
            LEFT JOIN product p ON ps.product_id = p.product_id
            LEFT JOIN staff sf ON ps.staff_id = sf.staff_id
        """

        conditions = []
        params = []

        # 關鍵字搜尋條件 (Figma 提示是 "姓名/電話/編號")
        # 您的 searchProductSells 服務需要能處理這些
        # 以下是一個示例，您需要根據您的搜尋邏輯調整
        if keyword:
            keyword_conditions = []
            keyword_params = []

            # 搜尋會員姓名
            keyword_conditions.append("m.name LIKE %s")
            keyword_params.append(like_keyword)

            # 搜尋會員電話 (member 表需要有 phone 欄位)
            # if 'phone' in m.columns: # 假設可以這樣檢查，或者直接加入
            #     keyword_conditions.append("m.phone LIKE %s")
            #     keyword_params.append(like_keyword)

            # 搜尋會員編號 (member_id)
            keyword_conditions.append("CAST(ps.member_id AS CHAR) LIKE %s") # member_id 是 INT，轉為 CHAR 比較
            keyword_params.append(like_keyword)

            # 也可以加入對 product_name, note 等的搜尋
            keyword_conditions.append("p.name LIKE %s")
            keyword_params.append(like_keyword)
            keyword_conditions.append("ps.note LIKE %s")
            keyword_params.append(like_keyword)

            conditions.append(f"({' OR '.join(keyword_conditions)})")
            params.extend(keyword_params)

        # 店家 ID 過濾 (如果有的話)
        if store_id:
            conditions.append("ps.store_id = %s")
            params.append(store_id)

        query_where_clause = ""
        if conditions:
            query_where_clause = "WHERE " + " AND ".join(conditions)

        query = query_select_list + query_where_clause + " ORDER BY ps.date DESC, ps.product_sell_id DESC"

        print(f"Executing search query: {query} with params: {params}") # 調試用
        cursor.execute(query, tuple(params))
        result = cursor.fetchall()
    conn.close()
    # 日期格式化 (如果需要且 DictCursor 返回的是 date 物件)
    # for row in result:
    #     if row.get('date') and not isinstance(row.get('date'), str):
    #         row['date'] = row['date'].isoformat()
    return result