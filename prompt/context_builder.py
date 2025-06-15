from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from schemas import BaziContext, UserInput
from utils.cal_tools import BaziEngine

"""
计划:
1. 实现get_calendare方法生成当前日期所在周和下周的干支历 
2. 修正BaziContext字段与system_prompt变量匹配
3. 完善build_context方法确保所有提示词变量正确填充
"""

class BaziContextBuilder:
    def __init__(self):
        self.engine = BaziEngine()

    def get_calendar(self):
        """获取未来两周的干支历，从本周一开始"""
        # 获取当前时间
        current_time = self.engine.get_timenow()
        
        # 计算本周一的日期
        days_since_monday = current_time.weekday()  # 0是周一，1是周二，以此类推
        monday = current_time - timedelta(days=days_since_monday)
        
        # 设置为本周一的0点
        start_date = datetime(monday.year, monday.month, monday.day)
        # 两周后的结束日期(13天后，共14天)
        end_date = start_date + timedelta(days=13)
        
        # 生成日历头部，例如：6月9日-6月22日干支历
        header = f"{start_date.month}月{start_date.day}日-{end_date.month}月{end_date.day}日干支历"
        
        # 生成未来两周的日期列表
        calendar_items = [header]
        weekday_names = ["一", "二", "三", "四", "五", "六", "日"]
        
        # 生成14天的日历，从本周一开始
        for i in range(14):
            date = start_date + timedelta(days=i)
            weekday = weekday_names[date.weekday()]
            
            # 获取干支信息
            ganzhi_info = self.engine.get_ganzhi_info(date)
            day_ganzhi = ganzhi_info['day_ganzhi']
            
            # 格式化为"6月9日 周一 己酉日"
            calendar_item = f"{date.month}月{date.day}日 周{weekday} {day_ganzhi}日"
            calendar_items.append(calendar_item)
        
        # 合并为一个字符串
        calendar = "\n".join(calendar_items)
        return calendar

    def build_context(self, user_info: UserInput) -> BaziContext:
        """根据用户输入调用计算工具得到完整排盘信息输出一个BaziContext对象"""
        
        # 解析用户输入的生日时间
        birth_time = datetime.strptime(user_info.birth_time, '%Y-%m-%d %H:%M:%S')
        
        # 获取当前时间信息
        current_time = self.engine.get_timenow()
        current_ganzhi = self.engine.get_ganzhi_info(current_time)
        
        # 计算农历信息
        lunar_info = self.engine.convert_solar_to_lunar(current_time)
        
        # 构建当前时间字符串 "6月9日周一-乙巳年壬午月十四"
        weekday_names = ["一", "二", "三", "四", "五", "六", "日"]
        weekday = weekday_names[current_time.weekday()]
        nowtime = f"{current_time.month}月{current_time.day}日周{weekday}-{current_ganzhi['year_ganzhi']}年{current_ganzhi['month_ganzhi']}月{lunar_info['day']}日"
        
        # 获取未来两周日历
        calendar = self.get_calendar()
        
        # 计算八字信息
        bazi_info = self.engine.calculate_bazi(birth_time, user_info.birth_location)
        
        # 计算大运信息
        dayun_info = self.engine.calculate_dayun(birth_time, user_info.gender, user_info.birth_location)
        
        # 构建大运字符串 - 从原始数据拼接，添加命理关系
        dayun_list_str = " -> ".join([f"{dayun['age']}岁 {dayun['year']}年 {dayun['ganzhi']} {dayun['ming_li']}" for dayun in dayun_info["dayun_list"]])
        dayun_time = f"{dayun_list_str}"
        
        # 拼接生辰信息 "2001年12月23日13:00 辛巳年冬月初九午时"
        birth_solar = dayun_info['birth_solar']
        birth_lunar = dayun_info['birth_lunar']
        birth_correct = f"{birth_solar['year']}年{birth_solar['month']}月{birth_solar['day']}日{birth_solar['hour']}:{birth_solar['minute']:02d} {birth_lunar['display']['full_string']}"
        
        # 拼接八字信息 - 从原始数据拼接
        bazi = f"{dayun_info['bazi']['year']} {dayun_info['bazi']['month']} {dayun_info['bazi']['day']} {dayun_info['bazi']['hour']}"
        
        # 拼接起运信息 - 从原始数据拼接，添加"上大运"
        qiyun_data = dayun_info['qiyun_data']
        qiyun_time = f"出生后{qiyun_data['year']}年{qiyun_data['month']}月{qiyun_data['day']}日 上大运"
        
        # 拼接交运信息 - 从原始数据拼接
        jiaoyun_data = dayun_info['jiaoyun_data']
        jiaoyun_time = f"逢丙、辛年 {jiaoyun_data['year']}年{jiaoyun_data['month']}月交大运"
        
        return BaziContext(
            nowtime=nowtime,
            calendar=calendar,
            name=user_info.name if user_info.name else "",
            gender=user_info.gender,
            isTai="是" if user_info.isTai else "否",
            birth_correct=birth_correct,
            city=user_info.city if user_info.city else user_info.birth_location,
            bazi=bazi,
            dayun_time=dayun_time,
            qiyun_time=qiyun_time,
            jiaoyun_time=jiaoyun_time
        )


# 测试代码
if __name__ == "__main__":
    print("\n" + "="*50)
    print("BaziContextBuilder 测试")
    print("="*50)
    
    # 创建测试用户数据
    test_user = UserInput(
        birth_time="2001-12-23 13:00:00",
        birth_location="浙江省金华市东阳市",
        name="测试用户",
        gender="女",
        isTai=False,
        city="北京"
    )
    
    # 创建上下文构建器
    builder = BaziContextBuilder()
    
    # 测试get_calendare方法
    print("\n1. get_calendare 方法测试:")
    calendar = builder.get_calendar()
    print(f"未来两周日历:\n{calendar}")
    
    # 测试build_context方法
    print("\n2. build_context 方法测试:")
    context = builder.build_context(test_user)
    
    # 打印所有字段，检查是否与system_prompt.txt中的变量匹配
    print("\n3. 生成的上下文字段:")
    print(f"nowtime: {context.nowtime}")
    print(f"calendar (前3行):")
    calendar_lines = context.calendar.split('\n')
    for i in range(min(3, len(calendar_lines))):
        print(f"  {calendar_lines[i]}")
    print(f"name: {context.name}")
    print(f"gender: {context.gender}")
    print(f"isTai: {context.isTai}")
    print(f"birth_correct: {context.birth_correct}")
    print(f"city: {context.city}")
    print(f"bazi: {context.bazi}")
    print(f"dayun_time: {context.dayun_time}")
    print(f"qiyun_time: {context.qiyun_time}")
    print(f"jiaoyun_time: {context.jiaoyun_time}")
    
    # 检查字段是否与system_prompt.txt中的变量匹配
    print("\n4. 字段与system_prompt.txt变量匹配检查:")
    prompt_vars = ["nowtime", "calendar", "name", "gender", "isTai", "birth_correct", "city", "bazi", "dayun_time", "jiaoyun_time"]
    context_dict = context.dict()
    
    for var in prompt_vars:
        if var in context_dict:
            print(f"✓ {var} 已正确实现")
        else:
            print(f"✗ {var} 未实现或名称不匹配")
    
    print("\n" + "="*50)
    print("测试完成")
    print("="*50)
    