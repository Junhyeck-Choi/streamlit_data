# streamlit_data
도시 데이터 분석학교 5기 streamlit 프로젝트 예시입니다!\
링크 : http://urbandata.streamlit.app/

**제작방법**
  1. 깃허브에 로그인한다
  2. repository를 생성한다 (README.md 생성 클릭)
  3. repository에 시각화하고자 하는 데이터 (daily_emergency.csv)를 업로드 하면서 data 폴더를 생성한다
  4. chatgpt 등 생성형 ai를 이용하여 app.py, requirements.txt, 01_bar.py 02_pie.py를 생성한다.
  5. app.py, requirements.txt는 repository에 바로 업로드 한다.
  6. 01_bar.py 02_pie.py는 pages 폴더를 생성하면서 업로드 한다.
  7. streamlit에 가서 반영을 확인한다 (페이지 생성 시 우측 하단 Manage app > ... > reboot app)

**프롬프트 생성 예시**

(i) app.py, requirements.txt 생성하기
>첨부한 데이터 파일(daily_emergency.csv)을 바탕으로 streamlit에서 그래프를 시각화할 수 있는 python 코드(.py 형태)를 짜줘 github에 올려서 streamlit으로 앱을 실행할거야
>
>배경설명 : 데이터는 2020년 1월 1일부터 2022년 12월 31일 까지 서울 지역의 증상 별 응급출동 횟수야. 각 날짜가 행으로 들어가있고, 열에는 증상 별 횟수가 들어가있어
>
>지시 : 나는 pandas 라이브러리를 사용해서 데이터를 읽고 plotly 라이브러리를 사용해서 증상 별 출동 횟수를 line 그래프로 시각화하는 페이지를 만들고 싶어. x축은 날짜고, y축은 출동횟수야.
>
>제약조건 : 상단에 증상별 버튼이 있어서 toggle 하면 증상 별 그래프가 on/off 되도록 해줘. 데이터는 data 폴더 내에 위치해있어 ('./data/daily_emergency.csv), requirement.txt도 같이 만들어줘

(ii) 01_bar.py 02_pie.py 생성하기 (하부 페이지 만들기)
>배경설명 : 나는 streamlit 하부 페이지에 01_bar.py 02_pie.py를 가진 파일로 2개의 페이지를 생성하고 싶어
>
>지시 1 : 먼저 01_bar.py는 날짜를 상단에서 입력하면, 해당 날짜에 해당하는 증상 별 출동 건수를 bar 그래프로 시각화하는 페이지를 만들어줘. x축은 증상 명, y축은 출동 건수야
>
>지시 2 : 02_pie.py는 날짜를 상단에서 입력하면, 해당 날짜에 해당하는 증상 별 출동 건수 비율을 pie 그래프로 시각화하는 페이지를 만들어줘
>
>제약사항 : 시각화는 plotly 패키지를 사용해줘
