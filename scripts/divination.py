#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
占卜计算辅助脚本 - shusu-divination
支持：小六壬起课 / 梅花易数起卦 / 六爻模拟起卦 / 塔罗抽牌

用法：
  python divination.py xiaoliu           # 小六壬（当前时间自动起课）
  python divination.py xiaoliu --numbers 3 7 2   # 小六壬（数字起课）
  python divination.py meihua --numbers 37 9     # 梅花易数（数字起卦）
  python divination.py meihua --time              # 梅花易数（时间起卦）
  python divination.py liuyao                    # 六爻（铜钱模拟起卦）
  python divination.py tarot --count 3           # 塔罗牌抽取（默认1张）
"""

import sys
import time
import datetime
import random
import json

# ============================================================
# 基础数据
# ============================================================

# 六十甲子
JIAZI_60 = [
    "甲子","乙丑","丙寅","丁卯","戊辰","己巳","庚午","辛未","壬申","癸酉",
    "甲戌","乙亥","丙子","丁丑","戊寅","己卯","庚辰","辛巳","壬午","癸未",
    "甲申","乙酉","丙戌","丁亥","戊子","己丑","庚寅","辛卯","壬辰","癸巳",
    "甲午","乙未","丙申","丁酉","戊戌","己亥","庚子","辛丑","壬寅","癸卯",
    "甲辰","乙巳","丙午","丁未","戊申","己酉","庚戌","辛亥","壬子","癸丑",
    "甲寅","乙卯","丙辰","丁巳","戊午","己未","庚申","辛酉","壬戌","癸亥",
]

# 十二地支
DIZHI = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
DIZHI_WUXING = {"子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火",
                "午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"}

# 小六壬六宫
XIAOLIU_GONG = ["大安","留连","速喜","赤口","小吉","空亡"]
XIAOLIU_JIXIONG = {"大安":"大吉","留连":"小吉","速喜":"吉","赤口":"凶","小吉":"小吉","空亡":"大凶"}
XIAOLIU_WUXING = {"大安":"木","留连":"土","速喜":"火","赤口":"金","小吉":"水","空亡":"土"}

# 先天八卦（梅花易数用）
BAGUA_NAMES = ["", "乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]
BAGUA_WUXING = {"乾":"金","兑":"金","离":"火","震":"木","巽":"木","坎":"水","艮":"土","坤":"土"}
BAGUA_SYMBOL = {"乾":"☰","兑":"☱","离":"☲","震":"☳","巽":"☴","坎":"☵","艮":"☶","坤":"☷"}
BAGUA_DIRECTION = {"乾":"西北","兑":"西","离":"南","震":"东","巽":"东南","坎":"北","艮":"东北","坤":"西南"}

# 六十四卦名（上卦×8 + 下卦，顺序：乾兑离震巽坎艮坤）
LIUSHI4_NAMES = {
    (1,1):"乾为天",(1,2):"天泽履",(1,3):"天火同人",(1,4):"天雷无妄",
    (1,5):"天风姤",(1,6):"天水讼",(1,7):"天山遁",(1,8):"天地否",
    (2,1):"泽天夬",(2,2):"兑为泽",(2,3):"泽火革",(2,4):"泽雷随",
    (2,5):"泽风大过",(2,6):"泽水困",(2,7):"泽山咸",(2,8):"泽地萃",
    (3,1):"火天大有",(3,2):"火泽睽",(3,3):"离为火",(3,4):"火雷噬嗑",
    (3,5):"火风鼎",(3,6):"火水未济",(3,7):"火山旅",(3,8):"火地晋",
    (4,1):"雷天大壮",(4,2):"雷泽归妹",(4,3):"雷火丰",(4,4):"震为雷",
    (4,5):"雷风恒",(4,6):"雷水解",(4,7):"雷山小过",(4,8):"雷地豫",
    (5,1):"风天小畜",(5,2):"风泽中孚",(5,3):"风火家人",(5,4):"风雷益",
    (5,5):"巽为风",(5,6):"风水涣",(5,7):"风山渐",(5,8):"风地观",
    (6,1):"水天需",(6,2):"水泽节",(6,3):"水火既济",(6,4):"水雷屯",
    (6,5):"水风井",(6,6):"坎为水",(6,7):"水山蹇",(6,8):"水地比",
    (7,1):"山天大畜",(7,2):"山泽损",(7,3):"山火贲",(7,4):"山雷颐",
    (7,5):"山风蛊",(7,6):"山水蒙",(7,7):"艮为山",(7,8):"山地剥",
    (8,1):"地天泰",(8,2):"地泽临",(8,3):"地火明夷",(8,4):"地雷复",
    (8,5):"地风升",(8,6):"地水师",(8,7):"地山谦",(8,8):"坤为地",
}

# 塔罗牌78张
TAROT_MAJOR = [
    "愚者(0)", "魔术师(I)", "女祭司(II)", "女皇(III)", "皇帝(IV)",
    "教皇(V)", "恋人(VI)", "战车(VII)", "力量(VIII)", "隐士(IX)",
    "命运之轮(X)", "正义(XI)", "倒吊人(XII)", "死神(XIII)", "节制(XIV)",
    "恶魔(XV)", "塔(XVI)", "星星(XVII)", "月亮(XVIII)", "太阳(XIX)",
    "审判(XX)", "世界(XXI)"
]
TAROT_SUITS = {
    "权杖": ["权杖Ace","权杖2","权杖3","权杖4","权杖5","权杖6","权杖7",
             "权杖8","权杖9","权杖10","权杖侍从","权杖骑士","权杖王后","权杖国王"],
    "圣杯": ["圣杯Ace","圣杯2","圣杯3","圣杯4","圣杯5","圣杯6","圣杯7",
             "圣杯8","圣杯9","圣杯10","圣杯侍从","圣杯骑士","圣杯王后","圣杯国王"],
    "宝剑": ["宝剑Ace","宝剑2","宝剑3","宝剑4","宝剑5","宝剑6","宝剑7",
             "宝剑8","宝剑9","宝剑10","宝剑侍从","宝剑骑士","宝剑王后","宝剑国王"],
    "星币": ["星币Ace","星币2","星币3","星币4","星币5","星币6","星币7",
             "星币8","星币9","星币10","星币侍从","星币骑士","星币王后","星币国王"],
}
TAROT_ALL = TAROT_MAJOR + TAROT_SUITS["权杖"] + TAROT_SUITS["圣杯"] + \
            TAROT_SUITS["宝剑"] + TAROT_SUITS["星币"]


# ============================================================
# 工具函数
# ============================================================

def get_current_datetime():
    """获取当前时间信息"""
    now = datetime.datetime.now()
    return {
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
        "timestamp": int(now.timestamp()),
        "dizhi_hour": DIZHI[now.hour // 2],  # 时辰地支
        "dizhi_hour_idx": now.hour // 2,     # 时辰序号(0=子,1=丑...)
    }

def wuxing_shengke(a, b):
    """判断五行a与b的关系（a生b / a克b / b生a / b克a / 比和）"""
    sheng = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
    ke = {"木":"土","火":"金","土":"水","金":"木","水":"火"}
    if a == b:
        return "比和"
    elif sheng.get(a) == b:
        return "生"   # a生b
    elif ke.get(a) == b:
        return "克"   # a克b
    elif sheng.get(b) == a:
        return "被生" # b生a
    elif ke.get(b) == a:
        return "被克" # b克a
    return "无关"


# ============================================================
# 小六壬
# ============================================================

def xiaoliu_by_time(month=None, day=None, hour_idx=None):
    """
    小六壬时间起课
    month: 月份(1-12)
    day: 日(1-31)
    hour_idx: 时辰序号(0=子 ~ 11=亥)
    返回：天宫、地宫、人宫
    """
    dt = get_current_datetime()
    if month is None:
        month = dt["month"]
    if day is None:
        day = dt["day"]
    if hour_idx is None:
        hour_idx = dt["dizhi_hour_idx"]

    # 月起大安(0)，顺行
    tian = (month - 1) % 6
    # 以日数继续顺行
    di = (tian + day - 1) % 6
    # 以时辰继续顺行（子=1）
    ren = (di + hour_idx) % 6

    return {
        "method": "时间起课",
        "input": f"{month}月{day}日{DIZHI[hour_idx]}时",
        "tian_gong": XIAOLIU_GONG[tian],
        "di_gong": XIAOLIU_GONG[di],
        "ren_gong": XIAOLIU_GONG[ren],
        "tian_jixiong": XIAOLIU_JIXIONG[XIAOLIU_GONG[tian]],
        "di_jixiong": XIAOLIU_JIXIONG[XIAOLIU_GONG[di]],
        "ren_jixiong": XIAOLIU_JIXIONG[XIAOLIU_GONG[ren]],
        "dizhi_hour": DIZHI[hour_idx],
    }

def xiaoliu_by_numbers(n1, n2, n3, hour_idx=None):
    """
    小六壬数字起课（道传体系）
    算法：参照 xiaoliuren/SKILL.md §3.1
    """
    dt = get_current_datetime()
    if hour_idx is None:
        hour_idx = dt["dizhi_hour_idx"]

    # 数字预处理：0视为10
    def proc(n):
        return 10 if n == 0 else n

    p1, p2, p3 = proc(n1), proc(n2), proc(n3)

    tian = p1 % 6
    di = (tian + p2 - 1) % 6
    ren = (di + p3 - 1) % 6

    return {
        "method": "数字起课",
        "input": f"数字 {n1},{n2},{n3}",
        "tian_gong": XIAOLIU_GONG[tian],
        "di_gong": XIAOLIU_GONG[di],
        "ren_gong": XIAOLIU_GONG[ren],
        "tian_jixiong": XIAOLIU_JIXIONG[XIAOLIU_GONG[tian]],
        "di_jixiong": XIAOLIU_JIXIONG[XIAOLIU_GONG[di]],
        "ren_jixiong": XIAOLIU_JIXIONG[XIAOLIU_GONG[ren]],
        "dizhi_hour": DIZHI[hour_idx],
    }


# ============================================================
# 梅花易数
# ============================================================

def meihua_by_numbers(upper_num, lower_num):
    """
    梅花易数数字起卦
    upper_num: 上卦数（对8取余，0→8）
    lower_num: 下卦数（对8取余，0→8）
    动爻 = (upper_num + lower_num) % 6，0→6
    """
    upper = upper_num % 8 or 8
    lower = lower_num % 8 or 8
    dong_yao = (upper_num + lower_num) % 6 or 6

    upper_name = BAGUA_NAMES[upper]
    lower_name = BAGUA_NAMES[lower]
    gua_name = LIUSHI4_NAMES.get((upper, lower), f"{upper_name}上{lower_name}下")

    # 确定体卦和用卦（动爻在上卦=>下卦为体，动爻在下卦=>上卦为体）
    if dong_yao >= 4:  # 上卦（4~6爻）有动爻
        ti_gua = lower_name
        yong_gua = upper_name
    else:              # 下卦（1~3爻）有动爻
        ti_gua = upper_name
        yong_gua = lower_name

    # 体用生克
    ti_wx = BAGUA_WUXING.get(ti_gua, "")
    yong_wx = BAGUA_WUXING.get(yong_gua, "")
    rel = wuxing_shengke(yong_wx, ti_wx)

    if rel == "生":
        jixiong = "吉（用生体）"
    elif rel == "被生":
        jixiong = "小吉（体生用，略泄）"
    elif rel == "克":
        jixiong = "大凶（用克体）"
    elif rel == "被克":
        jixiong = "吉（体克用）"
    else:
        jixiong = "平（体用比和）"

    # 计算互卦（2-4爻为下互，3-5爻为上互）
    # 简化：互卦内核（爻2,3,4=下互；爻3,4,5=上互）
    # 此处仅标注，详细卦象需查表
    return {
        "method": "数字起卦",
        "input": f"上卦数{upper_num}，下卦数{lower_num}",
        "upper_num": upper_num,
        "lower_num": lower_num,
        "upper_gua": upper_name,
        "lower_gua": lower_name,
        "upper_symbol": BAGUA_SYMBOL.get(upper_name, ""),
        "lower_symbol": BAGUA_SYMBOL.get(lower_name, ""),
        "gua_name": gua_name,
        "dong_yao": dong_yao,
        "ti_gua": ti_gua,
        "ti_wuxing": ti_wx,
        "yong_gua": yong_gua,
        "yong_wuxing": yong_wx,
        "ti_yong_rel": rel,
        "jixiong": jixiong,
    }

def meihua_by_time():
    """梅花易数时间起卦"""
    dt = get_current_datetime()
    # 上卦 = (年+月+日) % 8
    upper_num = dt["year"] + dt["month"] + dt["day"]
    # 下卦 = (年+月+日+时) % 8
    lower_num = upper_num + dt["dizhi_hour_idx"] + 1
    result = meihua_by_numbers(upper_num, lower_num)
    result["method"] = "时间起卦"
    result["input"] = f"{dt['year']}年{dt['month']}月{dt['day']}日{dt['dizhi_hour']}时"
    return result


# ============================================================
# 六爻（模拟铜钱起卦）
# ============================================================

YAO_MAP = {6: ("老阴", "× 变爻→阳"), 7: ("少阳", "— 静爻"),
           8: ("少阴", "-- 静爻"), 9: ("老阳", "○ 变爻→阴")}

def liuyao_cast():
    """
    模拟铜钱起六爻
    每爻三枚铜钱：正面=3，反面=2，三枚之和=6/7/8/9
    使用当前时间戳作为随机种子
    """
    seed = int(time.time() * 1000)
    random.seed(seed)

    yao_values = []
    yao_details = []

    for i in range(6):
        coins = [random.choice([2, 3]) for _ in range(3)]
        total = sum(coins)
        coin_str = "".join(["正" if c == 3 else "反" for c in coins])
        yao_name, yao_desc = YAO_MAP[total]
        yao_values.append(total)
        yao_details.append({
            "yao_pos": i + 1,
            "coins": coin_str,
            "total": total,
            "yao_name": yao_name,
            "desc": yao_desc,
        })

    # 本卦：下卦=下三爻，上卦=上三爻（奇数=阳，偶数=阴，先算本卦卦象）
    def yao_to_bagua_idx(vals):
        """三爻转八卦编号（乾1~坤8）"""
        binary = 0
        for v in reversed(vals):
            binary = binary * 2 + (1 if v in [7, 9] else 0)
        bagua_map = {7: 1, 6: 2, 5: 3, 4: 4, 3: 5, 2: 6, 1: 7, 0: 8}
        return bagua_map.get(binary, 8)

    lower_idx = yao_to_bagua_idx(yao_values[:3])
    upper_idx = yao_to_bagua_idx(yao_values[3:])
    ben_gua = LIUSHI4_NAMES.get((upper_idx, lower_idx), "未知卦")

    # 变卦：老阴→阳，老阳→阴
    def change_yao(v):
        return 7 if v == 6 else (8 if v == 9 else v)

    changed = [change_yao(v) for v in yao_values]
    lower_idx_c = yao_to_bagua_idx(changed[:3])
    upper_idx_c = yao_to_bagua_idx(changed[3:])
    bian_gua = LIUSHI4_NAMES.get((upper_idx_c, lower_idx_c), "未知卦")

    dong_yaos = [i+1 for i, v in enumerate(yao_values) if v in [6, 9]]

    return {
        "method": "铜钱模拟起卦",
        "yao_details": yao_details,
        "yao_values": yao_values,
        "ben_gua": ben_gua,
        "bian_gua": bian_gua if dong_yaos else "无变卦",
        "dong_yaos": dong_yaos,
        "upper_gua": BAGUA_NAMES[upper_idx],
        "lower_gua": BAGUA_NAMES[lower_idx],
    }


# ============================================================
# 塔罗牌
# ============================================================

def tarot_draw(count=1, seed=None):
    """
    抽取塔罗牌
    count: 抽取数量
    seed: 随机种子（默认使用时间戳）
    """
    if seed is None:
        seed = int(time.time() * 1000)
    random.seed(seed)

    indices = random.sample(range(78), min(count, 78))
    results = []
    for idx in indices:
        card = TAROT_ALL[idx]
        orientation = "正位" if (seed + idx) % 2 == 0 else "逆位"
        # 确定花色
        if idx < 22:
            suit = "大阿尔卡纳"
        elif idx < 36:
            suit = "权杖"
        elif idx < 50:
            suit = "圣杯"
        elif idx < 64:
            suit = "宝剑"
        else:
            suit = "星币"
        results.append({
            "index": idx,
            "card": card,
            "suit": suit,
            "orientation": orientation,
        })
    return results


# ============================================================
# 主程序入口
# ============================================================

def print_xiaoliu(result):
    print("\n🔮 小六壬排盘结果")
    print("=" * 40)
    print(f"起课方式：{result['method']}")
    print(f"起课输入：{result['input']}")
    print(f"当前时辰：{result['dizhi_hour']}时")
    print()
    print(f"天宫：{result['tian_gong']}（{result['tian_jixiong']}）")
    print(f"地宫：{result['di_gong']}（{result['di_jixiong']}）")
    print(f"人宫：{result['ren_gong']}（{result['ren_jixiong']}）")
    print()
    print("【综合吉凶】")
    ren = result['ren_gong']
    print(f"人宫为 {ren}，{result['ren_jixiong']}，主事结果{result['ren_jixiong']}。")


def print_meihua(result):
    print("\n🎲 梅花易数起卦结果")
    print("=" * 40)
    print(f"起卦方式：{result['method']}")
    print(f"起卦输入：{result['input']}")
    print()
    print(f"本卦：{result['upper_symbol']}{result['upper_gua']} + {result['lower_symbol']}{result['lower_gua']} = {result['gua_name']}")
    print(f"动爻：第 {result['dong_yao']} 爻")
    print()
    print(f"体卦：{result['ti_gua']}（{result['ti_wuxing']}）")
    print(f"用卦：{result['yong_gua']}（{result['yong_wuxing']}）")
    print(f"体用关系：{result['ti_yong_rel']} → {result['jixiong']}")


def print_liuyao(result):
    print("\n📿 六爻起卦结果")
    print("=" * 40)
    print(f"起卦方式：{result['method']}")
    print()
    print("掷卦过程：")
    for d in reversed(result['yao_details']):
        pos_name = ["初爻","二爻","三爻","四爻","五爻","上爻"][d['yao_pos']-1]
        print(f"  第{d['yao_pos']}掷（{pos_name}）：{d['coins']} → {d['yao_name']} {d['desc']}")
    print()
    print(f"本卦：{result['ben_gua']}")
    print(f"变卦：{result['bian_gua']}")
    if result['dong_yaos']:
        dong_str = "、".join([["初爻","二爻","三爻","四爻","五爻","上爻"][i-1] for i in result['dong_yaos']])
        print(f"动爻：{dong_str}")
    else:
        print("动爻：无（静卦）")


def print_tarot(cards):
    print("\n🃏 塔罗牌抽取结果")
    print("=" * 40)
    positions = ["当前状态", "近期影响", "建议/结果",
                 "深层原因", "外部影响", "过去", "现在", "未来",
                 "位置9", "位置10"]
    for i, card in enumerate(cards):
        pos = positions[i] if i < len(positions) else f"第{i+1}张"
        print(f"[{pos}] {card['suit']} · {card['card']} ({card['orientation']})")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0].lower()

    if cmd == "xiaoliu":
        if "--numbers" in args:
            idx = args.index("--numbers")
            try:
                n1, n2, n3 = int(args[idx+1]), int(args[idx+2]), int(args[idx+3])
                result = xiaoliu_by_numbers(n1, n2, n3)
            except (IndexError, ValueError):
                print("错误：--numbers 需要三个整数参数")
                sys.exit(1)
        else:
            result = xiaoliu_by_time()
        print_xiaoliu(result)
        if "--json" in args:
            print("\nJSON数据：")
            print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "meihua":
        if "--numbers" in args:
            idx = args.index("--numbers")
            try:
                n1, n2 = int(args[idx+1]), int(args[idx+2])
                result = meihua_by_numbers(n1, n2)
            except (IndexError, ValueError):
                print("错误：--numbers 需要两个整数参数")
                sys.exit(1)
        else:
            result = meihua_by_time()
        print_meihua(result)
        if "--json" in args:
            print("\nJSON数据：")
            print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "liuyao":
        result = liuyao_cast()
        print_liuyao(result)
        if "--json" in args:
            print("\nJSON数据：")
            print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "tarot":
        count = 1
        if "--count" in args:
            idx = args.index("--count")
            try:
                count = int(args[idx+1])
            except (IndexError, ValueError):
                count = 1
        cards = tarot_draw(count)
        print_tarot(cards)
        if "--json" in args:
            print("\nJSON数据：")
            print(json.dumps(cards, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令：{cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
