import streamlit as st

# -------------------------------------
# 앱 제목 및 설명
# -------------------------------------
st.title("💡 가정용 전기 소비 계산기")
st.write("전자제품의 사용 시간과 소비 전력을 입력하면 하루 및 한 달 전기요금을 계산할 수 있어요!")

# -------------------------------------
# 전자제품 기본 소비 전력 사전 (W 단위)
# -------------------------------------
default_device_power = {
    "에어컨": 1500,
    "냉장고": 200,
    "TV": 100,
    "세탁기": 500,
    "컴퓨터": 300,
    "전자레인지": 1000
}

# -------------------------------------
# 사용자 입력: 제품 선택 및 소비 전력
# -------------------------------------
st.subheader("1️⃣ 사용 정보를 입력하세요")

# 전자제품 선택
device = st.selectbox("사용하는 전자제품을 선택하세요:", list(default_device_power.keys()))

# 절전모드 여부 선택
power_saving = st.checkbox("절전모드 사용 중인가요? (소비 전력 30% 절감)", value=False)

# 기본 소비 전력 불러오기
default_power = default_device_power[device]

# 사용자 소비 전력 입력 (기본값 제공)
custom_power = st.number_input(
    "제품의 소비 전력을 입력하세요 (단위: W)",
    min_value=10,
    max_value=10000,
    value=default_power,
    step=10
)

# 절전모드 적용
if power_saving:
    custom_power *= 0.7  # 소비 전력 30% 절감

# 하루 평균 사용 시간
hours_per_day = st.slider("하루 사용 시간 (시간 단위)", 0.0, 24.0, 1.0, step=0.5)

# 한 달 사용 일수
days_per_month = st.slider("한 달 동안 사용한 일수", 1, 31, 30)

# -------------------------------------
# 요금 단가 및 계산
# -------------------------------------
unit_price = 130  # 원/kWh

# W → kW 단위로 변환
power_kw = custom_power / 1000

# 하루 및 한 달 전력량 계산
daily_energy = power_kw * hours_per_day
monthly_energy = daily_energy * days_per_month
monthly_cost = monthly_energy * unit_price

# -------------------------------------
# 결과 출력
# -------------------------------------
st.subheader("💰 결과")

st.write(f"📌 전자제품: **{device}**")
st.write(f"🔋 하루 사용 전력: **{daily_energy:.2f} kWh**")
st.write(f"📅 한 달 사용 전력: **{monthly_energy:.2f} kWh**")
st.write(f"💸 예상 전기요금: **{monthly_cost:,.0f} 원**")

# 절전모드 메시지
if power_saving:
    st.success("✅ 절전모드가 적용되어 소비 전력이 30% 감소했어요!")

# -------------------------------------
# 친환경 절전 팁
# -------------------------------------
st.markdown("---")
st.subheader("🌱 절전 팁")
if device == "에어컨":
    st.info("✅ 에어컨은 26°C 이상으로 설정하고, 선풍기와 병행하면 전기 절약에 좋아요.")
elif device == "냉장고":
    st.info("✅ 냉장고 문을 자주 여닫지 않고, 적정 온도를 유지하세요.")
elif device == "TV":
    st.info("✅ 사용하지 않을 때는 플러그를 뽑아두면 대기전력을 줄일 수 있어요.")
else:
    st.info("✅ 사용 후 전원을 끄고, 대기 전력을 줄이면 환경과 전기요금 모두 아낄 수 있어요.")




import streamlit as st
import requests
import xml.etree.ElementTree as ET

# Streamlit 제목
st.title("🌫️ 현재 대기오염 정보 - 포항시")

# API키 (너의 API키를 이곳에 넣어줘)
API_KEY = st.secrets['secret_key']

# API 정보
API_URL = 'https://apis.data.go.kr/5020000/pohangArpltnEnvrn'

# API 파리메터
params = {
    "serviceKey": API_KEY,
    "returnType": "xml",
    "numOfRows": 10,
    "pageNo": 1,
    "sidoName": "경상북도",
    "stationName": "포항시",
}

# API 요청
response = requests.get(API_URL, params=params)

if response.status_code == 200:
    # XML 파서로 파싱
    root = ET.fromstring(response.content)
    items = root.findall('.//item')

    if not items:
        st.error("데이터가 없습니다.")
    else:
        st.success("데이터를 가져왔습니다.")
        for item in items:
            station_name = item.findtext("stationName")
            pm10 = item.findtext("pm10Value")
            pm25 = item.findtext("pm25Value")
            o3 = item.findtext("o3Value")
            no2 = item.findtext("no2Value")
            co = item.findtext("coValue")
            so2 = item.findtext("so2Value")

            st.write(f"**측정소**: {station_name}")
            st.write(f"- 미세먼지(PM10): {pm10} ㎍/㎥")
            st.write(f"- 초미세먼지(PM2.5): {pm25} ㎍/㎥")
            st.write(f"- 오존 (O₃): {o3} ppm")
            st.write(f"- 이산화질소 (NO₂): {no2} ppm")
            st.write(f"- 일산화탄소 (CO): {co} ppm")
            st.write(f"- 아황산가스 ( SO₂): {so2} ppm")
            st.write("-------------------------")

else:
    st.error("API 요청 중 오류가 발생되었습니다.")
