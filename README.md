<div align="center">

# 🐶 Pet Commerce Customer Churn Prediction Dashboard
### Machine Learning 기반 반려동물 커머스 고객 이탈 예측 및 분석 시스템

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white">
<img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white">
<img src="https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white">
<img src="https://img.shields.io/badge/LightGBM-02569B?style=for-the-badge">
<img src="https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white">

</div>

---

# 📖 프로젝트 소개

반려동물 커머스 고객 거래 데이터를 활용하여 **고객 이탈(Churn)을 예측**하고,
기업이 **이탈 가능성이 높은 고객을 사전에 식별하여 마케팅 전략을 수립할 수 있도록 지원하는 머신러닝 기반 웹 대시보드**입니다.
Streamlit을 이용하여 실시간 예측, 고객 분석 및 PDF 리포트 생성 기능을 제공합니다.

---

# 1. Project Overview

### 📌 주제
반려동물 커머스 고객 이탈 예측 Dashboard 개발

### 🎯 목표
- 고객 이탈 여부 예측
- 고객 특성 분석
- 실시간 예측 서비스 제공
- PDF Report 자동 생성

---

# 2. Dataset

### 데이터 구성
고객의 **구매(거래) 로그 데이터**를 기반으로 고객 단위 피처를 가공하여 사용합니다.

원천 데이터 주요 컬럼

| 컬럼명 | 설명 |
| :--- | :--- |
| 고객ID | 고객 식별자 |
| 주문번호 | 주문 식별자 |
| 거래일시 | 거래 발생 일시 |
| 매출 | 거래 매출액 |
| 단가 | 상품 단가 |
| 수량 | 구매 수량 |
| 카테고리 | 상품 카테고리 |
| 상품명 | 구매 상품명 |

위 거래 로그를 고객 단위로 집계하여 구매 빈도, 평균 주문 금액, 최근 구매 경과일 등 파생 피처를 생성하고, 이를 기반으로 이탈 여부(Churn)를 라벨링하여 모델을 학습합니다.

> ⚠️ 본 데이터셋은 학습/시연 목적의 가상 데이터입니다.

---

# 3. 프로젝트 구조

```text
Petcommerce-Churn-Predict
├── app.py                 # Streamlit 메인 앱
├── train_model.py         # 모델 학습 스크립트
├── requirements.txt
├── users.yaml              # 로그인 인증 정보 (gitignore 처리, 저장소에 포함되지 않음)
├── app.db                  # 로컬 SQLite DB (gitignore 처리)
├── models/
├── assets/
├── src/
│   └── churn_model.py
├── templates/
├── static/
└── README.md
```

> `users.yaml`, `app.db`는 민감 정보를 포함하므로 `.gitignore`에 등록되어 있으며, 저장소를 클론한 뒤 직접 생성해야 합니다. (`users.yaml.example` 참고)

---

# 4. 주요 기능

### 🔐 사용자 인증
- `streamlit-authenticator` 기반 로그인/세션 관리

### 📊 고객 이탈 예측
- 고객 정보 입력
- 이탈 확률 계산
- 예측 결과 시각화

### 📈 데이터 분석
- 고객 분포 분석
- Feature Importance
- 주요 통계 정보

### 📄 PDF Report
- 고객 정보 요약
- 예측 결과
- 분석 리포트 자동 생성 (ReportLab 기반)

### 🌐 리포트 렌더링
- Playwright를 활용한 HTML → PDF/이미지 변환 보조

---

# 5. Machine Learning Pipeline
