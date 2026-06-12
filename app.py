import sqlite3
import pandas as pd
import streamlit as st


# 1. 데이터베이스 및 테이블 생성, 초기 데이터 삽입 함수
def init_db():
    conn = sqlite3.connect("./db/scoreDB.db")
    cursor = conn.cursor()

    # score 테이블 생성 (국어: k, 영어: e, 컴퓨터: c)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS score (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            k INTEGER NOT NULL,
            e INTEGER NOT NULL,
            c INTEGER NOT NULL
        )
    """)

    # 기존 데이터가 없을 때만 임의의 학생 레코드 10개 삽입
    cursor.execute("SELECT COUNT(*) FROM score")
    if cursor.fetchone()[0] == 0:
        initial_students = [
            ("김철수", 85, 90, 95),
            ("이영희", 92, 88, 84),
            ("박민수", 78, 65, 70),
            ("최지우", 95, 100, 92),
            ("정다민", 60, 55, 68),
            ("강하늘", 88, 82, 90),
            ("윤서준", 72, 75, 80),
            ("한소희", 98, 96, 94),
            ("오지호", 50, 60, 55),
            ("임윤아", 83, 87, 89),
        ]
        cursor.executemany(
            "INSERT INTO score (name, k, e, c) VALUES (?, ?, ?, ?)",
            initial_students,
        )
        conn.commit()

    conn.close()


# 2. 학점 계산 함수
def calculate_grade(average):
    if average >= 90:
        return "A"
    elif average >= 80:
        return "B"
    elif average >= 70:
        return "C"
    elif average >= 60:
        return "D"
    else:
        return "F"


# 3. DB 데이터 조회 및 가공 함수
def get_scores():
    conn = sqlite3.connect("./db/scoreDB.db")
    query = "SELECT name, k, e, c FROM score"
    df = pd.read_sql_query(query, conn)
    conn.close()

    # 총점, 평균, 학점 계산하여 컬럼 추가
    df["총점"] = df["k"] + df["e"] + df["c"]
    df["평균"] = (df["총점"] / 3).round(2)
    df["학점"] = df["평균"].apply(calculate_grade)

    # 컬럼명 직관적으로 변경
    df.rename(
        columns={"name": "이름", "k": "국어(K)", "e": "영어(E)", "c": "컴퓨터(C)"},
        inplace=True,
    )

    return df


# --- Streamlit 앱 메인 실행부 ---
def main():
    st.set_page_config(page_title="학생 성적 관리 시스템", layout="wide")

    st.title("📊 학생 성적 관리 프로그램")
    st.markdown("SQLite3 데이터베이스에서 학생 정보를 읽어와 총점, 평균, 학점을 계산함.")
    st.write("---")

    # DB 초기화
    init_db()

    # 데이터 가져오기
    try:
        score_df = get_scores()

        # 상단 통계 지표 대시보드
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="총 학생 수", value=f"{len(score_df)}명")
        with col2:
            st.metric(label="전체 평균", value=f"{score_df['평균'].mean():.2f}점")
        with col3:
            st.metric(
                label="최고 득점자",
                value=f"{score_df.loc[score_df['총점'].idxmax(), '이름']} ({score_df['총점'].max()}점)",
            )

        st.write("")

        # 성적 데이터 테이블 출력
        st.subheader("📋 성적 리스트")
        # 정렬 기준 선택
        sort_order = st.selectbox(
            "총점 정렬 기준",
            ("내림차순", "오름차순")
        )
        
        # 선택한 기준에 따라 정렬
        if sort_order == "내림차순":
            score_df = score_df.sort_values(by="총점", ascending=False).reset_index(drop=True)
        else:
            score_df = score_df.sort_values(by="총점", ascending=True).reset_index(drop=True)
            
        # 순위 컬럼을 가장 왼쪽(첫 번째)에 추가
        score_df.insert(0, "순위", range(1, len(score_df) + 1))
        st.dataframe(score_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류 발생: {e}")


if __name__ == "__main__":
    main()