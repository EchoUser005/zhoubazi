from datetime import datetime, timedelta
import sxtwl
import requests
from functools import lru_cache

"""
日历计算工具

1. 公历转农历
2. 农历转公历
3. 获取今日干支历 (如：乙巳年壬午月甲申日)
4. 地理位置查经纬度（使用高德地图API，带缓存）
5. 真太阳时计算获得校准后生辰
6. 未来日历生成 (获取近n周干支历，假设今天是6月9日周一，则获取6月9日-6月22日干支历)
7. 四柱排盘
8. 大运信息计算工具
    -  8.24 修正大运映射不全bug
"""


class BaziEngine:
    def __init__(self):
        """初始化引擎"""
        self.TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        self.amap_key = "a33717c5f9e32f75631a1a14011554ff"

    # 1. 公历转农历
    def convert_solar_to_lunar(self, solar_date: datetime) -> dict:
        day = sxtwl.fromSolar(solar_date.year, solar_date.month, solar_date.day)

        # 农历月名称 (修正版本)
        lunar_month_names = ['正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '冬月',
                             '腊月']
        lunar_month_name = ("闰" if day.isLunarLeap() else "") + lunar_month_names[day.getLunarMonth() - 1]

        # 农历日名称
        lunar_day_names = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                           '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                           '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
        lunar_day_name = lunar_day_names[day.getLunarDay() - 1]

        # 时辰
        hour_index = (solar_date.hour + 1) // 2 % 12
        hour_zhi = self.DI_ZHI[hour_index]

        return {
            "year": day.getLunarYear(),
            "month": day.getLunarMonth(),
            "day": day.getLunarDay(),
            "is_leap": day.isLunarLeap(),
            "lunar_display": f"{day.getLunarYear()}年{lunar_month_name}{lunar_day_name} {hour_zhi}时"
        }

    # 2. 农历转公历
    def convert_lunar_to_solar(self, lunar_year: int, lunar_month: int, lunar_day: int,
                               is_leap: bool = False) -> datetime:
        day = sxtwl.fromLunar(lunar_year, lunar_month, lunar_day, is_leap)
        return datetime(day.getSolarYear(), day.getSolarMonth(), day.getSolarDay())

    # 3. 干支查询
    def get_ganzhi_info(self, solar_date: datetime) -> dict:
        day = sxtwl.fromSolar(solar_date.year, solar_date.month, solar_date.day)

        year_gz = day.getYearGZ()
        year_gan = self.TIAN_GAN[year_gz.tg]
        year_zhi = self.DI_ZHI[year_gz.dz]

        month_gz = day.getMonthGZ()
        month_gan = self.TIAN_GAN[month_gz.tg]
        month_zhi = self.DI_ZHI[month_gz.dz]

        day_gz = day.getDayGZ()
        day_gan = self.TIAN_GAN[day_gz.tg]
        day_zhi = self.DI_ZHI[day_gz.dz]

        return {
            "year_ganzhi": f"{year_gan}{year_zhi}",
            "month_ganzhi": f"{month_gan}{month_zhi}",
            "day_ganzhi": f"{day_gan}{day_zhi}",
            "year_gan": year_gan,
            "year_zhi": year_zhi,
            "month_gan": month_gan,
            "month_zhi": month_zhi,
            "day_gan": day_gan,
            "day_zhi": day_zhi
        }

    # 4. 地理位置查经纬度（使用高德地图API，带LRU缓存）
    @lru_cache(maxsize=500)
    def get_location_info(self, city_name: str) -> tuple[float, float]:

        try:
            url = "https://restapi.amap.com/v3/geocode/geo"
            params = {
                "address": city_name,
                "key": self.amap_key
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()

            if data.get("status") == "1" and data.get("geocodes"):
                location = data["geocodes"][0]["location"]
                lng, lat = location.split(",")
                return float(lng), float(lat)
            else:
                error_msg = data.get("info", "未知错误")
                raise ValueError(f"无法找到地理位置 '{city_name}': {error_msg}")

        except requests.RequestException as e:
            raise ValueError(f"地理位置查询网络错误: {e}")
        except Exception as e:
            raise ValueError(f"地理位置查询失败: {e}")

    # 5. 真太阳时计算
    def get_true_solar_time(self, solar_date: datetime, longitude: float) -> datetime:
        """输入公历时间和经度，返回校正后的真太阳时"""
        # 真太阳时 = 平太阳时(北京时间) + 经度时差
        # 经度时差(分钟) = (本地经度 - 120) * 4
        time_diff_minutes = (longitude - 120) * 4
        true_solar_time = solar_date + timedelta(minutes=time_diff_minutes)
        return true_solar_time

    def _calculate_bazi_from_tst(self, true_solar_time: datetime) -> dict:
        """
        核心排盘逻辑：根据真太阳时计算四柱 (已修正早子时问题)。
        """
        day_pillar_dt = true_solar_time
        if true_solar_time.hour == 23:
            day_pillar_dt = true_solar_time + timedelta(days=1)

        day_for_year_month = sxtwl.fromSolar(true_solar_time.year, true_solar_time.month, true_solar_time.day)
        day_for_day = sxtwl.fromSolar(day_pillar_dt.year, day_pillar_dt.month, day_pillar_dt.day)

        year_gz = day_for_year_month.getYearGZ()
        year_gan = self.TIAN_GAN[year_gz.tg]
        year_zhi = self.DI_ZHI[year_gz.dz]

        month_gz = day_for_year_month.getMonthGZ()
        month_gan = self.TIAN_GAN[month_gz.tg]
        month_zhi = self.DI_ZHI[month_gz.dz]

        day_gz = day_for_day.getDayGZ()
        day_gan = self.TIAN_GAN[day_gz.tg]
        day_zhi = self.DI_ZHI[day_gz.dz]

        hour_zhi_index = (true_solar_time.hour + 1) // 2 % 12
        hour_zhi = self.DI_ZHI[hour_zhi_index]

        day_gan_index = day_gz.tg
        hour_gan_index = (day_gan_index % 5 * 2 + hour_zhi_index % 12) % 10
        hour_gan = self.TIAN_GAN[hour_gan_index]

        return {
            "year_pillar": f"{year_gan}{year_zhi}",
            "month_pillar": f"{month_gan}{month_zhi}",
            "day_pillar": f"{day_gan}{day_zhi}",
            "hour_pillar": f"{hour_gan}{hour_zhi}"
        }

    # 7. 四柱排盘 (合并了真太阳时计算)
    def calculate_bazi(self, birth_time: datetime, city_name: str) -> dict:
        """输入公历生日和城市名，自动计算真太阳时并排出四柱"""
        longitude, _ = self.get_location_info(city_name)
        true_solar_time = self.get_true_solar_time(birth_time, longitude)

        bazi = self._calculate_bazi_from_tst(true_solar_time)
        bazi["true_solar_time"] = true_solar_time.strftime('%Y-%m-%d %H:%M:%S')

        return bazi

    def _get_lunar_time_string(self, dt: datetime) -> str:
        """根据datetime对象获取农历干支时间字符串"""
        day = sxtwl.fromSolar(dt.year, dt.month, dt.day)

        year_gz = day.getYearGZ()
        year_gan = self.TIAN_GAN[year_gz.tg]
        year_zhi = self.DI_ZHI[year_gz.dz]

        lunar_month = day.getLunarMonth()
        lunar_day = day.getLunarDay()

        hour_index = (dt.hour + 1) // 2 % 12
        hour_zhi = self.DI_ZHI[hour_index]

        lunar_month_names = ['正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '冬月',
                             '腊月']
        lunar_month_name = ("闰" if day.isLunarLeap() else "") + lunar_month_names[lunar_month - 1]

        lunar_day_names = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                           '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                           '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
        lunar_day_name = lunar_day_names[lunar_day - 1]

        return f"{year_gan}{year_zhi}年{lunar_month_name}月{lunar_day_name}{hour_zhi}时"

    def _get_lunar_data(self, dt: datetime) -> dict:
        """根据datetime对象获取农历原始数据结构"""
        day = sxtwl.fromSolar(dt.year, dt.month, dt.day)

        year_gz = day.getYearGZ()
        year_gan = self.TIAN_GAN[year_gz.tg]
        year_zhi = self.DI_ZHI[year_gz.dz]

        lunar_month = day.getLunarMonth()
        lunar_day = day.getLunarDay()
        is_leap = day.isLunarLeap()

        hour_index = (dt.hour + 1) // 2 % 12
        hour_zhi = self.DI_ZHI[hour_index]

        lunar_month_names = ['正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '冬月',
                             '腊月']
        lunar_month_name = ("闰" if is_leap else "") + lunar_month_names[lunar_month - 1]

        lunar_day_names = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                           '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                           '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
        lunar_day_name = lunar_day_names[lunar_day - 1]

        return {
            "year": day.getLunarYear(),
            "month": lunar_month,
            "day": lunar_day,
            "hour": hour_index,
            "is_leap_month": is_leap,
            "ganzhi": {
                "year_gan": year_gan,
                "year_zhi": year_zhi,
                "year_ganzhi": f"{year_gan}{year_zhi}"
            },
            "display": {
                "month_name": lunar_month_name,
                "day_name": lunar_day_name,
                "hour_name": hour_zhi,
                "full_string": f"{year_gan}{year_zhi}年{lunar_month_name}月{lunar_day_name}{hour_zhi}时"
            }
        }

    def calculate_dayun(self, birth_time: datetime, gender: str, city_name: str) -> dict:

        longitude, _ = self.get_location_info(city_name)
        true_solar_time = self.get_true_solar_time(birth_time, longitude)

        # 步骤1: 获取经过“早子时”校准后的正确八字
        bazi_info = self._calculate_bazi_from_tst(true_solar_time)

        day_master_gan_str = bazi_info['day_pillar'][0]
        day_gan_index = self.TIAN_GAN.index(day_master_gan_str)

        original_day = sxtwl.fromSolar(true_solar_time.year, true_solar_time.month, true_solar_time.day)
        year_gz = original_day.getYearGZ()
        py_gender = 1 if gender == "男" else 0
        is_forward = (year_gz.tg % 2 == 0 and py_gender == 1) or (year_gz.tg % 2 != 0 and py_gender == 0)

        # "节"的索引: 立春(3), 惊蛰(5), 清明(7), 立夏(9), 芒种(11), 小暑(13), 立秋(15), 白露(17), 寒露(19), 立冬(21), 大雪(23), 小寒(1)
        JIE_INDEXES = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23}

        jieqi_day = None
        temp_day = original_day
        if is_forward:  # 顺排，找未来的节
            # 如果出生当天就是节，则从下一天开始找
            if temp_day.hasJieQi() and temp_day.getJieQi() in JIE_INDEXES:
                temp_day = temp_day.after(1)
            while True:
                if temp_day.hasJieQi() and temp_day.getJieQi() in JIE_INDEXES:
                    jieqi_day = temp_day
                    break
                temp_day = temp_day.after(1)
        else:  # 逆排，找过去的节
            # 如果出生当天就是节，则从前一天开始找
            if temp_day.hasJieQi() and temp_day.getJieQi() in JIE_INDEXES:
                temp_day = temp_day.before(1)
            while True:
                if temp_day.hasJieQi() and temp_day.getJieQi() in JIE_INDEXES:
                    jieqi_day = temp_day
                    break
                temp_day = temp_day.before(1)

        jd = jieqi_day.getJieQiJD()
        jieqi_time_info = sxtwl.JD2DD(jd)
        jieqi_datetime = datetime(
            int(jieqi_time_info.Y), int(jieqi_time_info.M), int(jieqi_time_info.D),
            int(jieqi_time_info.h), int(jieqi_time_info.m), int(round(jieqi_time_info.s))
        )

        time_diff = abs(jieqi_datetime - true_solar_time)

        days_diff = time_diff.total_seconds() / (3600 * 24)

        # 计算起运岁数
        qiyun_years_float = days_diff / 3
        qiyun_year = int(qiyun_years_float)

        remaining_days_after_years = (qiyun_years_float - qiyun_year) * 360  # 按一年360天算
        qiyun_month = int(remaining_days_after_years / 30)
        qiyun_day = int(remaining_days_after_years % 30)

        # 实际起运周岁
        age_at_start_of_luck = int(round(qiyun_years_float))
        # 很多软件习惯用虚岁，这里也提供一个参考
        # 虚岁起运 = 周岁 + 1 或 + 2，这里简单加1
        xusui_at_start_of_luck = age_at_start_of_luck + 1

        qiyun_raw = {
            "year": qiyun_year,
            "month": qiyun_month,
            "day": qiyun_day,
            "age_at_start_of_luck": age_at_start_of_luck,  # 精确周岁
            "xusui_at_start_of_luck": xusui_at_start_of_luck  # 参考虚岁
        }

        jiaoyun_year = birth_time.year + age_at_start_of_luck
        jiaoyun_month = birth_time.month + qiyun_month
        while jiaoyun_month > 12:
            jiaoyun_month -= 12
            jiaoyun_year += 1
        jiaoyun_raw = {"year": jiaoyun_year, "month": jiaoyun_month}

        # 步骤5: 排列大运干支并计算正确的十神
        dayun_list = []
        current_dayun = None
        current_age = datetime.now().year - birth_time.year

        month_gz = original_day.getMonthGZ()  # 大运从月柱开始排

        gan_wuxing = ["木", "木", "火", "火", "土", "土", "金", "金", "水", "水"]
        relation_names = {
            "木木": "比肩", "木木_": "劫财", "木火": "食神", "木火_": "伤官", "木土": "偏财", "木土_": "正财",
            "木金": "七杀", "木金_": "正官", "木水": "偏印", "木水_": "正印", "火木": "偏印", "火木_": "正印",
            "火火": "比肩", "火火_": "劫财", "火土": "食神", "火土_": "伤官", "火金": "偏财", "火金_": "正财",
            "火水": "七杀", "火水_": "正官", "土木": "七杀", "土木_": "正官", "土火": "偏印", "土火_": "正印",
            "土土": "比肩", "土土_": "劫财", "土金": "食神", "土金_": "伤官", "土水": "偏财", "土水_": "正财",
            "金木": "偏财", "金木_": "正财", "金火": "七杀", "金火_": "正官", "金土": "偏印", "金土_": "正印",
            "金金": "比肩", "金金_": "劫财", "金水": "食神", "金水_": "伤官", "水木": "食神", "水木_": "伤官",
            "水火": "偏财", "水火_": "正财", "水土": "七杀", "水土_": "正官", "水金": "偏印", "水金_": "正印",
            "水水": "比肩", "水水_": "劫财"
        }

        for i in range(10):  # 计算10步大运
            # !!! 核心错误修正: 偏移量必须从1开始，所以用 i + 1 !!!
            offset = (i + 1) if is_forward else -(i + 1)

            dayun_gan_index = (month_gz.tg + offset) % 10
            dayun_zhi_index = (month_gz.dz + offset) % 12

            dayun_gan = self.TIAN_GAN[dayun_gan_index]
            dayun_zhi = self.DI_ZHI[dayun_zhi_index]

            age_start = age_at_start_of_luck + i * 10
            year_start = birth_time.year + age_start

            # 使用正确的日主天干计算十神
            day_wuxing = gan_wuxing[day_gan_index]
            dayun_wuxing = gan_wuxing[dayun_gan_index]

            relation_key = f"{day_wuxing}{dayun_wuxing}"
            # 异性为正，同性为偏。异性相吸，所以带下划线表示异性关系。
            if day_gan_index % 2 != dayun_gan_index % 2:
                relation_key += "_"
            ming_li = relation_names.get(relation_key, "未知")

            dayun_item = {
                "age": age_start, "year": year_start, "ganzhi": f"{dayun_gan}{dayun_zhi}",
                "gan": dayun_gan, "zhi": dayun_zhi, "ming_li": ming_li
            }
            dayun_list.append(dayun_item)

            if current_age >= age_start and (i == 9 or current_age < age_start + 10):
                current_dayun = dayun_item

        bazi = {
            "year": bazi_info['year_pillar'], "month": bazi_info['month_pillar'],
            "day": bazi_info['day_pillar'], "hour": bazi_info['hour_pillar']
        }

        birth_solar = {
            "year": true_solar_time.year, "month": true_solar_time.month, "day": true_solar_time.day,
            "hour": true_solar_time.hour, "minute": true_solar_time.minute, "second": true_solar_time.second,
            "timestamp": true_solar_time.timestamp(), "iso_format": true_solar_time.isoformat(),
            "display": true_solar_time.strftime('%Y-%m-%d %H:%M')
        }

        birth_lunar = self._get_lunar_data(true_solar_time)

        return {
            "birth_solar": birth_solar, "birth_lunar": birth_lunar, "bazi": bazi,
            "dayun_list": dayun_list, "qiyun_data": qiyun_raw, "jiaoyun_data": jiaoyun_raw,
            "current_dayun": current_dayun
        }

    def get_timenow(self) -> datetime:
        """获取当前精确时间"""
        return datetime.now()


# --- 使用示例 ---
if __name__ == '__main__':
    engine = BaziEngine()

    birth_time_str = "2001-12-23 13:00:00"
    birth_time = datetime.strptime(birth_time_str, '%Y-%m-%d %H:%M:%S')
    city = "浙江省金华市东阳市"
    gender = "女"

    print("\n" + "=" * 50)
    print("八字引擎 BaziEngine 功能测试 (使用早子时案例)")
    print("=" * 50)

    # 大运计算专项测试
    print("\n" + "*" * 10 + " 大运计算专项测试 " + "*" * 10)
    print(f"输入信息: {birth_time_str}, 性别: {gender}, 城市: {city}")
    try:
        result = engine.calculate_dayun(birth_time, gender, city)
        qiyun = result.get('qiyun_data', {})
        dayun_list = result.get('dayun_list', [])
        bazi = result.get('bazi', {})
        print(f"校准后八字: {bazi.get('year')} {bazi.get('month')} {bazi.get('day')} {bazi.get('hour')}")
        print(f"日主天干: {bazi.get('day', ' ')[0]}")
        print(f"起运时间: {qiyun.get('year')}年 {qiyun.get('month')}月 {qiyun.get('day')}日")
        if dayun_list:
            print("大运列表 (包含根据正确日主计算的十神):")
            for dayun in dayun_list[:5]:  # 显示前5步大运
                print(
                    f"  {dayun.get('age')}岁起 ({dayun.get('year')}年) {dayun.get('ganzhi')} ({dayun.get('ming_li')})")
    except Exception as e:
        print(f"大运计算测试失败: {e}")
    print("*" * 34)

    # 6. 四柱排盘
    print("\n" + "-" * 40)
    print("6. calculate_bazi 原始返回值:")
    print("【功能】计算四柱八字信息")
    try:
        result = engine.calculate_bazi(birth_time, city)
        print(f"返回类型: {type(result)}")
        print(f"返回值: {result}")
    except Exception as e:
        print(f"函数调用失败: {e}")

    # 7. 大运信息
    print("\n" + "-" * 40)
    print("7. calculate_dayun 原始返回值:")
    print("【功能】计算大运信息，包含命理关系")
    try:
        result = engine.calculate_dayun(birth_time, gender, city)
        print(f"返回类型: {type(result)}")
        print("返回值 (部分展示，内容较多):")
        if isinstance(result, dict):
            print(f"  包含键: {', '.join(result.keys())}")
            # 展示大运列表的前2个
            if "dayun_list" in result:
                print("\n  大运列表示例 (前2个):")
                for i, dayun in enumerate(result["dayun_list"][:2]):
                    print(f"    大运{i + 1}: {dayun}")
        else:
            print(f"  {result}")
    except Exception as e:
        print(f"函数调用失败: {e}")

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)