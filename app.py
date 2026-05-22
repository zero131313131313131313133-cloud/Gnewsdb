import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
import re
import time

# ---------------------------------
# 기본 설정
# ---------------------------------

st.set_page_config(
    page_title="GNews Dashboard",
    layout="wide"
)

st.title("📰 GNews 실시간 뉴스 대시보드")

# ---------------------------------
# API KEY
# ---------------------------------

API_KEY = "b1d649b7787942b0bd99c985986326aa"

# ---------------------------------
# 사이드바 설정
# ---------------------------------

st.sidebar.header("설정")

# 기본 키워드 Trump
keyword = st.sidebar.text_input(
    "검색 키워드",
    "Trump"
)

country = st.sidebar.selectbox(
    "국가 선택",
    ["us", "kr", "jp"]
)

max_articles = st.sidebar.slider(
    "뉴스 개수",
    10,
    100,
    20
)

run_type = st.sidebar.radio(
    "실행 방식",
    ["1회 실행", "다회 실행"]
)

# ---------------------------------
# 뉴스 가져오기 함수
# ---------------------------------

@st.cache_data(ttl=60)
def get_news(keyword, country, max_articles):

    url = (
        f"https://gnews.io/api/v4/search?"
        f"q={keyword}"
        f"&lang=en"
        f"&country={country}"
        f"&max={max_articles}"
        f"&apikey={API_KEY}"
    )

    response = requests.get(url)

    data = response.json()

    articles = data.get("articles", [])

    return articles

# ---------------------------------
# 실행 버튼
# ---------------------------------

run = st.sidebar.button("뉴스 가져오기")

# ---------------------------------
# 1회 실행
# ---------------------------------

if run_type == "1회 실행":

    if run:

        articles = get_news(
            keyword,
            country,
            max_articles
        )

        if len(articles) == 0:
            st.error("뉴스 데이터를 가져오지 못했습니다.")
            st.stop()

        df = pd.DataFrame(articles)

        # -----------------------------
        # 데이터 출력
        # -----------------------------

        st.subheader("📋 뉴스 데이터")

        st.dataframe(df)

        # -----------------------------
        # 뉴스 출력
        # -----------------------------

        st.subheader("📰 뉴스 목록")

        for article in articles:

            st.markdown(f"### {article['title']}")

            if article.get("image"):
                st.image(article["image"], width=400)

            st.write(article.get("description"))

            st.write(article.get("url"))

            st.write("---")

        # -----------------------------
        # 단어 분석
        # -----------------------------

        st.subheader("🔎 단어 빈도 분석")

        titles = " ".join(
            df["title"].astype(str)
        )

        # 특수문자 제거
        titles = re.sub(
            r"[^a-zA-Z ]",
            "",
            titles
        )

        words = titles.lower().split()

        stopwords = {
            "the", "a", "an", "is", "are",
            "to", "of", "and", "in",
            "on", "for", "with"
        }

        filtered_words = [
            word for word in words
            if word not in stopwords
        ]

        word_count = Counter(filtered_words)

        top_words = pd.DataFrame(
            word_count.most_common(10),
            columns=["word", "count"]
        )

        # -----------------------------
        # 단어 표 출력
        # -----------------------------

        st.subheader("📄 TOP 단어")

        st.dataframe(top_words)

        # -----------------------------
        # 막대 그래프
        # -----------------------------

        st.subheader("📊 단어 빈도 그래프")

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.bar(
            top_words["word"],
            top_words["count"]
        )

        plt.xticks(rotation=45)

        st.pyplot(fig)

        # -----------------------------
        # 워드클라우드
        # -----------------------------

        st.subheader("☁️ 워드클라우드")

        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white"
        ).generate(" ".join(filtered_words))

        fig2, ax2 = plt.subplots(figsize=(12, 6))

        ax2.imshow(wordcloud)

        ax2.axis("off")

        st.pyplot(fig2)

# ---------------------------------
# 다회 실행
# ---------------------------------

elif run_type == "다회 실행":

    refresh_time = st.sidebar.slider(
        "새로고침 간격(초)",
        5,
        60,
        10
    )

    placeholder = st.empty()

    if run:

        while True:

            articles = get_news(
                keyword,
                country,
                max_articles
            )

            if len(articles) == 0:
                st.error("뉴스 데이터를 가져오지 못했습니다.")
                break

            df = pd.DataFrame(articles)

            with placeholder.container():

                st.subheader("🔄 실시간 뉴스 데이터")

                st.dataframe(df)

                st.subheader("📰 최신 뉴스")

                for article in articles[:5]:

                    st.markdown(
                        f"### {article['title']}"
                    )

                    st.write(
                        article.get("description")
                    )

                    st.write(
                        article.get("url")
                    )

                    st.write("---")

            time.sleep(refresh_time)