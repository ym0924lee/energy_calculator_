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
import json # JSON 응답 처리를 위해 추가

# Streamlit 페이지 설정
st.set_page_config(layout="wide", page_title="한국 날씨 & 냉난방 가이드")
st.title("☀️ 한국 날씨 및 냉난방기 사용량 가이드 🌬️")

# --- 1. API 키 로드 ---
try:
    # 환경 변수에서 API 키 로드 시도 (로컬 개발용)
    api_key = st.secrets["WEATHER_API_KEY"]
except KeyError:
    st.error("⚠️ API 키가 설정되지 않았습니다. 'WEATHER_API_KEY' 환경 변수를 설정하거나, '.streamlit/secrets.toml' 파일을 확인해주세요.")
    st.stop() # API 키 없으면 앱 중단

# --- 2. 기상청 API 호출 함수 정의 ---
def get_living_weather_data(api_key, area_no, data_type="JSON"):
    # 기상청_생활기상지수 조회서비스(3.0) - 자외선지수, 대기정체지수, 여름철 체감온도
    # API 문서에 따라 적절한 서비스 URL 및 파라미터 구성
    # 여기서는 '자외선지수', '대기정체지수', '대상환경별 여름철 체감온도'를 모두 가져올 수 있도록 일반화
    # 각 지수별 API 엔드포인트가 다를 수 있으니, 필요시 함수를 분리하거나 if/else로 처리 필요

    # 예시 URL (API 문서에 따라 정확히 맞춰야 함)
    # 실제 API는 서비스별로 URL이 다를 수 있습니다. 이 예시는 하나의 통합된 URL을 가정합니다.
    # 기상청 API 문서에서 '자외선지수', '대기정체지수', '대상환경별 여름철 체감온도'의 정확한 엔드포인트를 확인하세요.
    
    # 🚨 중요: 아래 URL과 서비스 키 파라미터는 예시입니다.
    #         기상청 생활기상지수 조회서비스(3.0)의 각 지수별 정확한 요청 URL과 파라미터 이름을 API 문서에서 확인하세요.
    #         예시: 자외선지수 (getUVIdx), 대기정체지수 (getAirPollutionIdx), 대상환경별 여름철 체감온도 (getAftmHoliIdx)
    
    # 실제 API는 지수별로 서비스가 나뉘어 있을 가능성이 큽니다.
    # 예를 들어, 자외선지수는 getUVIdx, 대기정체지수는 getAirPollutionIdx 등.
    # 따라서 각 지수별로 API 호출 함수를 따로 만들거나, 하나의 함수 내에서 조건부로 URL을 바꿔야 할 수 있습니다.

    base_url = "http://apis.data.go.kr/1360000/LivingAndHealthWeatherStats/"
    
    endpoints = {
        "자외선지수": "getUVIdx",
        "대기정체지수": "getAirPollutionIdx",
        "여름철 체감온도": "getAftmHoliIdx" # API 문서에 정확한 이름 확인 필요
    }
    
    results = {}
    
    for key, endpoint in endpoints.items():
        url = f"{base_url}{endpoint}"
        params = {
            'serviceKey': api_key,
            'dataType': data_type,
            'areaNo': area_no, # 지역 코드
            'time': '202506101800' # 현재 시간 기준으로 변경해야 함. YYYYMMDDHHMM 형식.
                                    # 이 예시는 고정된 값입니다. 실제로는 현재 시간을 동적으로 생성해야 합니다.
                                    # from datetime import datetime / datetime.now().strftime("%Y%m%d%H%M")
            # 추가 파라미터가 있을 수 있음 (예: date, hour 등)
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status() # HTTP 오류 발생 시 예외 발생

            data = response.json()
            
            # API 응답 구조에 따라 데이터 추출
            # 예시: items.item 리스트 안에 데이터가 있다고 가정
            if 'response' in data and 'body' in data['response'] and 'items' in data['response']['body']:
                items = data['response']['body']['items']['item']
                if items:
                    # 가장 최근 또는 첫 번째 아이템의 정보 추출
                    results[key] = items[0] 
                else:
                    results[key] = {"message": f"'{key}' 데이터 없음"}
            else:
                results[key] = {"message": f"'{key}' 응답 구조 오류 또는 데이터 없음"}

        except requests.exceptions.RequestException as e:
            results[key] = {"error": f"'{key}' 정보를 가져오는 중 오류 발생: {e}"}
        except json.JSONDecodeError:
            results[key] = {"error": f"'{key}' 응답 JSON 디코딩 오류. 응답 내용: {response.text}"}
            
    return results

# --- 3. 지역 코드 매핑 (예시) ---
# 실제 기상청 생활기상지수 API의 'areaNo'에 맞는 지역 코드를 정확히 확인해야 합니다.
# 읍/면/동 단위까지는 API가 지원하지 않을 수 있으며, 시/군 단위까지만 지원할 수도 있습니다.
# 기상청 API 문서에서 제공하는 '지역코드' 표를 참조하여 정확한 코드를 입력해야 합니다.
korea_area_codes = {
    "서울": "11B10101",
    "부산": "11H20201",
    "대구": "11H10701",
    "인천": "11B20201",
    "광주": "11F20501",
    "대전": "11C20401",
    "울산": "11H20101",
    "세종": "11C20404", # 세종은 대전 기상청 관할일 가능성 있음
    "경기": "11B00000", # 경기도 전체를 나타내는 코드 (만약 있다면)
    "강원": "11C00000",
    "충북": "11C10000",
    "충남": "11C20000",
    "전북": "11F10000",
    "전남": "11F20000",
    "경북": "11H10000",
    "경남": "11H20000",
    "제주": "11G00000",
    # 실제 기상청 API 지역 코드로 업데이트 필요
}

# --- 4. Streamlit UI 구성 ---
st.header("🏡 1. 위치 선택")

selected_city_name = st.selectbox(
    "거주하시는 도시를 선택해주세요:",
    list(korea_area_codes.keys()),
    index=list(korea_area_codes.keys()).index("서울") # 기본값 서울
)

selected_area_code = korea_area_codes[selected_city_name]

if st.button("날씨 정보 및 냉난방 가이드 보기"):
    with st.spinner(f"'{selected_city_name}'의 날씨 정보를 가져오는 중입니다..."):
        weather_info = get_living_weather_data(api_key, selected_area_code)

    if weather_info:
        st.success(f"✔️ '{selected_city_name}' 날씨 정보 로드 완료!")
        
        st.subheader(f"✨ 2. {selected_city_name} 생활 기상 지수")
        
        # 자외선지수 표시
        if "자외선지수" in weather_info and 'value' in weather_info["자외선지수"]:
            uv_index = weather_info["자외선지수"]['value'] # 실제 필드명 확인
            uv_grade = ""
            if 0 <= uv_index <= 2: uv_grade = "낮음"
            elif 3 <= uv_index <= 5: uv_grade = "보통"
            elif 6 <= uv_index <= 7: uv_grade = "높음"
            elif 8 <= uv_index <= 10: uv_grade = "매우 높음"
            else: uv_grade = "위험"
            st.metric(label="☀️ 자외선 지수", value=f"{uv_index} ({uv_grade})")
            if uv_grade in ["높음", "매우 높음", "위험"]:
                st.info("선크림, 선글라스, 모자 등을 착용하고 외출을 자제하는 것이 좋아요.")
        elif "자외선지수" in weather_info and "message" in weather_info["자외선지수"]:
            st.warning(f"자외선 지수: {weather_info['자외선지수']['message']}")
        elif "자외선지수" in weather_info and "error" in weather_info["자외선지수"]:
            st.error(f"자외선 지수 오류: {weather_info['자외선지수']['error']}")

        # 대기정체지수 표시 (API 문서에 따라 필드명과 값 범위 확인 필요)
        if "대기정체지수" in weather_info and 'value' in weather_info["대기정체지수"]:
            air_stagnation_index = weather_info["대기정체지수"]['value'] # 실제 필드명 확인
            st.metric(label="🏭 대기 정체 지수", value=f"{air_stagnation_index}")
            if air_stagnation_index >= 50: # 예시 기준
                st.warning("대기가 정체되어 미세먼지 농도가 높아질 수 있습니다. 마스크 착용 및 환기에 주의하세요.")
        elif "대기정체지수" in weather_info and "message" in weather_info["대기정체지수"]:
            st.warning(f"대기 정체 지수: {weather_info['대기정체지수']['message']}")
        elif "대기정체지수" in weather_info and "error" in weather_info["대기정체지수"]:
            st.error(f"대기 정체 지수 오류: {weather_info['대기정체지수']['error']}")

        # 여름철 체감온도 표시 (API 문서에 따라 필드명과 값 범위 확인 필요)
        if "여름철 체감온도" in weather_info and 'value' in weather_info["여름철 체감온도"]:
            felt_temperature = weather_info["여름철 체감온도"]['value'] # 실제 필드명 확인
            st.metric(label="🥵 여름철 체감온도", value=f"{felt_temperature}°C")

            st.subheader("💡 3. 냉난방기 적정 사용량 가이드")
            if felt_temperature >= 33: # 매우 더운 날
                st.markdown("**🔥 폭염 주의! 냉방기 가동 필수!**")
                st.info("실내 온도를 26°C 이하로 유지하여 온열 질환을 예방하세요. 충분한 수분 섭취도 중요해요.")
                st.caption("과도한 냉방은 건강에 해로울 수 있으니, 실내외 온도 차이를 5°C 내외로 유지하는 것이 좋습니다.")
            elif felt_temperature >= 28: # 더운 날
                st.markdown("**🥵 더위 예상! 냉방기 사용 권장!**")
                st.info("실내 온도를 26~28°C로 설정하여 쾌적함을 유지하세요. 선풍기와 함께 사용하면 더 효율적이에요.")
            elif felt_temperature <= 10: # 매우 추운 날 (여름철에는 거의 없을 수 있음)
                st.markdown("**🥶 추위 예상! 난방기 사용 고려!**")
                st.info("실내 온도를 20~22°C로 유지하여 체온을 보호하세요. 따뜻한 옷차림도 중요합니다.")
            else:
                st.markdown("**🍃 쾌적한 날씨! 냉난방기 사용 자제!**")
                st.info("환기를 통해 실내 공기를 순환시키고, 자연 바람을 활용하여 에너지 절약에 동참하세요.")
        elif "여름철 체감온도" in weather_info and "message" in weather_info["여름철 체감온도"]:
            st.warning(f"여름철 체감온도: {weather_info['여름철 체감온도']['message']}")
            st.subheader("💡 3. 냉난방기 적정 사용량 가이드")
            st.info("체감온도 정보를 가져올 수 없어 일반적인 가이드를 제공합니다.")
            st.write("26°C 이상의 기온에서는 냉방기를, 20°C 이하의 기온에서는 난방기를 사용하는 것을 고려해 보세요.")
        elif "여름철 체감온도" in weather_info and "error" in weather_info["여름철 체감온도"]:
            st.error(f"여름철 체감온도 오류: {weather_info['여름철 체감온도']['error']}")
            st.subheader("💡 3. 냉난방기 적정 사용량 가이드")
            st.info("체감온도 정보를 가져올 수 없어 일반적인 가이드를 제공합니다.")
            st.write("26°C 이상의 기온에서는 냉방기를, 20°C 이하의 기온에서는 난방기를 사용하는 것을 고려해 보세요.")
            
    else:
        st.error("😭 날씨 정보를 가져오지 못했습니다. 잠시 후 다시 시도해주세요.")
        st.info("API 키, 네트워크 연결, 또는 기상청 API 서버 상태를 확인해 주세요.")

st.markdown("---")
st.caption("💡 본 가이드는 기상청 생활기상지수 데이터를 기반으로 하며, 개인의 체감 및 환경에 따라 다를 수 있습니다.")
