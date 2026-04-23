#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
神课金口诀脚本 - suanshang-jinkou
支持：输入日期时间+事项，自动起四课、论贵神将神、判吉凶

用法：
  python jinkou.py                          # 当前时间起课
  python jinkou.py --time 2026-04-22 14:30  # 指定时间起课
  python jinkou.py --thing 出行              # 指定事项
  python jinkou.py --pos 卯                 # 指定地分方位
  python jinkou.py --num 7                  # 指定数字
  python jinkou.py --json                   # JSON 输出
"""

import sys
import json
import datetime
import random
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============================================================
# 基础数据
# ============================================================

# 天干
TIANGAN = ["", "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
TIANGAN_WUXING = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土",
                  "己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
DIZHI = ["", "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
DIZHI_WUXING = {"子":"水","丑":"土","寅":"木","卯":"木","辰":"土",
                "巳":"火","午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"}

# 贵人表（日干 → 昼贵/夜贵）
GUI_REN = {
    "甲": {"昼":"丑", "夜":"未"},
    "戊": {"昼":"丑", "夜":"未"},
    "庚": {"昼":"丑", "夜":"未"},
    "乙": {"昼":"子", "夜":"申"},
    "己": {"昼":"子", "夜":"申"},
    "丙": {"昼":"亥", "夜":"酉"},
    "丁": {"昼":"亥", "夜":"酉"},
    "壬": {"昼":"巳", "夜":"卯"},
    "癸": {"昼":"巳", "夜":"卯"},
    "辛": {"昼":"午", "夜":"寅"},
}

# 十二贵神
GUI_SHEN = {
    "丑": {"名":"贵人","五行":"土","吉凶":"吉","主事":"贵人相助、逢凶化吉"},
    "巳": {"名":"腾蛇","五行":"火","吉凶":"凶","主事":"惊恐、怪异、邪祟"},
    "午": {"名":"朱雀","五行":"火","吉凶":"凶","主事":"口舌、文书、是非"},
    "卯": {"名":"六合","五行":"木","吉凶":"吉","主事":"和合、婚姻、合作"},
    "辰": {"名":"勾陈","五行":"土","吉凶":"凶","主事":"田土、官司、迟滞"},
    "寅": {"名":"青龙","五行":"木","吉凶":"吉","主事":"喜庆、升迁、婚嫁"},
    "戌": {"名":"天空","五行":"土","吉凶":"凶","主事":"欺诈、虚假、空亡"},
    "申": {"名":"白虎","五行":"金","吉凶":"凶","主事":"凶险、血光、灾祸"},
    "未": {"名":"太常","五行":"土","吉凶":"吉","主事":"饮食、财帛、衣冠"},
    "子": {"名":"玄武","五行":"水","吉凶":"凶","主事":"盗贼、暗昧、欺诈"},
    "酉": {"名":"太阴","五行":"金","吉凶":"吉","主事":"阴私、女性、隐秘"},
    "亥": {"名":"天后","五行":"水","吉凶":"吉","主事":"女性、婚姻、庇护"},
}

# 十二将神
JIANG_SHEN = {
    "寅": {"名":"功曹","五行":"木","主事":"公务、文书、升迁"},
    "卯": {"名":"太冲","五行":"木","主事":"出行、变动、逃亡"},
    "辰": {"名":"天罡","五行":"土","主事":"权柄、争斗、刑狱"},
    "巳": {"名":"太乙","五行":"火","主事":"智慧、谋划、文书"},
    "午": {"名":"胜光","五行":"火","主事":"进取、光明、竞争"},
    "未": {"名":"小吉","五行":"土","主事":"小喜、小财、吉利"},
    "申": {"名":"传送","五行":"金","主事":"传送、消息、行人"},
    "酉": {"名":"从魁","五行":"金","主事":"财帛、收获、金银"},
    "戌": {"名":"河魁","五行":"土","主事":"凶险、阻滞、破败"},
    "亥": {"名":"登明","五行":"水","主事":"智慧、谋略、隐秘"},
    "子": {"名":"神后","五行":"水","主事":"阴私、妇女、隐秘"},
    "丑": {"名":"大吉","五行":"土","主事":"稳重、积累、田宅"},
}

# 月将表（节气中气起）
YUE_JIANG = {
    1: "亥",   # 雨水起亥（登明）
    2: "戌",   # 春分起戌（河魁）
    3: "酉",   # 谷雨起酉（从魁）
    4: "申",   # 小满起申（传送）
    5: "未",   # 夏至起未（小吉）
    6: "午",   # 大暑起午（胜光）
    7: "巳",   # 处暑起巳（太乙）
    8: "辰",   # 秋分起辰（天罡）
    9: "卯",   # 霜降起卯（太冲）
    10: "寅",  # 小雪起寅（功曹）
    11: "丑",  # 冬至起丑（大吉）
    12: "子",  # 大寒起子（神后）
}

# 地分方位
DIFANG = {
    "北": "子", "东北": "丑", "东": "卯", "东南": "辰",
    "南": "午", "西南": "未", "西": "酉", "西北": "戌",
}
DIFANG_DETAIL = {
    "子": "正北", "丑": "东北偏北", "寅": "东北偏东",
    "卯": "正东", "辰": "东南偏东", "巳": "东南偏南",
    "午": "正南", "未": "西南偏南", "申": "西南偏西",
    "酉": "正西", "戌": "西北偏西", "亥": "西北偏北",
}

# 六十甲子（用于人元）
JIAZI = [
    "甲子","乙丑","丙寅","丁卯","戊辰","己巳","庚午","辛未","壬申","癸酉",
    "甲戌","乙亥","丙子","丁丑","戊寅","己卯","庚辰","辛巳","壬午","癸未",
    "甲申","乙酉","丙戌","丁亥","戊子","己丑","庚寅","辛卯","壬辰","癸巳",
    "甲午","乙未","丙申","丁酉","戊戌","己亥","庚子","辛丑","壬寅","癸卯",
    "甲辰","乙巳","丙午","丁未","戊申","己酉","庚戌","辛亥","壬子","癸丑",
    "甲寅","乙卯","丙辰","丁巳","戊午","己未","庚申","辛酉","壬戌","癸亥",
]

# 五行颜色
WUXING_COLOR = {"木":"青","火":"红","土":"黄","金":"白","水":"黑"}

# 吉凶神分类
JI_SHEN = ["贵人","青龙","六合","太常","太阴","天后"]
XIONG_SHEN = ["腾蛇","朱雀","勾陈","天空","白虎","玄武"]

# ============================================================
# 核心计算
# ============================================================

def is_daytime(dt):
    """判断昼夜（卯酉为界）"""
    hour = dt.hour
    return 5 <= hour < 17  # 卯时到酉时为昼

def get_day_gan(dt):
    """获取日干"""
    # 用儒略日
    jd = _to_julian_day(dt)
    # 1900-01-31是甲子日，索引0
    ref_jd = 2415021  # 1900-01-31 的儒略日
    days = jd - ref_jd
    idx = days % 60
    return JIAZI[idx][0]

def _to_julian_day(dt):
    """公历转儒略日"""
    a = (14 - dt.month) // 12
    y = dt.year + 4800 - a
    m = dt.month + 12 * a - 3
    jd = dt.day + (153*m + 2)//5 + 365*y + y//4 - y//100 + y//400 - 32045
    return jd

def get_gui_shengri(gan, is_day):
    """取贵人"""
    info = GUI_REN.get(gan, {"昼":"丑","夜":"未"})
    return info["昼"] if is_day else info["夜"]

def get_yue_jiang(month):
    """取月将"""
    return YUE_JIANG.get(month, "亥")

def get_ren_yuan(gui_zhi, jiang_zhi, di_fen, hour_gan):
    """求人元（天干）"""
    # 人元取法：从贵神、将神、地分中取
    # 简化：用人元与贵神相生或相同
    # 口诀：人元以贵神为根本，贵神生人元则吉
    
    # 简化：用贵神地支+将神地支推算人元
    # 实际上金口诀人元是从四位干支中取
    # 常用：人元 = 时干 或 人元 = 贵神所生之干
    
    # 标准取法：以贵神为主，贵神为阳则从贵神推
    gui_info = GUI_SHEN.get(gui_zhi, {})
    gui_wuxing = gui_info.get("五行","土")
    
    # 人元与贵神同气或相生
    # 简化：用贵神五行生人元
    wuxing_order = ["木","火","土","金","水","木"]
    # 找贵神在人元之前的位置
    # 人元取贵神所生之干，或与贵神同类
    
    # 更简化：用人元与贵神地支的关系
    # 地支藏干表
    ZANGAN = {
        "子":"癸","丑":"己","寅":"甲","卯":"乙","辰":"戊","巳":"丙",
        "午":"丁","未":"己","申":"庚","酉":"辛","戌":"戊","亥":"壬"
    }
    
    # 人元 = 时干（简化法）
    # 传统法：人元由贵神、将神、地分三者关系决定
    # 这里用最简：时干为人元
    return hour_gan

def get_di_fen_from_pos(pos_str):
    """从方位取地分"""
    pos_str = pos_str.strip()
    if pos_str in DIFANG:
        return DIFANG[pos_str]
    if pos_str in DIZHI:
        return pos_str
    # 东南/东北细分
    if pos_str == "东北北": return "丑"
    if pos_str == "东北东": return "寅"
    if pos_str == "东南东": return "辰"
    if pos_str == "东南南": return "巳"
    if pos_str == "西南南": return "未"
    if pos_str == "西南西": return "申"
    if pos_str == "西北西": return "戌"
    if pos_str == "西北北": return "亥"
    return "卯"  # 默认东

def get_di_fen_from_num(num):
    """从数字取地分"""
    idx = (num - 1) % 12
    return DIZHI[idx + 1]

def get_di_fen_from_time(dt):
    """从时辰取地分"""
    return DIZHI[(dt.hour % 12) + 1]

def analyze_jinkou(year, month, day, hour, minute=0, thing=None, pos=None, num=None, dt=None):
    """主函数：分析金口诀"""
    if dt is None:
        dt = datetime.datetime(year, month, day, hour, minute)
    
    # 1. 取基础信息
    day_gan = get_day_gan(dt)
    is_day = is_daytime(dt)
    gui_zhi = get_gui_shengri(day_gan, is_day)
    yue_jiang = get_yue_jiang(month)
    di_fen = pos if pos else (get_di_fen_from_num(num) if num else get_di_fen_from_time(dt))
    
    # 2. 求将神（月将加时）
    # 将神 = 月将 + 时辰，顺时针数到地分
    # 简化：直接用月将（精确需数宫位）
    # 这里用简法：将神 = 月将
    jiang_zhi = yue_jiang
    
    # 3. 求人元
    hour_gan_idx = (hour // 2) % 10  # 时干（近似）
    ren_yuan = TIANGAN[(hour // 2) % 10 + 1]
    
    # 4. 四课排列
    ke = {
        "人元": ren_yuan,
        "贵神": gui_zhi,
        "将神": jiang_zhi,
        "地分": di_fen,
    }
    
    # 5. 获取详细信息
    gui_info = GUI_SHEN.get(gui_zhi, {})
    jiang_info = JIANG_SHEN.get(jiang_zhi, {})
    di_fen_info = JIANG_SHEN.get(di_fen, {})
    
    # 6. 生克论断
    shengke = _analyze_shengke(ke, gui_info, jiang_info, di_fen_info)
    
    # 7. 吉凶判断
    jixiong = _analyze_jixiong(ke, gui_info, jiang_info, shengke)
    
    # 8. 分事断法
    fenxiang = _fenxiang(thing, ke, gui_info, jiang_info, shengke)
    
    # 9. 课体格局
    keti = _analyze_keti(ke)
    
    return {
        "time": dt.strftime("%Y年%m月%d日 %H时%M分"),
        "date_info": {
            "日干": day_gan,
            "昼夜": "昼贵" if is_day else "夜贵",
        },
        "ke": ke,
        "ke_detail": {
            "人元": {"干": ren_yuan, "五行": TIANGAN_WUXING.get(ren_yuan,"")},
            "贵神": gui_info,
            "将神": jiang_info,
            "地分": {"支": di_fen, "方位": DIFANG_DETAIL.get(di_fen,""), 
                     "五行": DIZHI_WUXING.get(di_fen,""),
                     "名": JIANG_SHEN.get(di_fen,{}).get("名","")},
        },
        "shengke": shengke,
        "jixiong": jixiong,
        "keti": keti,
        "fenxiang": fenxiang,
        "tips": _generate_tips(ke, gui_info, jiang_info, shengke, jixiong),
    }

def _analyze_shengke(ke, gui_info, jiang_info, di_fen_info):
    """分析生克关系"""
    result = {}
    
    # 人元与贵神
    ren_wx = TIANGAN_WUXING.get(ke["人元"], "")
    gui_wx = gui_info.get("五行", "土")
    
    # 主客论
    result["主客"] = _wuxing_relation(gui_wx, ren_wx, "人元", "贵神")
    
    # 贵神与将神
    jiang_wx = jiang_info.get("五行", "土")
    result["贵神将神"] = _wuxing_relation(gui_wx, jiang_wx, "贵神", "将神")
    
    # 将神与地分
    di_wx = di_fen_info.get("五行", DIZHI_WUXING.get(ke["地分"], ""))
    result["将神地分"] = _wuxing_relation(jiang_wx, di_wx, "将神", "地分")
    
    # 上下关系（人元→贵神→将神→地分）
    # 上克下：事难成；下克上：反有声；上生下：贵人助；下生上：自经营
    # 简化：看人元与地分
    ren_yuan = ke["人元"]
    di_fen = ke["地分"]
    
    # 人元克地分（客克主）
    ren_gan_idx = TIANGAN.index(ren_yuan) if ren_yuan in TIANGAN else 0
    di_zhi_idx = DIZHI.index(di_fen) if di_fen in DIZHI else 0
    
    # 五行生克
    sheng = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
    ke_wx_rel = {"木":"土","土":"水","水":"火","火":"金","金":"木"}
    
    ren_wx = TIANGAN_WUXING.get(ren_yuan, "")
    di_zhi_wx = DIZHI_WUXING.get(di_fen, "")
    
    if sheng.get(ren_wx) == di_zhi_wx:
        result["主客总论"] = "人元生地分（下受上生）：自力更生，辛苦经营"
    elif ke_wx_rel.get(ren_wx) == di_zhi_wx:
        result["主客总论"] = "人元克地分（客克主）：主动出击，反客为主"
    elif ren_wx == di_zhi_wx:
        result["主客总论"] = "人元地分比和：势均力敌，平稳推进"
    else:
        result["主客总论"] = "人元生地分：贵人相助，事情有转机"
    
    return result

def _wuxing_relation(wx1, wx2, name1, name2):
    """判断五行生克关系"""
    sheng = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
    ke_wx = {"木":"土","土":"水","水":"火","火":"金","金":"木"}
    
    if wx1 == wx2:
        return f"{name1}与{name2}比和：平稳"
    elif sheng.get(wx1) == wx2:
        return f"{name1}生{name2}：上生下，贵人相助"
    elif ke_wx.get(wx1) == wx2:
        return f"{name1}克{name2}：上克下，阻力较大"
    else:
        return f"{name1}被{name2}生：下生上，自力更生"

def _analyze_jixiong(ke, gui_info, jiang_info, shengke):
    """判断吉凶"""
    result = {}
    
    gui_name = gui_info.get("名", "")
    jiang_name = jiang_info.get("名", "")
    
    # 贵神吉凶
    if gui_name in JI_SHEN:
        result["贵神"] = f"吉神【{gui_name}】：{gui_info.get('主事','')} → 大吉"
    elif gui_name in XIONG_SHEN:
        result["贵神"] = f"凶神【{gui_name}】：{gui_info.get('主事','')} → 需谨慎"
    else:
        result["贵神"] = f"【{gui_name}】：{gui_info.get('主事','')}"
    
    # 将神吉凶
    result["将神"] = f"【{jiang_name}】：{jiang_info.get('主事','')}"
    
    # 综合
    if gui_name in JI_SHEN and jiang_name in ["小吉","从魁","功曹","太冲"]:
        result["综合"] = "吉象：事情顺利，可积极行动"
    elif gui_name in XIONG_SHEN:
        if gui_name in ["白虎","玄武"]:
            result["综合"] = "凶象：事情有阻滞或风险，需谨慎"
        else:
            result["综合"] = "中性带凶：口舌是非或迟滞，不宜冒进"
    else:
        result["综合"] = "中性象：平稳为主，相机而动"
    
    return result

def _analyze_keti(ke):
    """分析课体格局"""
    result = []
    
    # 六合
    liuhe_pairs = [("子","丑"),("寅","亥"),("卯","戌"),("辰","酉"),("巳","申"),("午","未")]
    zhi_list = [ke["贵神"], ke["将神"], ke["地分"]]
    
    # 检查三合
    sanhe = [("申","子","辰"),("巳","酉","丑"),("寅","午","戌"),("亥","卯","未")]
    found_sanhe = None
    for sg in sanhe:
        count = sum(1 for z in zhi_list if z in sg)
        if count >= 3:
            found_sanhe = sg
            break
    
    if found_sanhe:
        names = {"申":"金","子":"水","辰":"土","巳":"火","酉":"金","丑":"土",
                 "寅":"木","午":"火","戌":"土","亥":"水","卯":"木","未":"土"}
        element = names.get(found_sanhe[0], "")
        result.append(f"三合局：{'·'.join(found_sanhe)}（{element}局）→ 局旺事成")
    
    # 检查六冲
    chong_pairs = [("子","午"),("丑","未"),("寅","申"),("卯","酉"),("辰","戌"),("巳","亥")]
    for cp in chong_pairs:
        if ke["贵神"] in cp and ke["地分"] in cp:
            result.append(f"六冲：贵神{ke['贵神']}冲地分{ke['地分']} → 动荡、变动、分离")
            break
    
    # 检查三刑
    sanxing = [("寅","巳","申"),("丑","戌","未"),("子","卯"),("辰","午","酉","亥")]
    count_xing = sum(1 for z in zhi_list if z in sanxing[0])
    if count_xing >= 3:
        result.append("三刑：寅巳申无恩之刑 → 官非、争执")
    
    if not result:
        result.append("普通课：事情平稳发展")
    
    return result

def _fenxiang(thing, ke, gui_info, jiang_info, shengke):
    """分事断法"""
    gui_name = gui_info.get("名", "")
    jiang_name = jiang_info.get("名", "")
    
    result = {}
    
    # 根据事项关键词判断
    if thing is None:
        result["综合"] = "事情有转机，贵神相助，可积极行动"
        return result
    
    thing = thing.strip()
    
    # 求财
    if any(k in thing for k in ["求财","生意","投资","赚钱","财"]):
        if gui_name in ["青龙","太常"]:
            result["求财"] = "大吉：青龙/太常临贵神，财帛进门，收益可期"
        elif gui_name in ["白虎","玄武"]:
            result["求财"] = "凶：有破财风险，慎防小人，建议保守"
        elif jiang_name in ["从魁","小吉"]:
            result["求财"] = "小吉：从魁/小吉将神，财帛有收获，辛苦可得"
        else:
            result["求财"] = "平：财运一般，需主动争取，稳中求进"
    
    # 婚姻
    if any(k in thing for k in ["婚","姻","感情","恋爱","分手"]):
        if gui_name in ["六合","天后"]:
            result["婚姻"] = "大吉：六合/天后临贵神，感情和合，婚事可成"
        elif gui_name in ["腾蛇","玄武"]:
            result["婚姻"] = "凶：感情有变数，防口舌或第三者介入"
        else:
            result["婚姻"] = "平：感情平稳推进，需要耐心经营"
    
    # 出行
    if any(k in thing for k in ["出行","旅游","出门","动身"]):
        if gui_name in ["青龙","六合"]:
            result["出行"] = "吉：出行顺利，青龙/六合临贵神，一路平安"
        elif gui_name in ["白虎","天罡"]:
            result["出行"] = "凶：有阻滞或风险，白虎临贵神，不宜出行"
        else:
            result["出行"] = "平：出行顺利，路上需注意安全"
    
    # 官讼
    if any(k in thing for k in ["官讼","官司","诉讼","纠纷"]):
        if gui_name in ["勾陈","白虎"]:
            result["官讼"] = "凶：勾陈/白虎临贵神，官司不利，易败诉"
        elif gui_name in ["青龙","贵人"]:
            result["官讼"] = "吉：青龙/贵人临贵神，官司有贵人相助"
        else:
            result["官讼"] = "平：官司胶着，需要坚持，耐心应对"
    
    # 疾病
    if any(k in thing for k in ["病","健康","身体","医疗"]):
        if gui_name in ["白虎","玄武"]:
            result["疾病"] = "凶：白虎/玄武临贵神，需及时就医，不可拖延"
        elif gui_name in ["贵人","青龙"]:
            result["疾病"] = "吉：贵人/青龙临贵神，遇良医，可化险为夷"
        else:
            result["疾病"] = "平：身体有小恙，调养即可恢复"
    
    # 学业
    if any(k in thing for k in ["学业","考试","学习","升学"]):
        if gui_name in ["朱雀","太乙"]:
            result["学业"] = "吉：朱雀/太乙临贵神，文书之喜，考试顺利"
        else:
            result["学业"] = "平：学业平稳，需努力方可进步"
    
    if not result:
        result["综合"] = "事情有转机，贵神相助，可积极行动"
    
    return result

def _generate_tips(ke, gui_info, jiang_info, shengke, jixiong):
    """生成建议"""
    gui_name = gui_info.get("名", "")
    jiang_name = jiang_info.get("名", "")
    
    tips = []
    
    if gui_name in JI_SHEN:
        tips.append("贵神为吉神，贵人相助，事情可成")
    elif gui_name in XIONG_SHEN:
        tips.append("贵神为凶神，凡事谨慎，不宜冒进")
    
    if jiang_name in ["从魁","小吉","太冲","功曹"]:
        tips.append("将神吉利，事情进展顺利")
    elif jiang_name in ["河魁","腾蛇"]:
        tips.append("将神带凶，需防阻滞或意外")
    
    # 根据生克
    if "贵人相助" in shengke.get("主客总论",""):
        tips.append("人元生地分：有贵人扶持，借力而行")
    elif "反客为主" in shengke.get("主客总论",""):
        tips.append("人元克地分：主动出击，可掌控局面")
    
    if not tips:
        tips.append("事情平稳，稳中求进，相机而动")
    
    return tips

# ============================================================
# 输出格式
# ============================================================

def print_jinkou(analysis, json_mode=False):
    """格式化输出"""
    if json_mode:
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
        return
    
    a = analysis
    ke = a["ke"]
    ke_d = a["ke_detail"]
    sk = a["shengke"]
    jx = a["jixiong"]
    kt = a["keti"]
    fx = a["fenxiang"]
    tips = a["tips"]
    
    output = []
    output.append("")
    output.append("=" * 48)
    output.append(f"  神课金口诀 · {a['time']}")
    output.append("=" * 48)
    output.append("")
    
    # 四课
    output.append("┌────────┬────────┬────────┬────────┐")
    output.append(f"│  人元  │  贵神  │  将神  │  地分  │")
    output.append("├────────┼────────┼────────┼────────┤")
    output.append(f"│  {ke['人元']}   │  {ke['贵神']}   │  {ke['将神']}   │  {ke['地分']}   │")
    output.append(f"│  {ke_d['贵神']['名']}  │  {ke_d['将神']['名']}  │  {ke_d['地分']['名']}  │")
    output.append("└────────┴────────┴────────┴────────┘")
    
    output.append("")
    output.append(f"【日干】{a['date_info']['日干']}  【昼夜】{a['date_info']['昼夜']}")
    output.append(f"【方位】{ke_d['地分']['方位']}（{ke_d['地分']['支']}宫）")
    
    output.append("")
    output.append("【生克论断】")
    output.append(f"  ▸ 贵神将神：{sk.get('贵神将神','')}")
    output.append(f"  ▸ 将神地分：{sk.get('将神地分','')}")
    output.append(f"  ▸ 主客总论：{sk.get('主客总论','')}")
    
    output.append("")
    output.append("【课体格局】")
    for t in kt:
        output.append(f"  ▸ {t}")
    
    output.append("")
    output.append("【吉凶判断】")
    output.append(f"  ▸ 贵神：{jx.get('贵神','')}")
    output.append(f"  ▸ 将神：{jx.get('将神','')}")
    output.append(f"  ▸ 综合：{jx.get('综合','')}")
    
    output.append("")
    output.append("【分事断法】")
    for k, v in fx.items():
        output.append(f"  ▸ {k}：{v}")
    
    output.append("")
    output.append("【行动建议】")
    for i, t in enumerate(tips, 1):
        output.append(f"  {i}. {t}")
    
    output.append("")
    output.append("=" * 48)
    output.append("")
    
    print("\n".join(output))

# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    args = sys.argv[1:]
    
    if len(args) == 0 or "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)
    
    json_mode = "--json" in args
    dt_now = datetime.datetime.now()
    
    thing = None
    pos = None
    num = None
    year, month, day, hour = dt_now.year, dt_now.month, dt_now.day, dt_now.hour
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--time" and i + 2 < len(args):
            try:
                date_str = args[i+1]
                time_str = args[i+2]
                dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                year, month, day, hour = dt.year, dt.month, dt.day, dt.hour
                i += 3
                continue
            except:
                i += 1
                continue
        elif arg == "--thing" and i + 1 < len(args):
            thing = args[i+1]
            i += 2
            continue
        elif arg == "--pos" and i + 1 < len(args):
            pos = args[i+1]
            i += 2
            continue
        elif arg == "--num" and i + 1 < len(args):
            try:
                num = int(args[i+1])
            except:
                pass
            i += 2
            continue
        else:
            i += 1
    
    result = analyze_jinkou(year, month, day, hour, thing=thing, pos=pos, num=num)
    print_jinkou(result, json_mode=json_mode)
