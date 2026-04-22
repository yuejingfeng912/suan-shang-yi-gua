#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黄历生成脚本 - shusu-divination
根据日期生成完整的黄历信息（干支、建除十二神、宜忌、吉时、神煞等）

用法：
  python calendar.py                          # 今日黄历
  python calendar.py --date 2026-05-01        # 指定日期
  python calendar.py --week                   # 一周黄历
  python calendar.py --month                  # 一月黄历
  python calendar.py --json                   # JSON格式输出
"""

import sys
import datetime
import json
import math

# ============================================================
# 基础数据
# ============================================================

TIANGAN = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
DIZHI = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
JIAZI_60 = [
    "甲子","乙丑","丙寅","丁卯","戊辰","己巳","庚午","辛未","壬申","癸酉",
    "甲戌","乙亥","丙子","丁丑","戊寅","己卯","庚辰","辛巳","壬午","癸未",
    "甲申","乙酉","丙戌","丁亥","戊子","己丑","庚寅","辛卯","壬辰","癸巳",
    "甲午","乙未","丙申","丁酉","戊戌","己亥","庚子","辛丑","壬寅","癸卯",
    "甲辰","乙巳","丙午","丁未","戊申","己酉","庚戌","辛亥","壬子","癸丑",
    "甲寅","乙卯","丙辰","丁巳","戊午","己未","庚申","辛酉","壬戌","癸亥",
]

# 天干五行
TIANGAN_WUXING = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土",
                  "庚":"金","辛":"金","壬":"水","癸":"水"}

# 地支五行
DIZHI_WUXING = {"子":"水","丑":"土","寅":"木","卯":"木","辰":"土","巳":"火",
                "午":"火","未":"土","申":"金","酉":"金","戌":"土","亥":"水"}

# 建除十二神
JIANCHU_12 = ["建","除","满","平","定","执","破","危","成","收","开","闭"]

# 建除十二神宜忌
JIANCHU_YI = {
    "建": ["出行","求职","祈福","动土","开光"],
    "除": ["除旧","治病","解除","扫舍"],
    "满": ["婚嫁","入宅","祭祀","祈福"],
    "平": ["祭祀","祈福","修造","动土","开市"],
    "定": ["嫁娶","祭祀","订盟","纳采"],
    "执": ["祭祀","纳财","立券"],
    "破": ["破屋坏垣","拆屋"],
    "危": ["登高","祈福","安床"],
    "成": ["百事皆宜","开市","交易","立券","纳财","嫁娶","出行","动土"],
    "收": ["纳财","收债","种殖"],
    "开": ["出行","开业","开市","嫁娶","交易"],
    "闭": ["安葬","修造"],
}

JIANCHU_JI = {
    "建": ["嫁娶","安葬","动土(修造)"],
    "除": ["嫁娶","建造","上梁"],
    "满": ["上梁","安葬"],
    "平": [],
    "定": ["远行","上任","诉讼"],
    "执": ["嫁娶","出行","搬迁"],
    "破": ["百事不宜","嫁娶","出行","开业","安葬"],
    "危": ["出行","嫁娶","动土"],
    "成": ["诉讼","词讼"],
    "收": ["开市","出行","嫁娶","安葬"],
    "开": ["安葬","埋葬"],
    "闭": ["嫁娶","出行","开市","动土"],
}

# 每日冲煞
CHONG_SHA = {
    "子":("午","南"),"丑":("未","东"),"寅":("申","北"),"卯":("酉","西"),
    "辰":("戌","南"),"巳":("亥","东"),"午":("子","北"),"未":("丑","西"),
    "申":("寅","南"),"酉":("卯","东"),"戌":("辰","北"),"亥":("巳","西"),
}

# 纳音五行
NAYIN = {
    "甲子":"海中金","乙丑":"海中金","丙寅":"炉中火","丁卯":"炉中火",
    "戊辰":"大林木","己巳":"大林木","庚午":"路旁土","辛未":"路旁土",
    "壬申":"剑锋金","癸酉":"剑锋金","甲戌":"山头火","乙亥":"山头火",
    "丙子":"涧下水","丁丑":"涧下水","戊寅":"城头土","己卯":"城头土",
    "庚辰":"白蜡金","辛巳":"白蜡金","壬午":"杨柳木","癸未":"杨柳木",
    "甲申":"泉中水","乙酉":"泉中水","丙戌":"屋上土","丁亥":"屋上土",
    "戊子":"霹雳火","己丑":"霹雳火","庚寅":"松柏木","辛卯":"松柏木",
    "壬辰":"长流水","癸巳":"长流水","甲午":"砂中金","乙未":"砂中金",
    "丙申":"山下火","丁酉":"山下火","戊戌":"平地木","己亥":"平地木",
    "庚子":"壁上土","辛丑":"壁上土","壬寅":"金箔金","癸卯":"金箔金",
    "甲辰":"覆灯火","乙巳":"覆灯火","丙午":"天河水","丁未":"天河水",
    "戊申":"大驿土","己酉":"大驿土","庚戌":"钗钏金","辛亥":"钗钏金",
    "壬子":"桑柘木","癸丑":"桑柘木","甲寅":"大溪水","乙卯":"大溪水",
    "丙辰":"沙中土","丁巳":"沙中土","戊午":"天上火","己未":"天上火",
    "庚申":"石榴木","辛酉":"石榴木","壬戌":"大海水","癸亥":"大海水",
}

# 吉时（按日干）
JISHI_MAP = {
    "甲":"丑 未","乙":"子 申","丙":"亥 酉","丁":"亥 酉",
    "戊":"丑 未","己":"子 申","庚":"丑 未","辛":"午 寅",
    "壬":"卯 巳","癸":"卯 巳",
}

# 二十八宿（简化）
STAR28 = ["角","亢","氐","房","心","尾","箕",
          "斗","牛","女","虚","危","室","壁",
          "奎","娄","胃","昴","毕","觜","参",
          "井","鬼","柳","星","张","翼","轸"]

# 每月天德方位
TIANDE = {1:"丁",2:"申",3:"壬",4:"辛",5:"亥",6:"甲",
          7:"癸",8:"寅",9:"丙",10:"乙",11:"巳",12:"庚"}

YUEDE = {1:"壬",2:"庚",3:"丙",4:"甲",5:"壬",6:"庚",
         7:"丙",8:"甲",9:"壬",10:"庚",11:"丙",12:"甲"}

# 天干阴阳
TIANGAN_YINYANG = {"甲":"阳","乙":"阴","丙":"阳","丁":"阴","戊":"阳",
                   "己":"阴","庚":"阳","辛":"阴","壬":"阳","癸":"阴"}


# ============================================================
# 计算函数
# ============================================================

def days_between(d1, d2):
    """计算两个日期之间的天数"""
    return (d2 - d1).days

def get_jiazi_index(year, month, day):
    """
    获取日柱六十甲子序号
    以1900年1月1日（庚子日，序号36）为基准
    """
    base = datetime.date(1900, 1, 1)  # 庚子日，JIAZI_60[36]
    target = datetime.date(year, month, day)
    delta = days_between(base, target)
    return (36 + delta) % 60

def get_year_ganzhi(year):
    """获取年干支（以立春2月4日为界）"""
    # 简化：以公历1-2月归上一年
    return (year - 4) % 60

def get_month_ganzhi(year_gz_idx, month):
    """获取月干支"""
    # 年干决定正月干
    year_gan = year_gz_idx % 10
    # 五虎遁：甲己→丙寅, 乙庚→戊寅, 丙辛→庚寅, 丁壬→壬寅, 戊癸→甲寅
    start_gan = [2, 4, 6, 8, 0][year_gan % 5]  # 丙=2,戊=4,庚=6,壬=8,甲=0
    # 正月=寅(2), 干从start_gan开始，支从寅(2)开始
    gan_idx = (start_gan + month - 1) % 10
    zhi_idx = (2 + month - 1) % 12  # 正月=寅
    return gan_idx * 6 + zhi_idx // 2  # 简化映射

def get_hour_ganzhi(day_gz_idx, hour_idx):
    """获取时干支（hour_idx: 0=子, 1=丑...）"""
    # 五鼠遁日上起时
    day_gan = day_gz_idx % 10
    start_gan = [0, 2, 4, 6, 8][day_gan % 5]  # 甲己→甲, 乙庚→丙, ...
    gan_idx = (start_gan + hour_idx) % 10
    zhi_idx = hour_idx % 12
    return f"{TIANGAN[gan_idx]}{DIZHI[zhi_idx]}"

def get_jianchu(month, day):
    """
    获取建除十二神
    建除值日从月建开始，每月初一建，
    即：建 = 月建所在地支，每日顺序递进
    """
    # 月建地支序号（正月=寅=2, 二月=卯=3...）
    jian_zhi = (month + 1) % 12  # 正月(1)→寅(2)
    # 初一为建，之后顺序
    offset = (day - 1) % 12
    jianchu_idx = (offset) % 12
    return JIANCHU_12[jianchu_idx]

def get_jishen(month, day):
    """获取当日主要吉神（简化算法）"""
    gods = []
    # 天德
    td = TIANDE.get(month, "")
    if td:
        gods.append(f"天德（{td}）")
    # 月德
    yd = YUEDE.get(month, "")
    if yd:
        gods.append(f"月德（{yd}）")
    # 三合日（简化判断）
    day_zhi_idx = (get_jiazi_index(datetime.date.today().year, month, day) % 12)
    # 天喜（日支与月建六合）
    liu_he = {2:0, 3:11, 4:8, 5:9, 6:10, 7:5, 8:6, 9:7, 10:4, 11:3, 0:1, 1:2}
    # 月建=寅(2),六合=亥(11)
    yue_jian = (month + 1) % 12
    if liu_he.get(day_zhi_idx) == yue_jian or day_zhi_idx == liu_he.get(yue_jian, -1):
        gods.append("天喜")
    return gods if gods else ["无特列吉神"]

def get_xiongsha(month, day):
    """获取当日主要凶煞（简化算法）"""
    evils = []
    # 月破（日支冲月建）
    yue_jian = (month + 1) % 12
    day_zhi_idx = (get_jiazi_index(datetime.date.today().year, month, day) % 12)
    chong_map = {0:6,1:7,2:8,3:9,4:10,5:11,6:0,7:1,8:2,9:3,10:4,11:5}
    if chong_map.get(yue_jian) == day_zhi_idx:
        evils.append("月破")
    return evils if evils else ["无特列凶煞"]

def get_28star(month, day):
    """获取二十八宿（简化，每4天换一宿）"""
    idx = (month * 31 + day) % 28
    return STAR28[idx]


# ============================================================
# 黄历生成主函数
# ============================================================

def generate_calendar(year, month, day):
    """生成单日完整黄历"""
    date_obj = datetime.date(year, month, day)

    # 日柱干支
    day_gz_idx = get_jiazi_index(year, month, day)
    day_gz = JIAZI_60[day_gz_idx]
    day_gan = TIANGAN[day_gz_idx % 10]
    day_zhi = DIZHI[day_gz_idx % 12]

    # 年柱干支
    year_gz_idx = get_year_ganzhi(year)
    year_gz = JIAZI_60[year_gz_idx]

    # 纳音
    nayin = NAYIN.get(day_gz, "未知")

    # 冲煞
    chong_zhi, sha_fang = CHONG_SHA.get(day_zhi, ("未知", "未知"))

    # 建除值神
    jianchu = get_jianchu(month, day)

    # 宜忌
    yi_list = JIANCHU_YI.get(jianchu, [])
    ji_list = JIANCHU_JI.get(jianchu, [])

    # 吉时
    jishi = JISHI_MAP.get(day_gan, "")

    # 吉神凶煞
    jishen = get_jishen(month, day)
    xiongsha = get_xiongsha(month, day)

    # 二十八宿
    star28 = get_28star(month, day)

    # 五行
    day_wuxing = f"{TIANGAN_WUXING.get(day_gan,'')} {DIZHI_WUXING.get(day_zhi,'')}"

    # 星期
    weekday = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"][date_obj.weekday()]

    result = {
        "date": f"{year}年{month:02d}月{day:02d}日",
        "weekday": weekday,
        "year_gz": year_gz,
        "day_gz": day_gz,
        "day_gan": day_gan,
        "day_zhi": day_zhi,
        "nayin": nayin,
        "day_wuxing": day_wuxing,
        "chong": f"冲{chong_zhi}",
        "sha": f"煞{sha_fang}",
        "jianchu": jianchu,
        "yi": yi_list,
        "ji": ji_list,
        "jishen": jishen,
        "xiongsha": xiongsha,
        "jishi": jishi,
        "star28": star28,
        "tiangan_yinyang": TIANGAN_YINYANG.get(day_gan, ""),
    }

    return result


def print_calendar(cal):
    """格式化输出黄历"""
    print(f"\n📅 【{cal['date']} 黄历】  {cal['weekday']}")
    print("=" * 45)
    print(f"年柱：{cal['year_gz']}    日柱：{cal['day_gz']}    纳音：{cal['nayin']}")
    print(f"日干支五行：{cal['day_wuxing']}    {cal['chong']}    {cal['sha']}")
    print(f"建除值日：{cal['jianchu']}    二十八宿：{cal['star28']}宿")
    print()

    yi_str = "、".join(cal['yi']) if cal['yi'] else "无"
    ji_str = "、".join(cal['ji']) if cal['ji'] else "无"
    print(f"【今日宜】")
    print(f"  ✅ {yi_str}")
    print()
    print(f"【今日忌】")
    print(f"  ❌ {ji_str}")
    print()

    js_str = "、".join(cal['jishen'])
    xs_str = "、".join(cal['xiongsha'])
    print(f"【神煞】")
    print(f"  吉神：{js_str}")
    print(f"  凶煞：{xs_str}")
    print()

    print(f"【吉时】")
    if cal['jishi']:
        hours = cal['jishi'].split()
        for h in hours:
            idx = DIZHI.index(h) if h in DIZHI else -1
            if idx >= 0:
                time_range = f"{23 if idx==0 else idx*2-1:02d}:00-{(idx*2+1)%24:02d}:00" if idx == 0 else f"{idx*2-1:02d}:00-{idx*2+1:02d}:00"
                print(f"  🟢 {h}时（{time_range}）")
    else:
        print(f"  （查无特别吉时）")


def print_week(calendars):
    """输出一周黄历"""
    print("\n📅 一周黄历概览")
    print("=" * 70)
    print(f"{'日期':<12}{'星期':<6}{'日柱':<6}{'建除':<4}{'宜(摘要)':<20}{'忌(摘要)':<15}")
    print("-" * 70)
    for cal in calendars:
        yi_summary = "、".join(cal['yi'][:3]) if cal['yi'] else "无"
        ji_summary = "、".join(cal['ji'][:2]) if cal['ji'] else "无"
        print(f"{cal['date']:<12}{cal['weekday']:<6}{cal['day_gz']:<6}{cal['jianchu']:<4}{yi_summary:<20}{ji_summary:<15}")
    print("=" * 70)


def main():
    args = sys.argv[1:]
    json_mode = "--json" in args
    week_mode = "--week" in args
    month_mode = "--month" in args

    # 解析日期参数
    date_str = None
    if "--date" in args:
        idx = args.index("--date")
        try:
            date_str = args[idx + 1]
        except IndexError:
            pass

    if date_str:
        parts = date_str.split("-")
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    else:
        today = datetime.date.today()
        year, month, day = today.year, today.month, today.day

    if week_mode:
        # 一周黄历
        base = datetime.date(year, month, day)
        calendars = []
        for i in range(7):
            d = base + datetime.timedelta(days=i)
            cal = generate_calendar(d.year, d.month, d.day)
            calendars.append(cal)
        if json_mode:
            print(json.dumps(calendars, ensure_ascii=False, indent=2))
        else:
            print_week(calendars)

    elif month_mode:
        # 一月黄历
        base = datetime.date(year, month, 1)
        calendars = []
        d = base
        while d.month == month:
            cal = generate_calendar(d.year, d.month, d.day)
            calendars.append(cal)
            d += datetime.timedelta(days=1)
        if json_mode:
            print(json.dumps(calendars, ensure_ascii=False, indent=2))
        else:
            print_week(calendars)

    else:
        # 单日黄历
        cal = generate_calendar(year, month, day)
        if json_mode:
            print(json.dumps(cal, ensure_ascii=False, indent=2))
        else:
            print_calendar(cal)


if __name__ == "__main__":
    main()
