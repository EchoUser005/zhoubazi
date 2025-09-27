from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas import BaziContext, UserInput
from utils.cal_tools import BaziEngine

"""
计划:
1. 实现get_calendar方法生成当前日期所在周和下周的干支历 
2. 修正BaziContext字段与system_prompt变量匹配
3. 完善build_context方法确保所有提示词变量正确填充
"""

class BaziContextBuilder:
    def __init__(self):
        self.engine = BaziEngine()

    def get_calendar(self):
        """获取未来两周的干支历"""
        current_time = self.engine.get_timenow()
        today_weekday = current_time.weekday()
        days_from_monday = timedelta(days=today_weekday)
        monday_of_this_week = current_time - days_from_monday
        
        start_date = datetime(monday_of_this_week.year, monday_of_this_week.month, monday_of_this_week.day)
        
        end_date = start_date + timedelta(days=13)
        

        weekday_names = ["一", "二", "三", "四", "五", "六", "日"]
        calendar_items = []

        for i in range(14):
            date = start_date + timedelta(days=i)
            weekday = weekday_names[date.weekday()]
            
            # 获取干支信息
            ganzhi_info = self.engine.get_ganzhi_info(date)
            day_ganzhi = ganzhi_info['day_ganzhi']
            
            # 格式化为"6月24日 周一 甲子日"
            calendar_item = f"周{weekday} {day_ganzhi}日 {date.month}月{date.day}日"
            calendar_items.append(calendar_item)
        
        # 合并为一个字符串
        calendar = "\n".join(calendar_items)
        return calendar

    def build_context(self, user_info: UserInput) -> BaziContext:
        """根据用户输入调用计算工具得到完整排盘信息输出一个BaziContext对象"""
        
        # 根据is_lunar字段处理日期
        if user_info.is_lunar:
            # 使用断言确保农历年月日都已提供，并帮助类型检查器
            assert user_info.year is not None, "农历年份不能为空"
            assert user_info.month is not None, "农历月份不能为空"
            assert user_info.day is not None, "农历日期不能为空"
            
            # 将农历转换为公历
            lunar_date = self.engine.convert_lunar_to_solar(
                user_info.year, user_info.month, user_info.day
            )
            
            # 在农历模式下，我们不再依赖birth_time，而是依赖一个新的time字段
            # 但是为了兼容，暂时保留此逻辑，后续将改为从新的time字段读取
            time_str = user_info.birth_time if user_info.birth_time else "12:00:00"

            birth_time_str = f"{lunar_date.strftime('%Y-%m-%d')} {time_str}"
            birth_time = datetime.strptime(birth_time_str, '%Y-%m-%d %H:%M:%S')
        else:
            # 保持原有逻辑，处理公历日期
            if not user_info.birth_time:
                raise ValueError("公历出生时间 (birth_time) 未提供。")
            birth_time = datetime.strptime(user_info.birth_time, '%Y-%m-%d %H:%M:%S')

        current_time = self.engine.get_timenow()
        current_ganzhi = self.engine.get_ganzhi_info(current_time)
        lunar_info = self.engine.convert_solar_to_lunar(current_time)
        # weekday_names = ["一", "二", "三", "四", "五", "六", "日"]
        # weekday = weekday_names[current_time.weekday()]
        # 修改为当前流年流月,避免过度分析今天
        nowtime_month = f"{current_ganzhi['year_ganzhi']}年{current_ganzhi['month_ganzhi']}月"
        calendar = self.get_calendar()

        dayun_info = self.engine.calculate_dayun(birth_time, user_info.gender, user_info.birth_location)

        dayun_list_str = " -> ".join([f"{dayun['age']}岁 {dayun['year']}年 {dayun['ganzhi']} {dayun['ming_li']}" for dayun in dayun_info["dayun_list"]])
        dayun_time = f"{dayun_list_str}"
        
        birth_solar = dayun_info['birth_solar']
        birth_lunar = dayun_info['birth_lunar']
        birth_correct = f"{birth_solar['year']}年{birth_solar['month']}月{birth_solar['day']}日{birth_solar['hour']}:{birth_solar['minute']:02d} {birth_lunar['display']['full_string']}"
        
        bazi = f"{dayun_info['bazi']['year']} {dayun_info['bazi']['month']} {dayun_info['bazi']['day']} {dayun_info['bazi']['hour']}"
        
        qiyun_data = dayun_info['qiyun_data']
        qiyun_time = f"出生后{qiyun_data['year']}年{qiyun_data['month']}月{qiyun_data['day']}日 上大运"
        
        jiaoyun_data = dayun_info['jiaoyun_data']
        jiaoyun_time = f"逢丙、辛年 {jiaoyun_data['year']}年{jiaoyun_data['month']}月交大运"
        
        return BaziContext(
            nowtime=nowtime_month,
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


if __name__ == "__main__":
    print("\n" + "="*50)
    print("BaziContextBuilder 测试")
    print("="*50)
    
    test_user = UserInput(
        birth_time="2001-12-23 13:00:00",
        birth_location="浙江省金华市东阳市",
        name="测试用户",
        gender="女",
        isTai=False,
        city="北京",
        is_lunar=False # 为测试用例添加新字段
    )
    
    builder = BaziContextBuilder()
    
    # 测试get_calendare方法
    print("\n1. get_calendar 方法测试:")
    calendar = builder.get_calendar()
    print(f"未来两周日历:\n{calendar}")
    
    # 测试build_context方法
    print("\n2. build_context 方法测试:")
    context = builder.build_context(test_user)
    
    # 打印所有字段，检查是否与system_prompt.txt中的变量匹配
    print("\n3. 生成的上下文字段:")
    print(f"nowtime_month: {context.nowtime}")
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
    prompt_vars = [
        "nowtime",
        "calendar",
        "name",
        "gender",
        "isTai",
        "birth_correct",
        "city",
         "calendar", "name", "gender", "isTai", "birth_correct", "city", "bazi", "dayun_time", "jiaoyun_time"]
    context_dict = context.model_dump()
    
    for var in prompt_vars:
        if var in context_dict:
            print(f"{var} 已正确实现")
        else:
            print(f"{var} 未实现或名称不匹配")
    
    print("\n" + "="*50)
    print("测试完成")
    print("="*50)
    