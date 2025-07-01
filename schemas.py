from pydantic import BaseModel, Field
from typing import Optional

"""
命理排盘数据模型定义:

1. UserInput - 用户的基本输入信息
2. BaziContext - 经过计算后的完整命盘上下文
3. AnalysisContext - 综合用户输入和命盘上下文的完整分析上下文
"""

class UserInput(BaseModel):
    """用户输入的原始信息"""
    birth_time: Optional[str] = Field(None, description="公历出生时间, 格式: YYYY-MM-DD HH:MM:SS")
    birth_location: str = Field(..., description="出生地点, 格式: 省/市/区")
    name: Optional[str] = None  # 姓名，可选
    gender: str  # 性别，"男"或"女"
    isTai: Optional[bool] = None  # 是否胎身命，可选
    city: Optional[str] = None  # 当前所在城市，可选，不填则使用出生地

    # 为农历输入添加新字段
    is_lunar: bool = Field(False, description="是否为农历日期")
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None

class BaziContext(BaseModel):
    """计算后的命盘上下文，用于传入模板"""
    nowtime: str  # 当前时间，格式: 6月9日周一-乙巳年壬午月十四 流年:乙巳年 流月：壬午月 流日：甲申日
    calendar: str  # 近期日历，格式: 周一 己酉日(土金旺)
    name: str  # 姓名
    gender: str  # 性别
    isTai: str  # 是否胎身命，"是"或"否"
    birth_correct: str  # 真太阳时生辰，格式: 2001年12月23日13:00 辛巳年冬月初九午时
    city: str  # 当前所在城市
    bazi: str  # 四柱，格式: 辛巳 庚子 庚辰 壬午
    dayun_time: str  # 大运信息，格式: 大运: 2岁 2003年 庚子 -> 12岁 2013年 辛丑 -> ...
    qiyun_time: str  # 起运时间，格式: 出生后4年5月8日18时 上大运
    jiaoyun_time: str  # 交运时间，格式: 逢丙、辛年 小暑后26天7小时 交大运

class AnalysisContext(BaseModel):
    """完整分析上下文，包含原始输入和计算结果"""
    user_input: UserInput  # 用户输入信息
    bazi_context: BaziContext  # 计算后的命盘上下文

# 如果在__main__中，打印模型文档
if __name__ == "__main__":
    print("--- 数据模型说明 ---\n")
    print("1. UserInput - 用户输入模型:")
    print(UserInput.__doc__)
    print("\n字段:")
    for field_name, field in UserInput.__annotations__.items():
        field_type = getattr(UserInput, f"__annotations__", {}).get(field_name, "")
        print(f"  - {field_name}: {field_type}")
    
    print("\n2. BaziContext - 命盘上下文模型:")
    print(BaziContext.__doc__)
    print("\n字段:")
    for field_name, field in BaziContext.__annotations__.items():
        field_type = getattr(BaziContext, f"__annotations__", {}).get(field_name, "")
        print(f"  - {field_name}: {field_type}")
    
    print("\n3. AnalysisContext - 完整分析上下文模型:")
    print(AnalysisContext.__doc__)
    
    print("\n--- 示例数据结构 ---")
    example_user = UserInput(
        birth_time="2001-12-23 13:00:00",
        birth_location="浙江省金华市", 
        name="示例用户",
        gender="女",
        city="北京市",
        is_lunar=False
    )
    print(f"\n用户输入示例:\n{example_user.model_dump()}")


