import streamlit as st
import json
import os
from jinja2 import Template

# Streamlit 페이지 설정
st.set_page_config(page_title="로컬 LLM 가이드 v4.0 Ultimate", layout="wide", initial_sidebar_state="collapsed")

# =====================================================================
# 데이터 정의 부분 (여기서 내용을 수정하면 화면에 자동으로 반영됩니다)
# =====================================================================

MODEL_PROFILES = {
        llama4: {
            title: "Llama-4 (8B-Instruct)",
            tagline: '"로컬 LLM의 교과서, 균형 잡힌 고성능 범용 비서"',
            badge: "무손실 구동 권장",
            speed: "~38 tok/s",
            quant: "Q8_0",
            vram: "약 8.5 GB",
            context: "128k",
            desc: "Meta의 최첨단 Llama-4 아키텍처 기반으로 튜닝된 범용 플래그십 지식형 모델입니다. 이전 세대 대비 인스트럭션 추종 능력이 최대 30% 강화되어 프롬프트 내 세세한 제약을 단 한 개도 무시하지 않고 끝까지 지킵니다. 특히 한국어 인코더 성능이 획기적으로 개선되어, 영어와 유사한 수준의 압축률과 표현 가독성을 자랑합니다.",
            pros: [
                "매우 낮은 환각(Hallucination) 지지율",
                "영한 문서 번역, 대규모 요약 품질 1위",
                "가장 범용적이고 다양한 라이브러리 지원 연동성"
            ],
            cons: [
                "수학 및 복잡한 논리식 연산에서 가끔씩 계산 실수 유발",
                "독창성 있는 창작 소설, 시 등에서 답변 문체가 약간 인위적"
            ],
            cmd: "ollama run llama4:8b-instruct-q8_0",
            prompt: '"너는 지금부터 최고 권위의 비즈니스 컨설턴트다. 아래 전달하는 기획서 초안의 논리적 모순점 3가지를 찾고, 비판적이고 간결한 대안을 제시해줘."'
        },
        qwen3: {
            title: "Qwen-3 (7B-Instruct)",
            tagline: '"번개처럼 빠른 속도, 아시아 언어와 개발의 절대강자"',
            badge: "극강의 가성비",
            speed: "~46 tok/s",
            quant: "Q6_K",
            vram: "약 6.0 GB",
            context: "32k",
            desc: "Alibaba가 내놓은 7B 체급의 괴물 모델입니다. 한국어, 일본어, 중국어를 포함한 아시아권 언어의 이해도가 극도로 높으며, 코드 생성 속도와 코딩 성공률 부문에서 상용 대형 LLM에 필적하는 고효율을 자부합니다. 메모리 점유가 적어 가벼운 백그라운드 코딩 지원용으로 제격입니다.",
            pros: [
                "동일 체급 중 아시아 언어 및 한국어 자연스러움 1위",
                "코드 에러 수정 및 자동 완성 성공률 극대화",
                "초당 45 토큰 이상의 압도적인 가속 연산 속도"
            ],
            cons: [
                "영어 문맥 내에 숨겨진 인문학적 비유나 서구식 밈 이해도가 비교적 약함",
                "32k 이상의 아주 긴 복잡 문맥에서는 가중치 혼선 가능성 존재"
            ],
            cmd: "ollama run qwen3:7b-instruct-q6_k",
            prompt: '"다음 제공하는 파이썬 비동기 통신 코드에서 발생하기 쉬운 메모리 누수 지점 2곳을 찾아 리팩토링 버전을 짜줘."'
        },
        gemma3: {
            title: "Gemma-3 (9B-Instruct)",
            tagline: '"작은 거인, 70B급의 논리 전개 능력을 이식받은 해결사"',
            badge: "초고성능 두뇌",
            speed: "~28 tok/s",
            quant: "Q6_K",
            vram: "약 8.2 GB",
            context: "16k",
            desc: "구글의 독자적인 AI 인프라 학습 결과를 바탕으로 수려한 수학 및 논리 추론력을 갖춘 9B 모델입니다. 수능 킬러 문항 및 어려운 프로그래밍 알고리즘을 입력했을 때, 단계별 풀이 과정(Chain of Thought)을 짚어나가는 호흡이 가장 차분하고 정교합니다.",
            pros: [
                "수학식 연산 및 참/거짓 논리 검증 9B 체급 독보적 1위",
                "풍부하고 학술적이며 신뢰도 높은 인프라 지식 정보력",
                "단계별 추론 가이드가 명확하고 정돈된 포맷"
            ],
            cons: [
                "어휘 사전(Vocab Size)이 비대하여 모델 파일 크기 대비 VRAM 소모가 살짝 큼",
                "한국어 실시간 타이핑 출력 반응 속도가 다른 7B-8B에 비해 다소 무거움"
            ],
            cmd: "ollama run gemma3:9b-instruct-q6_k",
            prompt: '"물리학 논제인 슈뢰딩거의 고양이 패러독스를 중학생도 단번에 흥미를 느낄 수 있게 쉬운 동화식 비유로 서술해봐."'
        },
        mistral: {
            title: "Mistral Nemo (12B-Instruct)",
            tagline: '"128k 거대 문맥을 원활히 삼키는 정보 분석의 거장"',
            badge: "대용량 문맥 최적화",
            speed: "~22 tok/s",
            quant: "Q4_K_M",
            vram: "약 7.8 GB",
            context: "128k",
            desc: "Mistral AI가 엔비디아와 공동 설계한 12B 모델입니다. 이 모델은 16GB Mac Mini 사용자들에게 독특한 기회를 줍니다. 4비트 양자화를 적용해 VRAM 점유율을 대폭 낮춘 채, 12B가 주는 넓은 추론 공간과 무려 128,000토큰의 긴 문서 읽기 작업을 동시에 실현합니다.",
            pros: [
                "소설 한 권 전체, 긴 레포트 수십 장 동시 입력 가능",
                "고급 추론 및 상황극, 기획서 초안 창작력 우수",
                "엔비디아 최신 가중치 설계 공정 반영으로 높은 안전성"
            ],
            cons: [
                "16GB Mac의 한계 영역이라 구동 시 타 백그라운드 프로그램 정리 필수",
                "4-bit(Q4) 양자화 실행으로 세세한 단어 사용 오차 발생 여지 존재"
            ],
            cmd: "ollama run mistral-nemo:12b-instruct-q4_k_m",
            prompt: '"첨부한 영문 법적 계약서 전문에서 조항 간 서로 상충되어 소송 리스크가 생길 위험이 있는 부분을 찾아내 해석해줘."'
        },
        deepseek: {
            title: "DeepSeek Coder Lite (MoE)",
            tagline: '"필요한 두뇌 부위만 켜서 연산하는 고속 스마트 오피서"',
            badge: "지능형 아키텍처",
            speed: "~32 tok/s",
            quant: "Q4_K_M",
            vram: "약 7.5 GB",
            context: "64k",
            desc: "전체 16B급 파라미터를 가졌으나, 연산 중에는 필요한 전문가 부위(활성 파라미터 약 2.4B)만 선별적으로 가동하는 혁신적인 MoE(Mixture of Experts) 모델입니다. 덕분에 디스크 용량 대비 극도로 가벼운 VRAM 실시간 소모량과 비정상적으로 강력한 코딩 정확도를 경험할 수 있습니다.",
            pros: [
                "엄청나게 낮은 전력 소비량과 GPU 가열 감소 효과",
                "MoE 특유의 입체적 코딩 파이프라인 및 복수 함수 대조",
                "수학 논리 연산 성능 대비 환상적인 메모리 여유공간"
            ],
            cons: [
                "일반 감성 영역의 대화, 위로, 연설문 대필 등은 기계적인 뉘앙스로 제한됨",
                "일부 구형 로컬 구동 프레임워크(Ollama 구버전 등)에서 MoE 가속 불안정 오류 유발 가능"
            ],
            cmd: "ollama run deepseek-coder-lite:16b-q4_k_m",
            prompt: '"크롬 확장 프로그램용 백그라운드 서비스 워커를 작성하고, 브라우저가 종료되어도 상태 유지를 하도록 API를 매핑해줘."'
        },
        nemotron: {
            title: "Nemotron-4 (8B-Instruct)",
            tagline: '"AI 에이전트, JSON 정형 데이터 출력을 위해 출생한 전사"',
            badge: "JSON 및 API 연동 특화",
            speed: "~35 tok/s",
            quant: "Q8_0",
            vram: "약 8.5 GB",
            context: "4k",
            desc: "NVIDIA에서 커스텀 설계하여 배포한 고성능 8B 모델입니다. 정형화되지 않은 텍스트 데이터를 받아서 프로그래밍이 해석할 수 있는 엄격한 JSON 스키마 형태로 가공하는 능력이 뛰어납니다. 외부 API 호출 및 에이전트 구축(Function Calling) 벤치마크 최고 점수를 고수하고 있습니다.",
            pros: [
                "함수 호출(Function Calling) 실행 실패 확률이 3% 미만",
                "RAG(검색 증강 요약) 시 원본 소스 주소 및 출처 추출의 비정상적 정확도",
                "엔터프라이즈 업무 자동화 환경에 완벽 결합"
            ],
            cons: [
                "컨텍스트 윈도우가 4k 수준으로 협소하여 두꺼운 책 분석 불가능",
                "창의적인 작문, 긴 마케팅 문구 생성 등에는 너무 차갑고 단순한 어조 유지"
            ],
            cmd: "ollama run nemotron-4:8b-instruct-q8_0",
            prompt: '"다음 메신저 대화기록 전문을 읽고, 중요 일정(날짜, 시간, 참석자, 안건)만 식별하여 완벽한 RFC-8259 규격 JSON으로 반환해줘."'
        }
    }

EXTENDED_PROFILES = {
        exaone: {
            title: "Exaone 3.5 (7.8B-Instruct)",
            tagline: '"국내 사내 데이터 RAG 및 공문서 정제력 독보적 1위"',
            badge: "LG AI 연구소 개발",
            speed: "~40 tok/s",
            quant: "Q8_0",
            vram: "약 8.2 GB",
            context: "32k",
            desc: "LG AI Research가 개발한 국산 오픈소스의 자존심입니다. 한국어 특화 토크나이저(Tokenizer) 효율이 뛰어나 다른 외국계 모델에 비해 한글 출력 속도가 매우 우수하며, 한국의 역사, 법률, 회사 정관, 공공문서 어투를 완벽히 이해합니다. 사내 PDF 데이터베이스를 끌어다 쓰거나(RAG), 관공서 스타일의 서신 기획에 최적의 파트너입니다.",
            pros: [
                "국내 실정법, 행정 서식, 사내 보고서 어조 재현율 최고",
                "적은 한글 토큰 분할율로 동일 내용 생성 시 매우 적은 자원 소모",
                "국내 벤치마크 Ko-LLM 리더보드 최고 성과 유지"
            ],
            cons: [
                "글로벌 영문 논문 분석 등 영어 중심 맥락 추론은 Llama에 비해 미약",
                "코딩 자동 작성 및 웹 크롤러 스크립트 도출 성공률은 약간 처짐"
            ],
            cmd: "ollama run exaone:7.8b-instruct-q8_0",
            prompt: '"아래 제공하는 회의록 정리를 바탕으로, 대한민국 중소기업청 지원 사업 계획서 규격에 맞게 기대효과 및 마케팅 전략 부분을 공문서 스타일로 재작성해줘."'
        },
        phi4: {
            title: "Phi-4 (14B-Instruct)",
            tagline: '"작은 파라미터에 욱여넣은 초극강 고지능 수학/과학 해결사"',
            badge: "Microsoft Research",
            speed: "~18 tok/s",
            quant: "Q4_K_M",
            vram: "약 8.8 GB",
            context: "16k",
            desc: "마이크로소프트의 초고집적 연구 프로젝트의 산물입니다. 14B 수준의 파라미터 구조를 지니고 있어 16GB Mac에서는 4비트 양자화(Q4_K_M)로 타협해야 하지만, 그 성능은 70B급 플래그십과 맞먹습니다. 과학 연구, 대학 논문 수준의 물리학 계산, 그리고 매우 난해한 논리 구조를 추론할 때 최고의 지능을 선사합니다.",
            pros: [
                "GPT-4급 하드 수학식 및 과학적 공학 추론 연산 정합성 보유",
                "초밀도 데이터 집적 기술로 파라미터 대비 지능 밀도가 세계 1위"
            ],
            cons: [
                "생성 속도가 느린 편(16GB Mac 기준 초당 약 18토큰 안팎)",
                "메모리 한계에 가깝게 동작하므로 사용 시 여타 크롬 탭 등을 일시 닫아야 함"
            ],
            cmd: "ollama run phi4:14b-instruct-q4_k_m",
            prompt: '"다음 2차 행렬식들의 역행렬을 계산하고, 그 성질이 선형 변환 공간 내에서 왜 주축 회전을 제한하는지 수학적 단계로 증명해봐."'
        },
        deepseekR1: {
            title: "DeepSeek-R1-Distill-Llama (8B)",
            tagline: '"강화학습을 통한 자가 추론 CoT를 수행하는 논리 연산 해결사"',
            badge: "자가 추론 특화",
            speed: "~30 tok/s",
            quant: "Q8_0",
            vram: "약 8.5 GB",
            context: "32k",
            desc: "2026년 오프라인 로컬 환경에서 가장 각광받는 '추론 전용(Reasoning-Focused)' 가중치 모델입니다. Llama-3/4 8B 바디에 DeepSeek-R1의 자가 강화학습(Reinforcement Learning) 데이터를 이식받아, 난해한 질문을 주면 백그라운드에서 인간처럼 독백하며 자아성찰(Chain-of-Thought)을 전개한 후 가장 완성도 높은 논리식 답변을 출력합니다.",
            pros: [
                "답변 출력 전 혼잣말로 모든 문제의 오류를 가다듬어 정확도가 타 8B와 궤를 달리함",
                "코딩 예외 처리(Edge Cases) 구멍을 자발적으로 완벽 점검 및 보수"
            ],
            cons: [
                "생각 과정(CoT)을 먼저 타이핑하기 때문에 첫 번째 최종 토큰이 나오기까지 딜레이가 묾",
                "단순 질의응답이나 빠른 비서 모드로 쓰기에는 지나치게 장황하고 생각이 많음"
            ],
            cmd: "ollama run deepseek-r1:8b",
            prompt: '"A는 B보다 키가 크고, C는 D보다 키가 작으며, B는 D와 키가 같다. 가장 키가 작은 사람부터 큰 순서로 한 단어씩 논리 정렬해줘."'
        },
        hermes3: {
            title: "Hermes-3-Llama-3 (8B)",
            tagline: '"안전 가이드라인 필터를 우회하여 끝없는 창작의 자유를 누리는 연출가"',
            badge: "Nous Research",
            speed: "~36 tok/s",
            quant: "Q8_0",
            vram: "약 8.5 GB",
            context: "64k",
            desc: "Nous Research가 커뮤니티 지향적으로 릴리즈한 '검열 우회형/창작 전용' 플래그십 파인튜닝 가중치입니다. 다른 공식 상용 모델들이 시스템 가이드라인 규정으로 거절하는 과감한 세계관 시나리오, 소설 작문, 롤플레잉 연기를 유연하게 허용합니다. 작가, 게임 시나리오 디자이너에게 영감을 주는 최고의 가상 롤플레잉 머신입니다.",
            pros: [
                "검열 필터에 의한 '죄송하지만 도울 수 없습니다' 거부 반응 제로에 수렴",
                "뛰어난 단어 선택, 서정적 묘사 능력 및 유기적 상황 조율력"
            ],
            cons: [
                "정직하고 윤리적인 RAG 사내 지식 검증 등에는 필터가 너무 없어 사치스러움",
                "팩트 위주의 정확한 계산이 요구될 때는 묘사 어휘가 많아 오히려 환각성이 높아짐"
            ],
            cmd: "ollama run hermes3:8b",
            prompt: '"너는 중세 암흑 시대를 지배하는 냉혹한 마법 왕국의 왕이다. 성안으로 무단 침입한 성기사를 대면해 조용히 협박하는 연극적 시나리오 대사를 써줘."'
        },
        commandr: {
            title: "Cohere Command R (35B-Q2)",
            tagline: '"16GB Mac에서 35B 거대 모델의 문맥 제어력을 억지로 맛보는 하이엔드 테크닉"',
            badge: "극단적 한계 스퀴징",
            speed: "~12 tok/s",
            quant: "Q2_K (초고압축)",
            vram: "약 11.2 GB",
            context: "128k",
            desc: "Cohere의 35B 비즈니스 문서 거대 거장을 16GB 램을 가진 Mac Mini에 밀어 넣는 특수 튜닝 기술입니다. 2비트 극단적 압축(Q2_K)을 진행하면 VRAM 요구량이 약 11GB로 낮아져 간신히 16GB 시스템에서 튕기지 않고 로딩됩니다. 손실이 있으나, 거대 모델 고유의 깊은 인과 분석력과 RAG 전문 문서 파지 능력을 테스트하기에 흥미롭습니다.",
            pros: [
                "35B 체급이 자아내는 고차원 다국어 비즈니스 맥락 제어",
                "128k에 달하는 엄청난 입력 수용량"
            ],
            cons: [
                "극도로 인코딩 성능이 낮아져 비문 및 사소한 단어 오타가 잦음",
                "초당 약 10~12 토큰 수준으로, 타이핑을 지켜볼 때 다소 인내심 요구"
            ],
            cmd: "ollama run command-r:35b-v01-q2_K",
            prompt: '"다국적 제약 바이오 기업들의 2026 연간 회계 대차대조표 총 10장을 요약하여 공통된 리스크 인자를 한글 요약해줘."'
        }
    }

RADAR_CHART_DATASETS = [
                {
                    label: 'Llama-4 (8B)',
                    data: [85, 88, 96, 92, 95, 85],
                    borderColor: '#4f46e5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    borderWidth: 2,
                    pointBackgroundColor: '#4f46e5'
                },
                {
                    label: 'Qwen-3 (7B)',
                    data: [95, 92, 88, 97, 85, 90],
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.05)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointBackgroundColor: '#f59e0b'
                },
                {
                    label: 'Gemma-3 (9B)',
                    data: [88, 96, 91, 95, 93, 78],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2.5,
                    pointBackgroundColor: '#10b981'
                },
                {
                    label: 'Mistral Nemo (12B)',
                    data: [91, 90, 89, 90, 94, 72],
                    borderColor: '#06b6d4',
                    backgroundColor: 'transparent',
                    borderWidth: 1.5,
                    borderDash: [2, 2],
                    pointBackgroundColor: '#06b6d4'
                }
            ]

QUANT_CHART_DATASETS = [
                {
                    type: 'line',
                    label: '원시 지능 보존율 (%)',
                    data: [100, 99.5, 98.2, 94.0, 81.0],
                    borderColor: '#f43f5e',
                    backgroundColor: '#f43f5e',
                    borderWidth: 3,
                    tension: 0.3,
                    yAxisID: 'y_left'
                },
                {
                    type: 'bar',
                    label: '실제 VRAM 소모량 (GB)',
                    data: [16.5, 8.5, 6.8, 5.2, 4.2],
                    backgroundColor: 'rgba(79, 70, 229, 0.5)',
                    borderRadius: 4,
                    yAxisID: 'y_right'
                }
            ]

# =====================================================================
# HTML 렌더링 로직
# =====================================================================

template_path = os.path.join(os.path.dirname(__file__), "template.html")

try:
    with open(template_path, "r", encoding="utf-8") as f:
        template_str = f.read()

    template = Template(template_str)
    rendered_html = template.render(
        MODEL_PROFILES_JSON=json.dumps(MODEL_PROFILES, ensure_ascii=False),
        EXTENDED_PROFILES_JSON=json.dumps(EXTENDED_PROFILES, ensure_ascii=False),
        RADAR_CHART_DATASETS=json.dumps(RADAR_CHART_DATASETS, ensure_ascii=False),
        QUANT_CHART_DATASETS=json.dumps(QUANT_CHART_DATASETS, ensure_ascii=False)
    )

    st.components.v1.html(rendered_html, height=2200, scrolling=True)

except Exception as e:
    st.error(f"템플릿 로딩 중 오류가 발생했습니다: {e}")
