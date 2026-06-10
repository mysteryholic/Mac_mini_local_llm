import streamlit as st
import json
import os
from jinja2 import Template

# Streamlit 페이지 설정
st.set_page_config(page_title="로컬 LLM 가이드", layout="wide", initial_sidebar_state="collapsed")

# =====================================================================
# 데이터 정의 부분 (여기서 내용을 수정하면 화면에 자동으로 반영됩니다)
# =====================================================================

MODEL_PROFILES = {
    "llama4": {
        "title": "Llama-4 (8B-Instruct)",
        "tagline": '"로컬 LLM의 교과서, 균형 잡힌 고성능 범용 비서"',
        "badge": "무손실 구동 권장",
        "speed": "~38 tok/s",
        "quant": "Q8_0",
        "vram": "약 8.5 GB",
        "context": "128k",
        "desc": "Meta의 최첨단 Llama-4 아키텍처 기반으로 튜닝된 범용 플래그십 지식형 모델입니다. 이전 세대 대비 인스트럭션 추종 능력이 최대 30% 강화되어 프롬프트 내 세세한 제약을 단 한 개도 무시하지 않고 끝까지 지킵니다. 특히 한국어 인코더 성능이 획기적으로 개선되어, 영어와 유사한 수준의 압축률과 표현 가독성을 자랑합니다.",
        "pros": [
            "매우 낮은 환각(Hallucination) 지지율",
            "영한 문서 번역, 대규모 요약 품질 1위",
            "가장 범용적이고 다양한 라이브러리 지원 연동성"
        ],
        "cons": [
            "수학 및 복잡한 논리식 연산에서 가끔씩 계산 실수 유발",
            "독창성 있는 창작 소설, 시 등에서 답변 문체가 약간 인위적"
        ],
        "cmd": "ollama run llama4:8b-instruct-q8_0",
        "prompt": '"너는 지금부터 최고 권위의 비즈니스 컨설턴트다. 아래 전달하는 기획서 초안의 논리적 모순점 3가지를 찾고, 비판적이고 간결한 대안을 제시해줘."'
    },
    "qwen3": {
        "title": "Qwen-3 (7B-Instruct)",
        "tagline": '"번개처럼 빠른 속도, 아시아 언어와 개발의 절대강자"',
        "badge": "극강의 가성비",
        "speed": "~46 tok/s",
        "quant": "Q6_K",
        "vram": "약 6.0 GB",
        "context": "32k",
        "desc": "Alibaba가 내놓은 7B 체급의 괴물 모델입니다. 한국어, 일본어, 중국어를 포함한 아시아권 언어의 이해도가 극도로 높으며, 코드 생성 속도와 코딩 성공률 부문에서 상용 대형 LLM에 필적하는 고효율을 자부합니다. 메모리 점유가 적어 가벼운 백그라운드 코딩 지원용으로 제격입니다.",
        "pros": [
            "동일 체급 중 아시아 언어 및 한국어 자연스러움 1위",
            "코드 에러 수정 및 자동 완성 성공률 극대화",
            "초당 45 토큰 이상의 압도적인 가속 연산 속도"
        ],
        "cons": [
            "영어 문맥 내에 숨겨진 인문학적 비유나 서구식 밈 이해도가 비교적 약함",
            "32k 이상의 아주 긴 복잡 문맥에서는 가중치 혼선 가능성 존재"
        ],
        "cmd": "ollama run qwen3:7b-instruct-q6_k",
        "prompt": '"다음 제공하는 파이썬 비동기 통신 코드에서 발생하기 쉬운 메모리 누수 지점 2곳을 찾아 리팩토링 버전을 짜줘."'
    },
    "gemma3": {
        "title": "Gemma-3 (9B-Instruct)",
        "tagline": '"작은 거인, 70B급의 논리 전개 능력을 이식받은 해결사"',
        "badge": "초고성능 두뇌",
        "speed": "~28 tok/s",
        "quant": "Q6_K",
        "vram": "약 8.2 GB",
        "context": "16k",
        "desc": "구글의 독자적인 AI 인프라 학습 결과를 바탕으로 수려한 수학 및 논리 추론력을 갖춘 9B 모델입니다. 수능 킬러 문항 및 어려운 프로그래밍 알고리즘을 입력했을 때, 단계별 풀이 과정(Chain of Thought)을 짚어나가는 호흡이 가장 차분하고 정교합니다.",
        "pros": [
            "수학식 연산 및 참/거짓 논리 검증 9B 체급 독보적 1위",
            "풍부하고 학술적이며 신뢰도 높은 인프라 지식 정보력",
            "단계별 추론 가이드가 명확하고 정돈된 포맷"
        ],
        "cons": [
            "어휘 사전(Vocab Size)이 비대하여 모델 파일 크기 대비 VRAM 소모가 살짝 큼",
            "한국어 실시간 타이핑 출력 반응 속도가 다른 7B-8B에 비해 다소 무거움"
        ],
        "cmd": "ollama run gemma3:9b-instruct-q6_k",
        "prompt": '"물리학 논제인 슈뢰딩거의 고양이 패러독스를 중학생도 단번에 흥미를 느낄 수 있게 쉬운 동화식 비유로 서술해봐."'
    },
    "mistral": {
        "title": "Mistral Nemo (12B-Instruct)",
        "tagline": '"128k 거대 문맥을 원활히 삼키는 정보 분석의 거장"',
        "badge": "대용량 문맥 최적화",
        "speed": "~22 tok/s",
        "quant": "Q4_K_M",
        "vram": "약 7.8 GB",
        "context": "128k",
        "desc": "Mistral AI가 엔비디아와 공동 설계한 12B 모델입니다. 이 모델은 16GB Mac Mini 사용자들에게 독특한 기회를 줍니다. 4비트 양자화를 적용해 VRAM 점유율을 대폭 낮춘 채, 12B가 주는 넓은 추론 공간과 무려 128,000토큰의 긴 문서 읽기 작업을 동시에 실현합니다.",
        "pros": [
            "소설 한 권 전체, 긴 레포트 수십 장 동시 입력 가능",
            "고급 추론 및 상황극, 기획서 초안 창작력 우수",
            "엔비디아 최신 가중치 설계 공정 반영으로 높은 안전성"
        ],
        "cons": [
            "16GB Mac의 한계 영역이라 구동 시 타 백그라운드 프로그램 정리 필수",
            "4-bit(Q4) 양자화 실행으로 세세한 단어 사용 오차 발생 여지 존재"
        ],
        "cmd": "ollama run mistral-nemo:12b-instruct-q4_k_m",
        "prompt": '"첨부한 영문 법적 계약서 전문에서 조항 간 서로 상충되어 소송 리스크가 생길 위험이 있는 부분을 찾아내 해석해줘."'
    },
    "deepseek": {
        "title": "DeepSeek Coder Lite (MoE)",
        "tagline": '"필요한 두뇌 부위만 켜서 연산하는 고속 스마트 오피서"',
        "badge": "지능형 아키텍처",
        "speed": "~32 tok/s",
        "quant": "Q4_K_M",
        "vram": "약 7.5 GB",
        "context": "64k",
        "desc": "전체 16B급 파라미터를 가졌으나, 연산 중에는 필요한 전문가 부위(활성 파라미터 약 2.4B)만 선별적으로 가동하는 혁신적인 MoE(Mixture of Experts) 모델입니다. 덕분에 디스크 용량 대비 극도로 가벼운 VRAM 실시간 소모량과 비정상적으로 강력한 코딩 정확도를 경험할 수 있습니다.",
        "pros": [
            "엄청나게 낮은 전력 소비량과 GPU 가열 감소 효과",
            "MoE 특유의 입체적 코딩 파이프라인 및 복수 함수 대조",
            "수학 논리 연산 성능 대비 환상적인 메모리 여유공간"
        ],
        "cons": [
            "일반 감성 영역의 대화, 위로, 연설문 대필 등은 기계적인 뉘앙스로 제한됨",
            "일부 구형 로컬 구동 프레임워크(Ollama 구버전 등)에서 MoE 가속 불안정 오류 유발 가능"
        ],
        "cmd": "ollama run deepseek-coder-lite:16b-q4_k_m",
        "prompt": '"크롬 확장 프로그램용 백그라운드 서비스 워커를 작성하고, 브라우저가 종료되어도 상태 유지를 하도록 API를 매핑해줘."'
    },
    "nemotron": {
        "title": "Nemotron-4 (8B-Instruct)",
        "tagline": '"AI 에이전트, JSON 정형 데이터 출력을 위해 출생한 전사"',
        "badge": "JSON 및 API 연동 특화",
        "speed": "~35 tok/s",
        "quant": "Q8_0",
        "vram": "약 8.5 GB",
        "context": "4k",
        "desc": "NVIDIA에서 커스텀 설계하여 배포한 고성능 8B 모델입니다. 정형화되지 않은 텍스트 데이터를 받아서 프로그래밍이 해석할 수 있는 엄격한 JSON 스키마 형태로 가공하는 능력이 뛰어납니다. 외부 API 호출 및 에이전트 구축(Function Calling) 벤치마크 최고 점수를 고수하고 있습니다.",
        "pros": [
            "함수 호출(Function Calling) 실행 실패 확률이 3% 미만",
            "RAG(검색 증강 요약) 시 원본 소스 주소 및 출처 추출의 비정상적 정확도",
            "엔터프라이즈 업무 자동화 환경에 완벽 결합"
        ],
        "cons": [
            "컨텍스트 윈도우가 4k 수준으로 협소하여 두꺼운 책 분석 불가능",
            "창의적인 작문, 긴 마케팅 문구 생성 등에는 너무 차갑고 단순한 어조 유지"
        ],
        "cmd": "ollama run nemotron-4:8b-instruct-q8_0",
        "prompt": '"다음 메신저 대화기록 전문을 읽고, 중요 일정(날짜, 시간, 참석자, 안건)만 식별하여 완벽한 RFC-8259 규격 JSON으로 반환해줘."'
    }
}

# 레이더 차트 데이터셋 설정
RADAR_CHART_DATASETS = [
    {
        "label": 'Llama-4 (8B)',
        "data": [85, 88, 96, 92, 95, 85],
        "borderColor": '#4f46e5',
        "backgroundColor": 'rgba(79, 70, 229, 0.1)',
        "borderWidth": 2,
        "pointBackgroundColor": '#4f46e5'
    },
    {
        "label": 'Qwen-3 (7B)',
        "data": [95, 92, 88, 97, 85, 90],
        "borderColor": '#f59e0b',
        "backgroundColor": 'rgba(245, 158, 11, 0.05)',
        "borderWidth": 2,
        "borderDash": [5, 5],
        "pointBackgroundColor": '#f59e0b'
    },
    {
        "label": 'Gemma-3 (9B)',
        "data": [88, 96, 91, 95, 93, 78],
        "borderColor": '#10b981',
        "backgroundColor": 'rgba(16, 185, 129, 0.1)',
        "borderWidth": 2.5,
        "pointBackgroundColor": '#10b981'
    },
    {
        "label": 'Mistral Nemo (12B)',
        "data": [91, 90, 89, 90, 94, 72],
        "borderColor": '#06b6d4',
        "backgroundColor": 'transparent',
        "borderWidth": 1.5,
        "borderDash": [2, 2],
        "pointBackgroundColor": '#06b6d4'
    }
]

# 양자화 비트 정밀 차트 데이터셋 설정
QUANT_CHART_DATASETS = [
    {
        "type": 'line',
        "label": '원시 지능 보존율 (%)',
        "data": [100, 99.5, 98.2, 94.0, 81.0],
        "borderColor": '#f43f5e',
        "backgroundColor": '#f43f5e',
        "borderWidth": 3,
        "tension": 0.3,
        "yAxisID": 'y_left'
    },
    {
        "type": 'bar',
        "label": '실제 VRAM 소모량 (GB)',
        "data": [16.5, 8.5, 6.8, 5.2, 4.2],
        "backgroundColor": 'rgba(79, 70, 229, 0.5)',
        "borderRadius": 4,
        "yAxisID": 'y_right'
    }
]

# =====================================================================
# HTML 렌더링 로직
# =====================================================================

template_path = os.path.join(os.path.dirname(__file__), "template.html")

try:
    with open(template_path, "r", encoding="utf-8") as f:
        template_str = f.read()

    # Jinja2 템플릿 엔진을 사용하여 데이터를 HTML에 주입
    template = Template(template_str)
    rendered_html = template.render(
        MODEL_PROFILES_JSON=json.dumps(MODEL_PROFILES, ensure_ascii=False),
        RADAR_CHART_DATASETS=json.dumps(RADAR_CHART_DATASETS, ensure_ascii=False),
        QUANT_CHART_DATASETS=json.dumps(QUANT_CHART_DATASETS, ensure_ascii=False)
    )

    # Streamlit 컴포넌트를 통해 HTML 표시 (전체 화면 높이 넉넉히 설정)
    st.components.v1.html(rendered_html, height=2200, scrolling=True)

except Exception as e:
    st.error(f"템플릿 로딩 중 오류가 발생했습니다: {e}")
