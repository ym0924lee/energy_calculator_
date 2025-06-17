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

st.title("💡가정용 에너지 + 체감온도 정보")




# 한국 기상청 체감온도 API 연결
import streamlit as st
import requests
import xml.etree.ElementTree as ET

st.title("💡가정용 에너지 + 체감온도 정보")

# ------------------------------------------------------------------------------
# 1️⃣한국 기상청 생활지수 API 연결
# ------------------------------------------------------------------------------
API_KEY_KMA = "<너의_기상청_api_key>"

# API 정보
areaNo = "1100000000"  # 서울
time = "2021070618"    # base time
pageNo = 1
numOfRows = 10
dataType = "XML"

API_URL_KMA = f"https://apihub.kma.go.kr/api/typ02/openApi/LivingWthrIdxServiceV3/getSenTaIdxV3?numOfRows={numOfRows}&pageNo={pageNo}&dataType={dataType}&areaNo={areaNo}&time={time}&requestCode=A41&authKey={API_KEY_KMA}"

# API 요청
resp = requests.get(API_URL_KMA)
resp.raise_for_status()

# ------------------------------------------------------------------------------
# 2️⃣ XML 파서로 체감온도 파싱
# ------------------------------------------------------------------------------
root = ET.fromstring(resp.text)

current_feeltemp = None

for item in root.iter("item"):
    idx = item.find("sensationIdx").text
    if idx is not None:
        current_feeltemp = float(idx)
        break

if current_feeltemp is not None:
    st.write(f"✅ 현재 체감온도: {current_feeltemp}℃")

    # ------------------------------------------------------------------------------
    # 3️⃣에너지 사용 권고
    # ------------------------------------------------------------------------------
    if current_feeltemp >= 30:
        st.error("🔥 체감온도가 아주 높은 상태이에요.")
        st.write("✅ 에어컨 세기를 줄이는 것보다 실내온도의 26°C를 유지해주세요.")
        st.write("✅ 실내에서 선풍기도 함께 사용할 수 있습니다.")
    elif current_feeltemp < 10:
        st.error("❄ 체감온도가 아주 낮아요.")
        st.write("✅ 실내 난방을 20°C로 맞추고, 웃옷이나 이불로 체온을 보호해주세요.")
    else:
        st.success("✨ 체감온도가 쾌적합니다.")
        st.write("✅ 실내 온도는 22°C~24°C로 유지해주세요.")
        st.write("✅ 에너지 낭비가 없습니다.")
else:
    st.error("⚡ 현재 체감온도 데이터를 가져올 수 없습니다.")
    st.write("✅ API키, areaNo, time 등을 확인해주세요.")
