#!/usr/bin/env python3
import re, math

def eval_cell_formula(formula, data_rows, headers):
    """
    解析 `J2*6`, `ROUNDUP(K2*2,0)` 等公式，用源数据计算数值。
    
    列名: A B C ... Z (1-indexed in formula)
    行号: 实际数据行号（1=header row, 2=first data row）
    
    data_rows: 源表数据行（不含表头）
    headers: 源表表头
    """
    s = str(formula).strip()
    
    # Replace cell references like J2, K3 with actual values
    # Pattern: single letter + number (like J2, K15)
    def resolve_cell(m):
        col_letter = m.group(1).upper()
        row_num = int(m.group(2))
        
        col_idx = ord(col_letter) - 65  # A=0, B=1, ...
        data_row_idx = row_num - 2  # Row 1 in source = header, Row 2 = first data (index 0)
        
        if data_row_idx < 0 or data_row_idx >= len(data_rows):
            return "0"
        if col_idx < 0 or col_idx >= len(data_rows[data_row_idx]):
            return "0"
        
        val = data_rows[data_row_idx][col_idx]
        if val is None:
            return "0"
        return str(val)
    
    evaluated = re.sub(r'([A-Z])(\d+)', resolve_cell, s)
    
    # Handle ROUNDUP(x, 0)
    def do_roundup(m):
        inner = eval_simple(m.group(1))
        return str(math.ceil(inner))
    
    # Handle ROUNDDOWN(x, 0)  
    def do_rounddown(m):
        inner = eval_simple(m.group(1))
        return str(math.floor(inner))
    
    evaluated = re.sub(r'ROUNDUP\(([^,]+),0\)', do_roundup, evaluated)
    evaluated = re.sub(r'ROUNDDOWN\(([^,]+),0\)', do_rounddown, evaluated)
    evaluated = re.sub(r'ROUND\(([^,]+),0\)', do_roundup, evaluated)
    
    return _safe_eval(evaluated)

def eval_simple(expr):
    """Evaluate a simple arithmetic expression"""
    try:
        return float(eval(expr, {"__builtins__": {}}, {}))
    except:
        return 0.0

def _safe_eval(expr_str):
    """Safely evaluate arithmetic expression"""
    # Remove any remaining non-numeric/operator chars
    safe = re.sub(r'[^0-9+\-*/().,% ]', '', expr_str)
    # Remove % and commas
    safe = safe.replace('%', '').replace(',', '')
    if not safe.strip():
        return 0
    try:
        return float(eval(safe, {"__builtins__": {}}, {"round": round, "int": int, "float": float}))
    except:
        return 0.0

def is_formula(val):
    """Check if value looks like a formula that needs evaluation"""
    if not isinstance(val, str):
        return False
    return bool(re.search(r'[=*/()ROUNDUP,ROUNDDOWN]+', val))

def evaluate_source_value(val, data_rows, headers):
    """Convert source value to numeric - either direct or via formula evaluation"""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        s = val.strip()
        if not s:
            return None
        # Try direct numeric first
        try:
            return float(s) if '.' in s else int(s)
        except:
            pass
        # Try formula evaluation
        if is_formula(val):
            result = eval_cell_formula(val, data_rows, headers)
            if result != 0 or "0" in s:
                return int(result) if result == int(result) else result
    return None

# =========== 测试 ===========
if __name__ == "__main__":
    # Simulate source data
    headers = ["ID备份", "怪物名", "怪物类型", "空中单位", "攻击方式", "怪物形象", 
               "捕捉次数", "出现权重", "参考概率", "基础血量", "基础伤害", 
               "攻击频率", "攻击距离", "基础移速", "特殊能力", "dps", "强度比"]
    
    data = [
        ["", "普通丧尸", "小怪", "否", "近战", "", 1, "", "", 80, 10, "3秒", 10, 50, "无", "", ""],
        ["", "弹跳丧尸", "小怪", "否", "近战", "", 1, "", "", 80, 15, "5秒", 10, 70, "无", "", ""],
    ]
    
    tests = [
        ("J2*6", 480),
        ("ROUNDUP(K2*2,0)", 20),
        ("ROUNDDOWN(N2*0.8,0)", 40),
        ("J3*6", 480),
        ("ROUNDUP(K3*2,0)", 30),
        ("ROUNDDOWN(N3*0.8,0)", 56),
    ]
    
    for formula, expected in tests:
        result = eval_cell_formula(formula, data, headers)
        status = "✅" if abs(result - expected) < 0.01 else "❌"
        print(f"  {status} {formula} = {result} (expected {expected})")
