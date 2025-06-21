from flask import Blueprint, request, jsonify
from app.models.stress_test_model import (
    get_all_stress_tests, 
    add_stress_test, 
    update_stress_test,
    delete_stress_test, 
    get_stress_test_by_id,
    get_stress_tests_by_member_id
)

stress_test = Blueprint('stress_test', __name__)

@stress_test.route('', methods=['GET'])
def get_stress_tests():
    try:
        # 獲取查詢參數
        filters = {
            'name': request.args.get('name', ''),
            'member_id': request.args.get('member_id', '')
        }
        
        # 使用 model 函數獲取數據
        results = get_all_stress_tests(filters)
        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@stress_test.route('/member/<int:member_id>', methods=['GET'])
def get_member_stress_tests(member_id):
    try:
        results = get_stress_tests_by_member_id(member_id)
        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@stress_test.route('/<int:stress_id>', methods=['GET'])
def get_stress_test(stress_id):
    try:
        result = get_stress_test_by_id(stress_id)
        if result:
            return jsonify({"success": True, "data": result})
        else:
            return jsonify({"success": False, "error": "找不到該壓力測試記錄"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@stress_test.route('', methods=['POST'])
def add_stress_test_route():
    try:
        data = request.json
        
        member_id = data.get('member_id')
        
        if not member_id:
            return jsonify({"success": False, "error": "缺少會員ID (member_id)"}), 400
        
        # 處理分項分數
        scores = {
            'a_score': data.get('a_score', 0),
            'b_score': data.get('b_score', 0),
            'c_score': data.get('c_score', 0),
            'd_score': data.get('d_score', 0)
        }
        
        # 如果提供了答案而非分數，則計算分數
        answers = data.get('answers')
        if answers:
            calculated_scores = calculate_stress_scores(answers)
            scores.update(calculated_scores)
        
        # 使用 model 函數保存數據
        stress_id = add_stress_test(member_id, scores)
        
        return jsonify({
            "success": True,
            "message": "壓力測試儲存成功",
            "stress_id": stress_id,
            "scores": scores,
            "total_score": sum(scores.values())
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@stress_test.route('/<int:stress_id>', methods=['PUT'])
def update_stress_test_route(stress_id):
    try:
        data = request.json
        
        # 處理分項分數
        scores = {
            'a_score': data.get('a_score', 0),
            'b_score': data.get('b_score', 0),
            'c_score': data.get('c_score', 0),
            'd_score': data.get('d_score', 0)
        }
        
        # 如果提供了答案而非分數，則計算分數
        answers = data.get('answers')
        if answers:
            calculated_scores = calculate_stress_scores(answers)
            scores.update(calculated_scores)
        
        # 使用 model 函數更新數據
        update_stress_test(stress_id, scores)
        
        return jsonify({
            "success": True,
            "message": "壓力測試更新成功",
            "scores": scores,
            "total_score": sum(scores.values())
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def calculate_stress_scores(answers):
    """計算壓力測試各項分數
    
    Args:
        answers: 問題答案字典，格式如 {'a1': 'A', 'a2': 'B', ...}
                 其中 a* 為 A 類問題, b* 為 B 類問題, 以此類推
    
    Returns:
        包含 a_score, b_score, c_score, d_score 的字典
    """
    scores = {'a_score': 0, 'b_score': 0, 'c_score': 0, 'd_score': 0}
    
    for question_id, answer in answers.items():
        # 根據問題ID前綴確定是哪一類問題
        category = question_id[0] if question_id[0] in ['a', 'b', 'c', 'd'] else None
        
        if category:
            score_key = f"{category}_score"
            value = 0
            
            if answer == 'A':
                value = 1
            elif answer == 'B':
                value = 2
            elif answer == 'C':
                value = 3
            elif answer == 'D':
                value = 4
                
            scores[score_key] += value
    
    return scores

@stress_test.route('/<int:stress_id>', methods=['DELETE'])
def delete_stress_test_route(stress_id):
    try:
        delete_stress_test(stress_id)
        return jsonify({"success": True, "message": "壓力測試刪除成功"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500 