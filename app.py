import streamlit as st
import requests
import datetime
import json

# 页面配置
st.set_page_config(
    page_title="周易八字运势分析",
    page_icon="☯️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 自定义CSS
st.markdown("""
<style>
    .main {
        background-color: #f8f5f0;
        padding: 20px;
        border-radius: 10px;
    }
    .stButton > button {
        width: 100%;
        background-color: #000;
        color: white;
        border-radius: 50px;
        padding: 15px;
        font-size: 20px;
        margin-top: 20px;
    }
    .input-label {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .location-note {
        color: #888;
        font-size: 14px;
    }
    .solar-time {
        color: #666;
        font-size: 14px;
        margin-top: 5px;
    }
    .markdown-text {
        font-family: "Source Han Sans CN", "PingFang SC", "Microsoft YaHei", sans-serif;
        line-height: 1.6;
    }
    h1, h2, h3, h4 {
        color: #333;
        font-weight: 600;
    }
    hr {
        margin: 20px 0;
        border: 0;
        height: 1px;
        background: #ddd;
    }
</style>
""", unsafe_allow_html=True)

# API配置
API_URL = "http://localhost:8000/analyze/stream"

# 页面标题
st.title("周易八字运势分析")

# 创建表单
with st.form("bazi_form"):
    # 姓名
    st.markdown('<div class="input-label">姓名</div>', unsafe_allow_html=True)
    name = st.text_input("", placeholder="点击输入姓名", label_visibility="collapsed", key="name")
    
    # 性别
    st.markdown('<div class="input-label">性别</div>', unsafe_allow_html=True)
    gender = st.radio("", options=["男", "女"], horizontal=True, label_visibility="collapsed", key="gender")
    
    # 出生日期
    st.markdown('<div class="input-label">出生日期</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        # 为出生日期选择器定义一个合理的范围和默认值
        today = datetime.date.today()
        # 将默认日期设为20年前
        default_date = today.replace(year=today.year - 20)
        # 将可选最小日期设为120年前
        min_date = today.replace(year=today.year - 120)

        birth_date = st.date_input(
            "", 
            value=default_date,
            min_value=min_date,
            max_value=today,
            format="YYYY-MM-DD", 
            label_visibility="collapsed", 
            key="birth_date"
        )
    with col2:
        birth_time = st.time_input("", label_visibility="collapsed", key="birth_time")
    
    
    st.markdown('<div class="input-label">出生/常用城市</div>', unsafe_allow_html=True)
    st.markdown('<div class="location-note">请输入详细地址，精确到市/县，用于校准真太阳时</div>', unsafe_allow_html=True)
    location = st.text_input("", placeholder="例如：浙江省杭州市", label_visibility="collapsed", key="location")
    
    # 提交按钮
    submit_button = st.form_submit_button("开始本周运势分析", use_container_width=True)

# 处理表单提交
if submit_button:
    # 修正校验逻辑
    if not name or not location:
        st.error("请填写姓名和出生城市")
    else:
        # 准备请求数据
        birth_datetime = f"{birth_date} {birth_time}"
        
        # 确保API的两个地址字段都用同一个输入值填充
        data = {
            "birth_time": birth_datetime,
            "birth_location": location,
            "name": name,
            "gender": gender,
            "isTai": True, # 默认使用真太阳时
            "city": location
        }
        
        # 显示加载动画
        with st.spinner("正在分析中，请稍候..."):
            try:
                # 发送流式请求
                with requests.post(API_URL, json=data, stream=True) as response:
                    # 检查响应状态
                    if response.status_code != 200:
                        st.error(f"API请求失败: {response.status_code}")
                        try:
                            st.error(response.json())
                        except json.JSONDecodeError:
                            st.error(response.text)
                    else:
                        # 创建一个空容器来存放结果
                        result_container = st.empty()
                        full_response = ""
                        
                        # 处理流式响应
                        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                            if chunk:
                                full_response += chunk
                                # 更新显示
                                result_container.markdown(f'<div class="markdown-text">{full_response}</div>', unsafe_allow_html=True)
                        
                        st.success("分析完成！")
            
            except Exception as e:
                st.error(f"连接API时出错: {str(e)}")