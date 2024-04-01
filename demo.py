import streamlit as st
import base64
from PIL import Image
from io import BytesIO
import pymysql
import time

st.set_page_config(layout="wide")

def get_base64_of_image(image_data):
    return base64.b64encode(image_data).decode("utf-8")

def get_base64_of_image2(image):
    img_buffer = BytesIO()
    image.save(img_buffer, format="PNG")
    img_str = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
    return img_str

# 下个页面地址
next_page_url = "http://localhost:8501/two"


# 使用CSS来居中显示
st.markdown("""
    <style>
    .center {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# 在页面中居中显示标题
st.markdown('<h1 class="center">自动阅卷系统</h1>', unsafe_allow_html=True)

st.write('')
st.write('')
st.write('')


# 连接数据库
conn = pymysql.connect(
    host='%',
    user='root',
    password='L123456',
    port=3306,
    db='marking_system2',
    charset='utf8'
)

with conn.cursor() as cursor:
    cursor.execute('SELECT paper_name, subject, grade, attribute, paper_image1, paper_image2 FROM paper')
    results = cursor.fetchall()

col1, col2, col3 = st.columns(3)
with col1:
    # 创建年级下拉框
    grade_options = ['高一', '高二', '高三']
    selected_grade = st.selectbox('年级',['']+ grade_options)

with col2:
    # 创建学科下拉框
    subject_options = ['数学', '语文', '英语', '物理', '化学', '生物','地理', '历史', '政治']
    selected_subject = st.selectbox('学科', ['']+subject_options)

with col3:
    # 创建类型下拉框
    attribute_options = ['期中', '期末', '月考', '周考']
    selected_attribute = st.selectbox('类型',['']+ attribute_options)

st.markdown("***") 

st.write('<span style="color: red;">【可供选择的试卷】</span>', unsafe_allow_html=True)

filtered_results = results

if selected_grade:
    filtered_results = [r for r in filtered_results if r[2] == selected_grade]

if selected_subject:
    filtered_results = [r for r in filtered_results if r[1] == selected_subject]

if selected_attribute:
    filtered_results = [r for r in filtered_results if r[3] == selected_attribute]

num_pairs = len(filtered_results)
for i in range(num_pairs):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        image_base64_1 = get_base64_of_image(filtered_results[i][4])
        next_page_url = "http://localhost:8501/two"
        st.markdown(f'<div style="background-color: #f2f2f2; padding: 10px;"><a href="{next_page_url}"><img src="data:image/png;base64,{image_base64_1}" style="width:100%" title=""></a></div>', unsafe_allow_html=True)
    
    with col2:
        image_base64_2 = get_base64_of_image(filtered_results[i][5])
        next_page_url = "http://localhost:8501/two"
        st.markdown(f'<div style="background-color: #f2f2f2; padding: 10px;"><a href="{next_page_url}"><img src="data:image/png;base64,{image_base64_2}" style="width:100%" title=""></a></div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<style>.container {display: flex; align-items: center; justify-content: center;}</style>', unsafe_allow_html=True)
        st.markdown('<div class="container">', unsafe_allow_html=True)
        st.markdown('<style>textarea {height: 100px;}</style>', unsafe_allow_html=True)
        a = st.text_area('试卷介绍', f'''试卷名称：{filtered_results[i][0]}
科目：{filtered_results[i][1]}
年级：{filtered_results[i][2]}''', key=str(i))

    st.markdown("***")

#添加新试卷
st.write('<span style="color: red;">【添加新试卷】</span>', unsafe_allow_html=True)

col4,col5,col6 = st.columns(3)

with col4:
    uploaded_files_front = st.file_uploader("上传正面试卷", type=["jpg", "png", "jpeg"])
    if uploaded_files_front is not None:
        image = Image.open(uploaded_files_front)
        next_page_url = "http://localhost:8501/two"
        st.markdown(f'<a href="{next_page_url}"><img src="data:image/png;base64,{get_base64_of_image2(image)}" style="width:100%" title=""></a>', unsafe_allow_html=True)

with col5:
    uploaded_files_back = st.file_uploader("上传反面试卷", type=["jpg", "png", "jpeg"])
    if uploaded_files_back is not None:
        image = Image.open(uploaded_files_back)
        next_page_url = "http://localhost:8501/two"
        st.markdown(f'<a href="{next_page_url}"><img src="data:image/png;base64,{get_base64_of_image2(image)}" style="width:100%" title=""></a>', unsafe_allow_html=True)



# 上传答案
answer = st.file_uploader("上传试卷答案", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files_front and uploaded_files_back and answer:  
    with col6:
        st.markdown('<style>.container {display: flex; align-items: center; justify-content: center;}</style>', unsafe_allow_html=True)
        st.markdown('<div class="container">', unsafe_allow_html=True)

        with st.spinner('正在解析中…'):
            time.sleep(10)  

        st.markdown('<style>textarea {height: 100px;}</style>', unsafe_allow_html=True)
        a = st.text_area('试卷介绍', '''试卷名称：五市十校联考试卷 
科目：政治 
年级：高一
''',key='3')

