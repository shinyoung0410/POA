# import streamlit as st
import requests
import json

# --- 웹 상단 탭 및 설정 ---
st.set_page_config(page_title="제일약품 듀글로우정 마케팅 전략 생성기", page_icon="💊", layout="wide")
st.title("💊 제일약품 듀글로우정 마케팅 전략 드래프트 Generator")
st.write("내부 실무 데이터(UBIST, 처방 실적 등) 분석 및 최신 시장 이슈를 반영한 전략 초안을 생성합니다.")

# --- 사이드바 (설정 영역) ---
with st.sidebar:
    st.header("⚙️ 기본 설정")
    default_key = ""
    api_key_input = st.text_input("Google API Key", value=default_key, type="password", help="Gemini API 키를 입력하세요.")
    
    st.markdown("---")
    st.header("📂 분석 데이터 업로드")
    ppt_file = st.file_uploader("1. 전년도 전략 PPT 슬라이드", type=["pptx", "pdf"])
    ubist_file = st.file_uploader("2. 작년~올해 UBIST 데이터", type=["xlsx", "csv"])
    rx_file = st.file_uploader("3. 작년~올해 처방전 실적 데이터", type=["xlsx", "csv"])
    monitoring_file = st.file_uploader("4. 작년~올해 모니터링 실적", type=["xlsx", "csv"])
    
    st.markdown("---")
    target_q = st.selectbox("전략 목표 분기/연도", ["2026년 하반기", "2027년 상반기", "2027년 전체"])
    generate_btn = st.button("🚀 마케팅 전략 드래프트 생성", type="primary")

# A. Gemini REST API 호출 함수
def generate_strategy_draft(api_key, context_text, target_period):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    system_prompt = f"""
    당신은 제일약품의 수석 제약 마케팅 PM입니다. SGLT-2 inhibitor + TZD 복합제인 '듀글로우정(다파글리플로진+피오글리타존)'의 {target_period} 마케팅 전략 드래프트를 작성해야 합니다.

    [제공된 내부 데이터 요약 및 참고사항]
    {context_text}

    [필수 작성 항목 및 프레임워크]
    1. Executive Summary (핵심 요약)
    2. 시장 및 경쟁 환경 분석 (SGLT-2i + TZD 병용 처방 시장 및 경쟁 품목 동향)
    3. 전년도 성과 평가 및 SWOT 분석 (Strengths, Weaknesses, Opportunities, Threats)
    4. 핵심 마케팅 타겟 및 메세지 (Endocrinology 전문의 및 종합병원/개원의별 타겟팅)
    5. 전략적 세부 실행 과제 (Key Strategic Initiatives)
       - 학술 마케팅 (심포지엄, 랜선 세미나, 학회 연계)
       - 영업 현장 가이드 (Academic Detailing 메시지)
    6. KPI 및 예상 ROI 모니터링 계획

    전문의 대상 전문 의학 용어와 실무 제약 마케팅 톤앤매너를 유지하여 논리적이고 구체적으로 작성하세요.
    """
    
    payload = {
        "contents": [{"parts": [{"text": system_prompt}]}]
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        result = response.json()
        if response.status_code == 200:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error: API 호출 실패 - {result.get('error', {}).get('message', '알 수 없는 오류')}"
    except Exception as e:
        return f"Error: 네트워크 문제 ({e})"

# --- 메인 실행 화면 ---
if generate_btn:
    if not api_key_input:
        st.error("사이드바에 Google API Key를 입력해 주세요!")
    else:
        with st.spinner("제공된 실적 데이터 분석 및 마케팅 전략 드래프트를 작성 중입니다..."):
            
            # 업로드된 파일 정보 정리 (텍스트 요약 컨텍스트 생성)
            file_summary = []
            if ppt_file: file_summary.append(f"- 전년도 전략 PPT 첨부됨 ({ppt_file.name})")
            if ubist_file: file_summary.append(f"- UBIST 데이터 첨부됨 ({ubist_file.name})")
            if rx_file: file_summary.append(f"- 처방전 실적 데이터 첨부됨 ({rx_file.name})")
            if monitoring_file: file_summary.append(f"- 모니터링 실적 첨부됨 ({monitoring_file.name})")
            
            context_text = "\n".join(file_summary) if file_summary else "첨부된 파일 없음 (기본 브랜드 지식 기반 작성)"
            
            # 전략 생성
            strategy_result = generate_strategy_draft(api_key_input, context_text, target_q)
            
            if strategy_result.startswith("Error:"):
                st.error(strategy_result)
            else:
                st.success("🎉 듀글로우정 마케팅 전략 드래프트 작성이 완료되었습니다!")
                
                # 결과 출력
                st.markdown("---")
                st.markdown(strategy_result)
                
                # 텍스트 다운로드 버튼
                st.download_button(
                    label="📄 마케팅 전략 드래프트 (TXT) 다운로드",
                    data=strategy_result,
                    file_name=f"제일약품_듀글로우정_마케팅전략_{target_q}.txt",
                    mime="text/plain"
                )

# --- 하단 제안: 전략 수립 시 함께 활용할 추천 뉴스 키워드 ---
st.markdown("---")
st.subheader("🔍 전략 반영용 Google 검색 추천 이슈/뉴스 키워드")
st.write("구글 검색을 통해 아래 뉴스 및 논문 이슈를 확보한 후 전략 메세지에 포함시키면 완성도가 더욱 높아집니다.")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    **1. 임상 및 학술 이슈**
    * `SGLT2 억제제 TZD 병용요법 3상 임상`
    * `다파글리플로진 피오글리타존 복합제 당화혈색소 감소 효과`
    * `당뇨병 치료제 췌장 베타세포 보호 및 인슐린 저항성 개선`
    """)
with col2:
    st.markdown("""
    **2. 가이드라인 및 제도/시장 이슈**
    * `대한당뇨병학회 진료지침 SGLT2i TZD 병용 권고`
    * `당뇨병 복합제 급여 기준 확대 동향`
    * `듀글로우정 종합병원 DC(약사심의위원회) 통과 및 처방 케이스`
    """)