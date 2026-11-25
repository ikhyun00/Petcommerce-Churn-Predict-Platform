<div align="center">

# 🐶 Pet Commerce Customer Churn Prediction Dashboard
### Machine Learning 기반 반려동물 커머스 고객 이탈 예측 및 분석 시스템

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white">
<img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white">
<img src="https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white">
<img src="https://img.shields.io/badge/XGBoost-EA4335?style=for-the-badge">
<img src="https://img.shields.io/badge/LightGBM-02569B?style=for-the-badge">
<img src="https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white">

</div>

---

# 📖 프로젝트 소개

반려동물 커머스 고객 거래 데이터를 활용하여 **고객 이탈(Churn)을 예측**하고,
기업이 **이탈 가능성이 높은 고객을 사전에 식별하여 마케팅 전략을 수립할 수 있도록 지원하는 머신러닝 기반 웹 대시보드**입니다.
Streamlit을 이용하여 고객·카테고리 이탈 예측, 고객 분석 및 PDF 리포트 생성 기능을 제공하며,
여러 사용자가 **각자의 거래 데이터를 업로드해도 동작하도록** 컬럼 자동 매핑과 상대 위험 등급을 적용했습니다.

---

# 1. Project Overview

### 📌 주제
반려동물 커머스 고객 이탈 예측 Dashboard 개발

### 🎯 목표
- 고객 단위 / 고객-카테고리 단위 이탈 예측
- 업로드 데이터에 관계없이 동작하는 일반화된 분석
- 세그먼트·카테고리·환불·재고 분석 대시보드 제공
- PDF Report 자동 생성

---

# 2. Dataset

### 데이터 구성
고객의 **구매(거래) 로그 데이터**를 기반으로 고객 단위 피처를 가공하여 사용합니다.

원천 데이터 주요 컬럼

| 컬럼명 | 설명 |
| :--- | :--- |
| 고객ID | 고객 식별자 (필수) |
| 주문번호 | 주문 식별자 (필수) |
| 거래일시 | 거래 발생 일시 (필수) |
| 매출 | 거래 매출액 (없으면 단가 × 수량으로 계산) |
| 단가 | 상품 단가 |
| 수량 | 구매 수량 |
| 카테고리 | 상품 카테고리 |
| 상품명 | 구매 상품명 |

컬럼명이 달라도 `order_id`, `invoice`, `주문코드` 등 별칭 사전과 매핑 UI로 표준 컬럼에 자동 매핑합니다.
거래 로그를 고객 단위로 집계하여 구매 빈도, 평균 주문 금액, 최근 구매 경과일, 구매 간격 등 파생 피처를 생성하고, 이를 기반으로 이탈 여부(Churn)를 라벨링하여 모델을 학습합니다.

> ⚠️ 본 데이터셋은 학습/시연 목적의 가상 데이터입니다.

---

# 3. 프로젝트 구조

```text
Petcommerce-Churn-Predict-Platform
├── app.py                 # Streamlit 메인 앱 (레이아웃·사이드바·단계 전환)
├── train_model.py         # 모델 학습 스크립트
├── .streamlit/config.toml # 앱 테마 (화이트 + 인디고)
├── requirements.txt
├── app.db                  # 로컬 SQLite DB (실행 시 자동 생성, gitignore 처리)
├── models/                 # 학습된 모델, 피처 목록, 임계값 (.pkl)
├── assets/                 # 한글 폰트
├── src/
│   ├── churn_model.py      # 피처 생성, 라벨링, 학습, 추론
│   ├── auth.py             # 회원가입/로그인 (bcrypt, JWT)
│   ├── report_ui.py        # Pro 리포트 탭 (요약·세그먼트·카테고리·ML·환불·재고·비교)
│   ├── report_component.py # 카드·차트 공통 컴포넌트와 차트 팔레트
│   ├── style.py, style_token.py # 상단 바와 디자인 토큰(CSS)
│   └── storage.py          # SQLite 저장소
├── templates/              # PDF 리포트 HTML 템플릿 (Jinja2)
├── static/                 # PDF 리포트 CSS, Pretendard 폰트(OFL)
└── README.md
```

> `app.db`는 사용자 정보를 포함하므로 `.gitignore`에 등록되어 있으며, 앱 최초 실행 시 자동으로 생성됩니다.

---

# 4. 주요 기능

### 🔐 사용자 인증
- 회원가입 / 로그인 (비밀번호 `bcrypt` 해시 저장)
- `PyJWT` 기반 로그인 세션 유지 (8시간 만료)

### 📊 고객 이탈 예측
- CSV/Excel 업로드 및 컬럼 매핑
- 고객별 이탈 확률 계산
- 위험 등급(Critical / High / Medium / Low) 시각화

### 📈 데이터 분석
- 요약 탭 (핵심 KPI)
- 세그먼트 / 카테고리 / 환불 / 재고 / 비교분석
- 고객-카테고리 이탈 예측

### 📄 PDF Report
- 표지(핵심 지표·주요 발견) + 핵심 요약 · 세그먼트 · 카테고리 · ML 이탈예측 · 방어 우선 고객 · 환불/재고 페이지
- 포함할 탭을 골라 A4 가로 리포트로 생성 (Jinja2 HTML 템플릿 기반)

### 🌐 리포트 렌더링
- Playwright(헤드리스 Chromium)를 별도 프로세스로 실행하여 HTML → PDF 변환

---

# 5. Machine Learning Pipeline

```
거래 로그 업로드 + 컬럼 매핑
↓
전처리 (타입 변환, 중복·음수·결측 제거)
↓
롤링 스냅샷 생성 (30일 간격, 각 시점 이전 데이터로만 피처 생성,
                 가장 최근 시점 = 데이터 끝 - 최대 관측 기간 90일 → 라벨 관측 창이 데이터 끝을 넘지 않음)
↓
개인화 이탈 라벨링 (평균 구매 간격 × 1.8, 30~90일)
↓
시간 순 분할 (학습 / 검증 1개 시점 / 테스트 1개 시점)
  + purging: 라벨 관측 창이 검증 시점을 넘는 학습 행 제외
↓
이력 90일 이상 고객 전체로 학습 (history_days 피처 포함)
  → 3~6개월 구간용 Logistic / 6개월 이상 구간용 XGBoost, 평가는 각 구간 고객으로 (6개월 이상은 6~12개월 고객 기준)
↓
이탈 예측 = 업로드 데이터 안에서 이탈 확률 상위 30% (위험 등급 Critical·High와 동일)
  → 규칙 점수·3~6개월·6개월 이상은 점수 척도가 달라 각 그룹 안에서 순위를 매김
↓
Streamlit Dashboard 예측 서비스
↓
PDF Report 생성
```
 
---

# 6. 사용 모델

| 모델 | 비고 |
| :--- | :--- |
| 규칙 기반 점수 | 이력 90일 미만 고객 (최근성·빈도·최근 매출·재구매 가중합) |
| **Logistic Regression** | **이력 3~6개월 고객 모델** |
| **XGBoost** | **이력 6개월 이상 고객 모델** |
| **LightGBM** | **고객-카테고리 이탈 모델** |

평가 지표: ROC-AUC, PR-AUC, Precision·Recall@상위 30%, Lift(정밀도 ÷ 이탈률), Precision@Top 10%·20%

내부 테스트 결과 (최근 테스트 시점 2021-09-10, 관측 창 잘림 없음)

| 모델 | ROC-AUC | PR-AUC | 상위 30% 정밀도 | 상위 30% 재현율 | Lift | 테스트 이탈률 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 3~6개월 Logistic | 0.648 | 0.661 | 0.674 | 0.370 | 1.23 | 54.8% |
| 6개월 이상 XGBoost (6~12개월 고객 평가) | 0.756 | 0.680 | 0.699 | 0.480 | 1.59 | 43.9% |
| 고객-카테고리 LightGBM | 0.639 | 0.634 | 0.641 | 0.397 | 1.32 | 48.5% |
| 규칙 점수 (이력 90일 미만) | 0.576 | 0.711 | 0.710 | 0.314 | 1.05 | 67.7% |

> 업로드 데이터마다 이탈률과 확률 분포가 달라, 고정 확률 임계값 대신 데이터 안 상위 30%를 이탈 예측으로 표시합니다. 이전에 쓰던 F1 최대 임계값(0.26/0.28)은 이탈률이 50% 안팎인 데이터에서 고객의 67~91%를 이탈로 표시해 정밀도가 이탈률과 거의 같았습니다(0.57). 규칙 점수는 이력 90일 미만 고객 8개 시점(5,278행)에 고정 60일 관측 라벨을 붙여 평가했으며, 최근성 하나만 쓸 때(ROC-AUC 0.536)보다는 낫지만 구분력이 약합니다. 이탈률과 무관한 ROC-AUC를 주 지표로, PR-AUC와 정밀도는 이탈률 대비(Lift)로 해석합니다. 수정 전 버전은 테스트 시점 라벨의 88%가 관측 창이 잘려 PR-AUC가 부풀려져 있었습니다.

> 후보 4종(Logistic / LightGBM / XGBoost / CatBoost)을 외부 데이터셋(Kaggle Online Sales)으로 추가 검증했습니다. 6개월 이상 구간은 XGBoost(ROC-AUC 0.7249)와 CatBoost(0.7255)가 사실상 동률이었으나, CatBoost는 실제 서빙 시 2,662명에게 12종류의 확률값만 출력해 변별력이 없어 XGBoost를 채택했습니다. 3~6개월은 외부 ROC-AUC가 모든 모델 0.51~0.55로 랜덤 수준이어서, 내부 PR-AUC 1위인 Logistic Regression을 유지했습니다.

---

# 7. Tech Stack

| 분야 | 기술 |
| :--- | :--- |
| Language | Python |
| Web | Streamlit |
| Auth | bcrypt, PyJWT |
| ML | Logistic Regression, XGBoost, LightGBM, scikit-learn |
| DB | SQLite |
| Visualization | Plotly |
| Report | Jinja2, Playwright |

---

# 8. 실행 방법

```bash
git clone https://github.com/ikhyun00/Petcommerce-Churn-Predict-Platform.git
cd Petcommerce-Churn-Predict-Platform

# 1. 패키지 설치
pip install -r requirements.txt
playwright install chromium

# 2. JWT 비밀키 설정
export JWT_SECRET="your-secret-key"

# 3. 모델 학습 (선택, models/에 학습된 모델 포함)
python train_model.py

# 4. 대시보드 실행
streamlit run app.py
```

---

# 9. 프로젝트 특징

- ✅ 시간 순 롤링 스냅샷 + 관측 창 잘림 방지 + purging으로 데이터 누수 방지
- ✅ 고객별 구매 주기를 반영한 개인화 이탈 라벨
- ✅ 고객별 이력 구간으로 모델 라우팅 및 콜드스타트 규칙
- ✅ 업로드 데이터에 무관한 컬럼 매핑 및 상대 위험 등급
- ✅ PDF Report 자동 생성
- ✅ 로그인 기반 접근 제어

---

# 10. 향후 개선 사항

- SHAP 기반 모델 해석 기능
- 데이터가 더 쌓이면 구간별 모델과 단일 통합 모델 재비교
- 3~6개월 구간 일반화 개선 (외부 ROC-AUC 0.51~0.55): 첫 재구매까지 걸린 기간 등 신규 고객 피처 보강
- 이력 90일 미만 고객 규칙 점수 개선 (ROC-AUC 0.58): 첫 주문 금액·첫 구매 카테고리 등 신규 고객 신호 추가
- 코드 수정 후 모델로 외부 데이터 재검증
- 사용자 로그인 기능 강화 (OAuth 등)
- Docker 배포
- AWS 클라우드 배포

---

# 👨‍💻 Developer

| 이름 | 역할 |
| :--- | :--- |
| 조익현 | ML 모델링, 보안, DB |
| 김수민 | 데이터 수집, 프론트엔드(Streamlit UI) |
| 김새한 | 프론트엔드(Streamlit UI), 데이터 전처리 |

AI · Machine Learning · Data Analysis

GitHub: https://github.com/ikhyun00
