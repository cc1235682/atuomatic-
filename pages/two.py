import streamlit as st
import base64
import pymysql
import time 
from zipfile import ZipFile
import webbrowser


selected_question = None

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

def open_link(url):
    webbrowser.open_new_tab(url)

#读取最后的题号
def get_last_question_number():
    # 连接数据库
    conn = pymysql.connect(
            host='%',
            user='root',
            password='L123456',
            port=3306,
            db='marking_system2',
            charset='utf8'
    )

    cursor = conn.cursor()
    query = "SELECT question_number FROM question ORDER BY question_number DESC LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    
    if result:
        return result[0]
    else:
        return 1  # 默认返回1，如果数据库中没有题目记录

# 获取题目内容
def get_question_content(selected_question):
    conn = pymysql.connect(
            host='%',
            user='root',
            password='L123456',
            port=3306,
            db='marking_system2',
            charset='utf8'
    )
    cursor = conn.cursor()
    query = "SELECT question_image, question_analysis FROM question WHERE question_number = %s"
    cursor.execute(query, (selected_question,))
    result = cursor.fetchone()
    cursor.close()

    return result  

# 获取大模型调用后的题干分析
def get_question_analysis_suggestion(selected_question):
    conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='L123456',
            port=3306,
            db='marking_system2',
            charset='utf8'
    )
    cursor = conn.cursor()
    query = "SELECT a FROM question WHERE question_number = %s"
    cursor.execute(query, (selected_question,))
    result = cursor.fetchone()
    return result[0] if result else None

# 答案内容
def get_answer_content(selected_question):
    conn = pymysql.connect(
            host='%',
            user='root',
            password='L123456',
            port=3306,
            db='marking_system2',
            charset='utf8'
    )
    cursor = conn.cursor()
    query = "SELECT answer_image, answer_analysis FROM question WHERE question_number = %s"
    cursor.execute(query, (selected_question,))
    result = cursor.fetchone()
    cursor.close()

    return result  

# 获取大模型调用后的答案分析
def get_answer_analysis_suggestion(selected_question):
    conn = pymysql.connect(
            host='%',
            user='root',
            password='L123456',
            port=3306,
            db='marking_system2',
            charset='utf8'
    )
    cursor = conn.cursor()
    query = "SELECT b FROM question WHERE question_number = %s"
    cursor.execute(query, (selected_question,))
    result = cursor.fetchone()
    return result[0] if result else None 


# 学生答案内容
def get_student_answer_content(selected_question, student_name):
    conn = pymysql.connect(
            host='%',
            user='root',
            password='L123456',
            port=3306,
            db='marking_system2',
            charset='utf8'
    )
    cursor = conn.cursor()

    # 查询 class 表获取 student_id
    query_class = "SELECT student_id FROM class WHERE student_name = %s"
    cursor.execute(query_class, (student_name,))
    result_class = cursor.fetchone()

    if result_class:
        student_id = result_class[0]

        # 根据 student_id 和 selected_question 查询 answer 表获取学生答案内容
        query_answer = "SELECT student_answer_image, student_answer_analysis,score FROM answer WHERE student_id = %s AND question_number = %s"
        cursor.execute(query_answer, (student_id, selected_question))
        result_answer = cursor.fetchone()
        cursor.close()

        return result_answer  # 返回学生答案内容

    else:
        return None

def get_student_answer_analysis_suggestion(selected_question):
    conn = pymysql.connect(
        host='%',
        user='root',
        password='L123456',
        port=3306,
        db='marking_system2',
        charset='utf8'
    )
    cursor = conn.cursor()
    query = "SELECT new_score, b FROM answer WHERE question_number = %s"
    cursor.execute(query, (selected_question,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def content(selected_question):
    # 题目
    st.write(f'第{selected_question}题')
    question_content = get_question_content(selected_question)
    if question_content:
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            img1 = question_content[0]
            encoded_img1 = base64.b64encode(img1).decode()
            st.markdown(
                f'<div style="background-color: #f4f4f4; padding: 10px; border-radius: 5px;">'
                f'<img src="data:image/png;base64,{encoded_img1}" alt="图片1" style="width:100%">'
                '</div>',
                unsafe_allow_html=True
            )
        with row1_col2:
            with st.form(key=f'form_{selected_question}'):
                # 获取题干分析并存储在会话状态中
                text_key = f'text_{selected_question}'
                if text_key not in st.session_state:
                    st.session_state[text_key] = question_content[1]  

                st.session_state[text_key] = st.text_area('题干分析', value=st.session_state[text_key], height=200, max_chars=800)
                text1_2 = st.text_input('与大模型对话', max_chars=100, key='text1_2')
                if st.form_submit_button('确定'):
                    with st.spinner('正在分析中……'):
                        time.sleep(5)
                        question_analysis_suggestion = get_question_analysis_suggestion(selected_question)
                        st.session_state[text_key] = question_analysis_suggestion
                        st.experimental_rerun()
                            
    else:
        st.write("题目不存在")

    # 答案
    answer_content = get_answer_content(selected_question)

    if answer_content:
        st.markdown("***")  # 分隔线
        row2_col1, row2_col2 = st.columns(2)

        with row2_col1:
            img2 = answer_content[0]
            encoded_img2 = base64.b64encode(img2).decode()
            img_width = 400  # 设置图片宽度
            img_height = 400  # 设置图片高度
            st.markdown(
                f'<div style="background-color: #f4f4f4; padding: 10px; border-radius: 5px;">'
                f'<img src="data:image/png;base64,{encoded_img2}" alt="图片2" style="width:{img_width}px; height:{img_height}px">'
                '</div>',
                unsafe_allow_html=True
            )

        with row2_col2:
            with st.form(key=f'form_answer_{selected_question}'):
                text_key = f'text_answer_{selected_question}'
                if text_key not in st.session_state:
                    st.session_state[text_key] = answer_content[1]

                st.session_state[text_key] = st.text_area('答案分析', value=st.session_state[text_key], height=200, max_chars=800)
                text2_2 = st.text_input('与大模型对话', max_chars=100, key='text2_2')
                if st.form_submit_button('确定'):
                    with st.spinner('正在分析中……'):
                        time.sleep(5)
                        answer_analysis_suggestion = get_answer_analysis_suggestion(selected_question)
                        st.session_state[text_key] = answer_analysis_suggestion
                        st.experimental_rerun()

    else:
        st.write("答案不存在")

    st.markdown("***")  

            
    
def student(selected_question):
    student_name = '小美' 

    row3_col1, row3_col2 = st.columns(2)
    
    with row3_col1: 
        student_name = st.selectbox('请选择学生', options=['小美', '小帅', '小强'], key='select_box')
        student_answer_content = get_student_answer_content(selected_question, student_name)
        img3 = student_answer_content[0]
        encoded_img3 = base64.b64encode(img3).decode()
        st.markdown(
            f'<div style="background-color: #f4f4f4; padding: 10px; border-radius: 5px;">'
            f'<img src="data:image/png;base64,{encoded_img3}" alt="学生答案图片" style="width:100%">'
            '</div>',
            unsafe_allow_html=True
        )

        with row3_col2:
            with st.form(key=f'form_answer_{selected_question}_{student_name}'):
                text_key = f'text_answer_{selected_question}_{student_name}'
                score_key = f'score_{selected_question}_{student_name}'
    
                if text_key not in st.session_state:
                    st.session_state[text_key] = student_answer_content[1]  # 设置默认的答案分析内容

                if score_key not in st.session_state:
                    st.session_state[score_key] = student_answer_content[2]  # 设置默认的分数
                
                st.session_state[score_key] = st.text_input('学生得分', value=st.session_state[score_key])
                st.session_state[text_key] = st.text_area('学生答案分析', value=st.session_state[text_key], height=200, max_chars=800)
                
                text3_3 = st.text_input('与大模型对话', max_chars=100, key='text3_3')
                if st.form_submit_button('确定'):
                    with st.spinner('正在分析中……'):
                        time.sleep(5)
                        s,student_answer_analysis_suggestion = get_student_answer_analysis_suggestion(selected_question)
                        st.session_state[text_key] = student_answer_analysis_suggestion
                        st.session_state[score_key] = s
                        st.experimental_rerun()


if 'student_image' not in st.session_state:
    st.session_state.student_image = None

if 'has_uploaded_student_image' not in st.session_state:
    st.session_state.has_uploaded_student_image = False

def main():

    global selected_question
    if 'selected_question' not in st.session_state:
        st.session_state.selected_question = 1  # 默认显示第一题

    if st.session_state.selected_question is None:
        st.session_state.selected_question = 1  # 默认显示第一题

    st.sidebar.header('题号')
    for i in range(1,get_last_question_number()+1):
        if st.sidebar.button(f'第{i}题', key=f'button_{i}'):
            st.session_state.selected_question = i
    
    content(st.session_state.selected_question)

    button_placeholder = st.sidebar.empty()

    st.write("")  # 添加一个空行

    st.sidebar.markdown("***")  # 添加分隔线

    
    if not st.session_state.has_uploaded_student_image:
        st.session_state.student_image = st.sidebar.file_uploader("批量导入答题卡", type=["zip"], accept_multiple_files=False)
        if st.session_state.student_image is not None:
            with st.spinner('正在解析中……'):
                time.sleep(5)  # 模拟解析过程
                if button_placeholder.button("学情报告分析",key='xueqing'):
                    open_link("http://localhost:8501/three")
                student(st.session_state.selected_question)
                st.session_state.has_uploaded_student_image = True
    else:
        student(st.session_state.selected_question)
        st.session_state.student_image = st.sidebar.file_uploader("批量导入答题卡", type=["zip"], accept_multiple_files=False)
        if button_placeholder.button("学情报告分析",key='xueqing'):
            open_link("http://localhost:8501/three")

    

if __name__ == "__main__":
    main()

    
