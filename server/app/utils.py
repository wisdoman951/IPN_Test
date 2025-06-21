# IPN_ERP/server/app/utils.py

from flask_login import current_user

def get_store_based_where_condition(table_alias=None):
    """
    根據 flask_login 的 current_user 權限，產生 SQL 的 WHERE 條件句。
    :param table_alias: 查詢語句中，包含 store_id 的資料表的 SQL 別名 (例如 's', 'mr')。
    :return: 一個包含 (SQL 條件字串, [參數]) 的元組 (tuple)。
    """
    # 檢查使用者是否登入
    if not current_user.is_authenticated:
        # 未登入，回傳一個永遠為假的條件，防止資料外洩
        return (" AND 1=0 ", [])

    permission = current_user.permission
    store_id = current_user.id  # 在我們的 User class 中，id 就是 store_id

    # 如果是總部 admin，不添加任何 store_id 過濾條件
    if permission == 'admin':
        return ("", [])  # 回傳空字串，表示查詢所有分店

    # 如果是分店 basic，添加 store_id 過濾條件
    if permission == 'basic' and store_id:
        if not table_alias:
            # 如果沒有提供資料表別名，直接使用欄位名
            return (f" AND store_id = %s ", [store_id])
        else:
            # 如果有提供別名，使用 "別名.欄位名" 的格式
            return (f" AND {table_alias}.store_id = %s ", [store_id])
    
    # 所有其他情況（例如權限未定義），都回傳一個永遠為假的條件
    return (" AND 1=0 ", [])