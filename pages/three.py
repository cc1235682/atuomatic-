import streamlit as st
import pymysql
import pandas as pd
from io import BytesIO
import base64
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# 学情可视化：学生分数排名
def score_rank():
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='L123456',
        port=3306,
        db='marking_system2',
        charset='utf8'
    )

    # 从class表获取学生姓名和学生ID
    class_query = "SELECT student_name, student_id FROM class"
    class_df = pd.read_sql(class_query, conn)

    # 根据学生ID从score表获取分数
    scores = []
    for student_id in class_df['student_id']:
        score_query = f"SELECT score FROM score WHERE student_id = {student_id}"
        score_df = pd.read_sql(score_query, conn)
        if not score_df.empty:
            scores.append(score_df['score'].values[0])
        else:
            scores.append(None)

    class_df['score'] = scores

    # 去除分数为None的行
    class_df = class_df.dropna()

    # 根据分数降序排序
    class_df = class_df.sort_values(by='score', ascending=False)

    # 生成排名列表
    rank_df = pd.DataFrame({
        '排名': range(1, len(class_df) + 1),
        '学生姓名': class_df['student_name'].tolist(),
        '分数': class_df['score'].round(1).tolist()  # 将分数保留一位小数
    })

    # 生成HTML表格
    html_table = rank_df.to_html(index=False, justify='center', classes='data', escape=False)
    html_table = html_table.replace('<table', '<table style="width: 80%; text-align: center;"')


    # 显示试卷名
    st.write("试卷名： 高一期末政治试卷")

    # 显示排名列表
    st.markdown(html_table, unsafe_allow_html=True)

    # 生成并显示下载按钮
    csv_file = rank_df.to_csv(index=False)
    b64 = base64.b64encode(csv_file.encode()).decode()  # 编码为base64
    href = f'<a href="data:file/csv;base64,{b64}" download="学生成绩.csv">下载表格</a>'
    st.markdown(href, unsafe_allow_html=True)


# 学情可视化：分数段
def score_range():
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='L123456',
            port=3306,
            db='marking_system2',
            charset='utf8'
    )

    query = "SELECT score FROM score "
    df = pd.read_sql(query, conn)

    # 统计各分数段学生数量
    bins = [0, 20, 40, 60, 70, 80, 90, 100]
    labels = ['0-20', '20-40', '40-60', '60-70', '70-80', '80-90', '90-100']
    score_ranges = pd.cut(df['score'], bins=bins, labels=labels, right=False)
    student_counts = score_ranges.value_counts().sort_index()

    # 计算最高分、最低分和平均分
    max_score = df['score'].max()
    min_score = df['score'].min()
    avg_score = df['score'].mean()

    # 计算及格率
    pass_rate = (df['score'] >= 60).mean() * 100

    # 创建矩形图
    fig, ax = plt.subplots()
    bar_plot = ax.bar(student_counts.index, student_counts)

    # 设置标题和轴标签
    ax.set_title('学生成绩分布')
    ax.set_xlabel('分数段')
    ax.set_ylabel('学生数量')

    # 在矩形条上显示人数
    for i, v in enumerate(student_counts):
        ax.text(i, v + 1, str(v), color='black', ha='center')

    # 设置y轴刻度
    plt.yticks([0, 10, 20, 30, 40, 50])

    # 显示最高分、最低分、平均分和及格率，并设置字体大小为12
    plt.text(7.5, 40, f'平均分：{avg_score:.2f}', fontsize=12, ha='left')
    plt.text(7.5, 48, f'最高分：{max_score}', fontsize=12, ha='left')
    plt.text(7.5, 44, f'最低分：{min_score}', fontsize=12, ha='left')
    plt.text(7.5, 36, f'及格率：{pass_rate:.2f}%', fontsize=12, ha='left')

    # 调整图形大小
    plt.gcf().set_size_inches(6, 3)

    # 显示矩形图
    st.pyplot(fig)


def main():
    # 使用CSS来居中显示
    st.markdown("""
        <style>
        .center {
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="center">学情分析报告</h1>', unsafe_allow_html=True)

    st.markdown("***") 
   
    col1, col2 = st.columns([1,2])

    with col1:
        score_rank()
    
    with col2:
        score_range()
    
    
if __name__ == "__main__":
    main()
