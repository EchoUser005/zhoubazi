from datetime import datetime, timedelta
import sxtwl
from geopy.geocoders import Nominatim

"""
日历计算工具

1. 公历转农历
2. 农历转公历
3. 获取今日干支历 (如：乙巳年壬午月甲申日)
4. 地理位置查经纬度
5. 真太阳时计算获得校准后生辰
6. 未来日历生成 (获取近n周干支历，假设今天是6月9日周一，则获取6月9日-6月22日干支历)
7. 四柱排盘
8. 大运信息计算工具
"""


class BaziEngine:
    def __init__(self):
        """初始化引擎"""
        self.TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        # 初始化地理位置查询器，并设置更长的超时时间（10秒）
        self.geolocator = Nominatim(user_agent="bazi_analyzer_app/1.0", timeout=10, proxies=None) # type: ignore

    # 1. 公历转农历
    def convert_solar_to_lunar(self, solar_date: datetime) -> dict:
        """输入公历datetime对象，返回农历信息字典"""
        day = sxtwl.fromSolar(solar_date.year, solar_date.month, solar_date.day)
        
        # 农历月名称 (修正版本)
        lunar_month_names = ['正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '冬月', '腊月']
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
    def convert_lunar_to_solar(self, lunar_year: int, lunar_month: int, lunar_day: int, is_leap: bool = False) -> datetime:
        """输入农历年月日和是否闰月，返回公历datetime对象"""
        day = sxtwl.fromLunar(lunar_year, lunar_month, lunar_day, is_leap)
        return datetime(day.getSolarYear(), day.getSolarMonth(), day.getSolarDay())

    # 3. 干支查询
    def get_ganzhi_info(self, solar_date: datetime) -> dict:
        """输入公历datetime对象，返回年月日干支及其他信息"""
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

    # 4. 地理位置查经纬度
    def get_location_info(self, city_name: str) -> tuple[float, float]:
        """输入城市名，利用geopy查询经纬度。如果找不到则抛出ValueError。"""
        try:
            location = self.geolocator.geocode(city_name)
            if location is None:
                raise ValueError(f"无法找到地理位置: '{city_name}'")
            return location.longitude, location.latitude # type: ignore
        except Exception as e:
            # 捕获所有geopy可能抛出的异常，并统一向上抛出
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
        """核心排盘逻辑：根据真太阳时计算四柱。"""
        # 使用校正后的时间排盘
        day = sxtwl.fromSolar(true_solar_time.year, true_solar_time.month, true_solar_time.day)
        
        # 获取年月日的天干地支
        year_gz = day.getYearGZ()
        year_gan = self.TIAN_GAN[year_gz.tg]
        year_zhi = self.DI_ZHI[year_gz.dz]
        
        month_gz = day.getMonthGZ()
        month_gan = self.TIAN_GAN[month_gz.tg]
        month_zhi = self.DI_ZHI[month_gz.dz]
        
        day_gz = day.getDayGZ()
        day_gan = self.TIAN_GAN[day_gz.tg]
        day_zhi = self.DI_ZHI[day_gz.dz]
        
        # 获取时辰地支和天干
        hour_zhi_index = (true_solar_time.hour + 1) // 2 % 12
        hour_zhi = self.DI_ZHI[hour_zhi_index]
        
        # 这里也需要修改，使用 day_gz.tg 替代 day_gan_index
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

    # 需要添加一个辅助方法获取农历干支时间字符串
    def _get_lunar_time_string(self, dt: datetime) -> str:
        """根据datetime对象获取农历干支时间字符串"""
        day = sxtwl.fromSolar(dt.year, dt.month, dt.day)
        
        # 获取年月日时干支
        year_gz = day.getYearGZ()
        year_gan = self.TIAN_GAN[year_gz.tg]
        year_zhi = self.DI_ZHI[year_gz.dz]
        
        # 获取农历月日
        lunar_month = day.getLunarMonth()
        lunar_day = day.getLunarDay()
        
        # 时辰
        hour_index = (dt.hour + 1) // 2 % 12
        hour_zhi = self.DI_ZHI[hour_index]
        
        # 农历月名称 (修正版本)
        lunar_month_names = ['正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '冬月', '腊月']
        lunar_month_name = ("闰" if day.isLunarLeap() else "") + lunar_month_names[lunar_month - 1]
        
        # 农历日名称
        lunar_day_names = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                           '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                           '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
        lunar_day_name = lunar_day_names[lunar_day - 1]
        
        return f"{year_gan}{year_zhi}年{lunar_month_name}月{lunar_day_name}{hour_zhi}时"
        
    # 修改为返回原始数据结构
    def _get_lunar_data(self, dt: datetime) -> dict:
        """根据datetime对象获取农历原始数据结构"""
        day = sxtwl.fromSolar(dt.year, dt.month, dt.day)
        
        # 获取年月日时干支
        year_gz = day.getYearGZ()
        year_gan = self.TIAN_GAN[year_gz.tg]
        year_zhi = self.DI_ZHI[year_gz.dz]
        
        # 获取农历月日
        lunar_month = day.getLunarMonth()
        lunar_day = day.getLunarDay()
        is_leap = day.isLunarLeap()
        
        # 时辰
        hour_index = (dt.hour + 1) // 2 % 12
        hour_zhi = self.DI_ZHI[hour_index]
        
        # 农历月名称(仅用于显示，不是原始数据) (修正版本)
        lunar_month_names = ['正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '冬月', '腊月']
        lunar_month_name = ("闰" if is_leap else "") + lunar_month_names[lunar_month - 1]
        
        # 农历日名称(仅用于显示，不是原始数据)
        lunar_day_names = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                           '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                           '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
        lunar_day_name = lunar_day_names[lunar_day - 1]
        
        # 返回原始数据结构
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

    # 8. 大运信息计算工具
    def calculate_dayun(self, birth_time: datetime, gender: str, city_name: str) -> dict:
        """输入生日、性别、城市，计算大运信息"""
        longitude, _ = self.get_location_info(city_name)
        true_solar_time = self.get_true_solar_time(birth_time, longitude)
        
        # 核心修正：直接从真太阳时计算八字，确保数据一致性
        bazi_info = self._calculate_bazi_from_tst(true_solar_time)
        
        # 获取出生当天信息 (使用校准后的真太阳时)
        day = sxtwl.fromSolar(true_solar_time.year, true_solar_time.month, true_solar_time.day)
        
        # 性别转换 (1为男, 0为女)
        py_gender = 1 if gender == "男" else 0
        
        # 获取年干支
        year_gz = day.getYearGZ()
        
        # 判断顺逆：阳年男、阴年女顺排，阴年男、阳年女逆排
        # 天干-甲(0)乙(1)丙(2)丁(3)戊(4)己(5)庚(6)辛(7)壬(8)癸(9)
        # 阳：甲丙戊庚壬 (偶数)
        # 阴：乙丁己辛癸 (奇数)
        is_forward = (year_gz.tg % 2 == 0 and py_gender == 1) or (year_gz.tg % 2 == 1 and py_gender == 0)
        
        # 查找上一个或下一个节令
        jieqi_day = None
        # 节令的索引: 小寒(1), 立春(3), 惊蛰(5), 清明(7), 立夏(9), 芒种(11), 小暑(13), 立秋(15), 白露(17), 寒露(19), 立冬(21), 大雪(23)
        JIE_QI_INDEXES = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23}
        
        # 临时用的day对象，用于循环查找
        temp_day = day
        if is_forward:
            # 顺排，找下一个节令
            while True:
                temp_day = temp_day.after(1)
                if temp_day.hasJieQi() and temp_day.getJieQi() in JIE_QI_INDEXES:
                    jieqi_day = temp_day
                    break
        else:
            # 逆排，找上一个节令
            # 先检查出生当天是不是节令
            if day.hasJieQi() and day.getJieQi() in JIE_QI_INDEXES:
                # 如果是，则找它之前的节令
                 temp_day = day.before(1)
            while True:
                if temp_day.hasJieQi() and temp_day.getJieQi() in JIE_QI_INDEXES:
                    jieqi_day = temp_day
                    break
                temp_day = temp_day.before(1)

        # 获取节令的精确时间
        jd = jieqi_day.getJieQiJD()
        jieqi_time_info = sxtwl.JD2DD(jd)
        jieqi_datetime = datetime(
            int(jieqi_time_info.Y), int(jieqi_time_info.M), int(jieqi_time_info.D),
            int(jieqi_time_info.h), int(jieqi_time_info.m), int(round(jieqi_time_info.s))
        )

        # 计算时间差
        time_diff = abs(jieqi_datetime - true_solar_time)

        # 3天=1岁, 1天=4个月, 1小时=5天
        days_diff = time_diff.total_seconds() / (3600 * 24)
        
        # 计算起运岁数
        qiyun_years_float = days_diff / 3
        
        qiyun_year = int(qiyun_years_float)
        
        # 计算剩余天数，换算成月和日
        remaining_days_after_years = (qiyun_years_float - qiyun_year) * 360 # 按一年360天算
        qiyun_month = int(remaining_days_after_years / 30)
        qiyun_day = int(remaining_days_after_years % 30)

        # 返回原始数据，不包含固定业务拼接字符串（如"起运"或"上大运"）
        qiyun_raw = {
            "year": qiyun_year,
            "month": qiyun_month,
            "day": qiyun_day
        }
        
        # 交运时间
        jiaoyun_year = birth_time.year + qiyun_year
        jiaoyun_month = birth_time.month + qiyun_month
        # 处理月份溢出
        while jiaoyun_month > 12:
            jiaoyun_month -= 12
            jiaoyun_year += 1
            
        # 交运时间原始数据，不包含"交运"字样
        jiaoyun_raw = {
            "year": jiaoyun_year,
            "month": jiaoyun_month,
            # 可以添加更多细节如特殊年份、时辰等
        }
        
        # 计算当前年龄和所在大运
        current_year = datetime.now().year
        current_age = current_year - birth_time.year
        
        # 获取大运干支列表
        month_gz = day.getMonthGZ()
        dayun_list = []
        current_dayun = None
        
        # 获取日干的索引，用于推算命理关系
        day_gz = day.getDayGZ()
        day_gan_index = day_gz.tg
        
        # 天干五行属性
        gan_wuxing = ["木", "木", "火", "火", "土", "土", "金", "金", "水", "水"]
        
        # 命理关系表（简化版）
        relation_names = {
            "木木": "比肩",
            "木木_": "劫财",
            "木火": "食神",
            "木火_": "伤官",
            "木土": "财星",
            "木土_": "财星",
            "木金": "杀星",
            "木金_": "官星",
            "木水": "印星",
            "木水_": "枭神",
            "火木": "印星",
            "火木_": "枭神",
            "火火": "比肩",
            "火火_": "劫财",
            "火土": "食神",
            "火土_": "伤官",
            "火金": "财星",
            "火金_": "财星",
            "火水": "杀星",
            "火水_": "官星",
            "土木": "杀星",
            "土木_": "官星",
            "土火": "印星",
            "土火_": "枭神",
            "土土": "比肩",
            "土土_": "劫财",
            "土金": "食神",
            "土金_": "伤官",
            "土水": "财星",
            "土水_": "财星",
            "金木": "财星",
            "金木_": "财星",
            "金火": "杀星",
            "金火_": "官星",
            "金土": "印星",
            "金土_": "枭神",
            "金金": "比肩",
            "金金_": "劫财",
            "金水": "食神",
            "金水_": "伤官",
            "水木": "食神",
            "水木_": "伤官",
            "水火": "财星",
            "水火_": "财星",
            "水土": "杀星",
            "水土_": "官星",
            "水金": "印星",
            "水金_": "枭神",
            "水水": "比肩",
            "水水_": "劫财"
        }
        
        for i in range(10):  # 计算10步大运
            age_start = qiyun_year + i * 10
            year_start = birth_time.year + age_start
            
            # 根据顺逆计算月柱偏移
            if is_forward:
                month_offset = i
            else:
                month_offset = -i
                
            # 从本命月柱推算大运干支
            month_gan_index = (month_gz.tg + month_offset) % 10
            month_zhi_index = (month_gz.dz + month_offset) % 12
            
            dayun_gan = self.TIAN_GAN[month_gan_index]
            dayun_zhi = self.DI_ZHI[month_zhi_index]
            
            # 计算命理关系
            day_wuxing = gan_wuxing[day_gan_index]
            dayun_wuxing = gan_wuxing[month_gan_index]
            
            # 阴阳性判断
            is_day_yang = day_gan_index % 2 == 0  # 奇数为阳
            is_dayun_yang = month_gan_index % 2 == 0
            
            # 构建关系键
            relation_key = f"{day_wuxing}{dayun_wuxing}"
            if is_day_yang != is_dayun_yang:
                relation_key += "_"
                
            # 获取命理关系名称
            ming_li = relation_names.get(relation_key, "未知")
            
            dayun_info = {
                "age": age_start,
                "year": year_start,
                "ganzhi": f"{dayun_gan}{dayun_zhi}",
                "gan": dayun_gan,
                "zhi": dayun_zhi,
                "ming_li": ming_li  # 添加命理关系
            }
            dayun_list.append(dayun_info)
            
            # 判断当前所在大运
            if current_age >= age_start and (i == 9 or current_age < age_start + 10):
                current_dayun = {
                    "age": age_start,
                    "year": year_start,
                    "ganzhi": f"{dayun_gan}{dayun_zhi}",
                    "gan": dayun_gan,
                    "zhi": dayun_zhi,
                    "ming_li": ming_li
                }
    
        # 生成基本八字数据
        bazi = {
            "year": bazi_info['year_pillar'],
            "month": bazi_info['month_pillar'],
            "day": bazi_info['day_pillar'],
            "hour": bazi_info['hour_pillar']
        }
        
        # 获取原始出生时间数据
        birth_solar = {
            "year": true_solar_time.year,
            "month": true_solar_time.month,
            "day": true_solar_time.day,
            "hour": true_solar_time.hour,
            "minute": true_solar_time.minute,
            "second": true_solar_time.second,
            "timestamp": true_solar_time.timestamp(),
            "iso_format": true_solar_time.isoformat(),
            "display": true_solar_time.strftime('%Y-%m-%d %H:%M')
        }
        
        # 获取农历原始数据
        birth_lunar = self._get_lunar_data(true_solar_time)
        
        return {
            "birth_solar": birth_solar,  # 公历日期时间原始数据
            "birth_lunar": birth_lunar,  # 农历日期时间原始数据
            "bazi": bazi,  # 八字原始数据
            "dayun_list": dayun_list,  # 大运列表
            "qiyun_data": qiyun_raw,  # 起运原始数据
            "jiaoyun_data": jiaoyun_raw,  # 交运原始数据
            "current_dayun": current_dayun  # 当前大运
        }

    # 获取当前时间
    def get_timenow(self) -> datetime:
        """获取当前精确时间"""
        return datetime.now()


# --- 使用示例 ---
if __name__ == '__main__':
    engine = BaziEngine()

    
    # 测试数据
    birth_time_str = "2001-12-23 13:00:00"
    birth_time = datetime.strptime(birth_time_str, '%Y-%m-%d %H:%M:%S')
    city = "浙江省金华市东阳市"  
    gender = "女"
    
    print("\n" + "="*50)
    print("八字引擎 BaziEngine 功能测试")
    print("="*50)

    # 大运计算专项测试
    print("\n" + "*"*10 + " 大运计算专项测试 " + "*"*10)
    print(f"输入信息: {birth_time_str}, 性别: {gender}, 城市: {city}")
    try:
        result = engine.calculate_dayun(birth_time, gender, city)
        qiyun = result.get('qiyun_data', {})
        dayun_list = result.get('dayun_list', [])
        print(f"起运时间: {qiyun.get('year')}年 {qiyun.get('month')}月 {qiyun.get('day')}日")
        if dayun_list:
            first_dayun = dayun_list[0]
            print(f"第一步大运: {first_dayun.get('age')}岁 ({first_dayun.get('year')}年) {first_dayun.get('ganzhi')} {first_dayun.get('ming_li')}")
    except Exception as e:
        print(f"大运计算测试失败: {e}")
    print("*"*34)
    
    # 1. 公历转农历
    print("\n1. convert_solar_to_lunar 原始返回值:")
    print("【功能】将公历日期转换为农历日期，返回结构化数据")
    try:
        result = engine.convert_solar_to_lunar(birth_time)
        print(f"返回类型: {type(result)}")
        print(f"返回值: {result}")
    except Exception as e:
        print(f"函数调用失败: {e}")
    
    # 2. 农历转公历
    print("\n" + "-"*40)
    print("2. convert_lunar_to_solar 原始返回值:")
    print("【功能】将农历日期转换为公历日期，返回datetime对象")
    try:
        result = engine.convert_lunar_to_solar(2001, 11, 9, False)
        print(f"返回类型: {type(result)}")
        print(f"返回值: {result}")
    except Exception as e:
        print(f"函数调用失败: {e}")
    
    # 3. 干支信息
    print("\n" + "-"*40)
    print("3. get_ganzhi_info 原始返回值:")
    print("【功能】获取给定日期的干支信息")
    try:
        result = engine.get_ganzhi_info(birth_time)
        print(f"返回类型: {type(result)}")
        print(f"返回值: {result}")
    except Exception as e:
        print(f"函数调用失败: {e}")
    
    # 4. 地理位置查询
    print("\n" + "-"*40)
    print("4. get_location_info 原始返回值:")
    print("【功能】根据地名查询经纬度信息")
    try:
        result = engine.get_location_info(city)
        print(f"返回类型: {type(result)}")
        print(f"返回值: {result}")
    except Exception as e:
        print(f"函数调用失败: {e}")
    
    # 5. 真太阳时
    print("\n" + "-"*40)
    print("5. get_true_solar_time 原始返回值:")
    print("【功能】根据经度计算真太阳时")
    try:
        longitude = 120.242  # 测试用经度值
        result = engine.get_true_solar_time(birth_time, longitude)
        print(f"返回类型: {type(result)}")
        print(f"返回值: {result}")
    except Exception as e:
        print(f"函数调用失败: {e}")
    
    # 6. 四柱排盘
    print("\n" + "-"*40)
    print("6. calculate_bazi 原始返回值:")
    print("【功能】计算四柱八字信息")
    try:
        result = engine.calculate_bazi(birth_time, city)
        print(f"返回类型: {type(result)}")
        print(f"返回值: {result}")
    except Exception as e:
        print(f"函数调用失败: {e}")
    
    # 7. 大运信息
    print("\n" + "-"*40)
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
                    print(f"    大运{i+1}: {dayun}")
        else:
            print(f"  {result}")
    except Exception as e:
        print(f"函数调用失败: {e}")
    
    # 8. _get_lunar_data
    print("\n" + "-"*40)
    print("8. _get_lunar_data 原始返回值:")
    print("【功能】获取农历详细数据，包含展示信息")
    try:
        result = engine._get_lunar_data(birth_time)
        print(f"返回类型: {type(result)}")
        print(f"返回值: {result}")
    except Exception as e:
        print(f"函数调用失败: {e}")
    
    print("\n" + "="*50)
    print("测试完成")
    print("="*50)