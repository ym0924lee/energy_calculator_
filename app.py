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
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime, timedelta

# --- API 설정 ---
# 한국환경공단 탄소중립포인트 에너지 사용량 정보 API의 서비스 URL
# 이 URL은 예시입니다. 반드시 데이터 포털에서 정확한 URL을 확인해서 변경해야 합니다!
# (예: https://www.data.go.kr/data/15082728/openapi.do 페이지에서 '활용가이드'나 'API 호출' 예시 확인)
API_BASE_URL = "http://apis.data.go.kr/B553123/CarbonPointService/getEnergyUsageList"

# --- 한글 폰트 설정 (선택 사항: 그래프에 한글이 깨질 때) ---
# 로컬에서 테스트할 때 시스템 폰트를 사용합니다.
# Streamlit Cloud에 배포할 때는 한글 폰트가 없을 수 있으므로,
# 해당 폰트 설정 부분을 제거하거나 Streamlit Cloud용 폰트 설정을 참고하세요.
try:
    # 맑은 고딕 (Windows), AppleGothic (Mac) 등 본인 OS에 맞는 폰트 설정
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지
except:
    st.warning("한글 폰트 설정에 실패했습니다. 그래프에 한글이 깨져 보일 수 있습니다.")


# --- API 데이터 가져오기 함수 ---
@st.cache_data(ttl=3600) # 1시간 동안 데이터를 캐싱하여 불필요한 API 호출 방지
def get_energy_data(api_key, start_date, end_date):
    params = {
        "serviceKey": api_key,
        "startDate": start_date,
        "endDate": end_date,
        "pageNo": 1,
        "numOfRows": 100, # 가져올 데이터 개수 (API 제한에 따라 조절)
        "_type": "json"   # JSON 형식으로 응답 요청
    }
    
    try:
        response = requests.get(API_BASE_URL, params=params, timeout=10)
        response.raise_for_status() # HTTP 오류가 발생하면 예외 발생

        data = response.json()
        
        # API 응답 구조에 따라 데이터 추출 방식이 달라집니다.
        # 한국환경공단 API는 보통 response -> body -> items -> item 경로에 실제 데이터가 있습니다.
        if 'response' in data and 'body' in data['response'] and \
           'items' in data['response']['body'] and data['response']['body']['items']:
            
            items = data['response']['body']['items']['item']
            
            # API 응답이 단일 항목일 경우 리스트로 감싸기 (pandas DataFrame 변환을 위해)
            if not isinstance(items, list):
                items = [items]

            df = pd.DataFrame(items)
            
            # 필요한 컬럼만 선택하고, 날짜 및 숫자 형식으로 변환 (컬럼명은 API 문서 확인)
            # 예시: 'registDt' (등록일자), 'electUseQty' (전기 사용량)
            # 실제 API 응답 컬럼명으로 변경해야 합니다.
            if 'registDt' in df.columns:
                df['registDt'] = pd.to_datetime(df['registDt'], format='%Y%m%d', errors='coerce')
                df = df.dropna(subset=['registDt']) # 날짜 변환 실패 행 제거

            if 'electUseQty' in df.columns:
                df['electUseQty'] = pd.to_numeric(df['electUseQty'], errors='coerce')
                df = df.dropna(subset=['electUseQty']) # 숫자 변환 실패 행 제거

            return df.copy() # 원본 데이터프레임 복사본 반환
        
        elif 'response' in data and 'header' in data['response'] and data['response']['header']['resultCode'] != '00':
            st.warning(f"API 응답 오류: {data['response']['header']['resultMsg']} (코드: {data['response']['header']['resultCode']})")
            return pd.DataFrame() # 빈 데이터프레임 반환
        else:
            st.warning("API 응답에 데이터가 없거나 예상치 못한 형식입니다.")
            st.json(data) # 디버깅을 위해 원본 응답 출력
            return pd.DataFrame()

    except requests.exceptions.RequestException as e:
        st.error(f"API 요청 중 오류 발생: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"데이터 처리 중 예상치 못한 오류 발생: {e}")
        return pd.DataFrame()

# --- Streamlit 앱 메인 UI ---
st.title("💡 탄소중립포인트 에너지 사용량 정보")
st.markdown("한국환경공단 API를 통해 에너지 사용량 데이터를 조회합니다.")

# 사이드바에서 API 키 가져오기
try:
    API_KEY = st.secrets["carbon_point_api_key"]
except KeyError:
    st.error("`secrets.toml` 파일에 API 키가 설정되지 않았습니다. `.streamlit/secrets.toml`을 확인해주세요.")
    st.stop() # 키 없으면 앱 중단

# 날짜 선택 위젯
today = datetime.now().date()
default_start_date = today - timedelta(days=365) # 기본 1년치 데이터

start_date_input = st.date_input("시작일", value=default_start_date)
end_date_input = st.date_input("종료일", value=today)

# '데이터 조회' 버튼
if st.button("데이터 조회"):
    # 날짜 유효성 검사
    if start_date_input > end_date_input:
        st.error("시작일은 종료일보다 이전 날짜여야 합니다.")
    else:
        # 날짜를 YYYYMMDD 형식 문자열로 변환
        start_date_str = start_date_input.strftime("%Y%m%d")
        end_date_str = end_date_input.strftime("%Y%m%d")

        with st.spinner("데이터를 불러오는 중..."):
            df_energy = get_energy_data(API_KEY, start_date_str, end_date_str)

        if not df_energy.empty:
            st.success(f"총 {len(df_energy)}건의 데이터를 불러왔습니다.")
            
            st.subheader("데이터 미리보기")
            st.dataframe(df_energy.head()) # 데이터프레임 상단 5행 표시

            # 그래프 그리기 (예시: 날짜별 전기 사용량)
            # 실제 컬럼명에 따라 'registDt'와 'electUseQty'를 변경해야 합니다.
            if 'registDt' in df_energy.columns and 'electUseQty' in df_energy.columns:
                st.subheader("월별 전기 사용량 추이")
                
                # 월별로 집계
                df_energy['year_month'] = df_energy['registDt'].dt.to_period('M').astype(str)
                monthly_usage = df_energy.groupby('year_month')['electUseQty'].sum().reset_index()

                fig, ax = plt.subplots(figsize=(10, 5))
                ax.bar(monthly_usage['year_month'], monthly_usage['electUseQty'], color='lightgreen')
                ax.set_xlabel("년월")
                ax.set_ylabel("전기 사용량 (kWh)")
                ax.set_title("월별 전기 사용량")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("그래프를 그릴 수 있는 'registDt' 또는 'electUseQty' 컬럼이 없습니다. API 응답의 컬럼명을 확인해주세요.")
                st.json(df_energy.columns.tolist()) # 현재 데이터프레임의 컬럼 목록 출력
        else:
            st.warning("데이터를 가져오지 못했거나 조회된 데이터가 없습니다.")

else:
    st.info("시작일과 종료일을 선택하고 '데이터 조회' 버튼을 눌러주세요.")
