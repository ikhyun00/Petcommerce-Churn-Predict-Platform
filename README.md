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

반려동물 커머스 고객 데이터를 활용하여 **고객 이탈(Churn)을 예측**하고,

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

고객 구매 및 행동 데이터를 활용

주요 변수 예시

| 변수명 | 설명 |
| :--- | :--- |
| Customer Age | 고객 나이 |
| Membership Period | 가입 기간 |
| Purchase Frequency | 구매 빈도 |
| Average Order Value | 평균 주문 금액 |
| Last Purchase Days | 마지막 구매 이후 경과일 |
| Coupon Usage | 쿠폰 사용 여부 |
| Customer Service Calls | 고객센터 이용 횟수 |
| Pet Type | 반려동물 종류 |
| Churn | 고객 이탈 여부(Target) |

---

# 3. 프로젝트 구조

```text
Petcommerce-Churn-Predict

├── app.py
├── requirements.txt
├── models/
├── assets/
├── src/
├── templates/
├── static/
└── README.md
```

---

# 4. 주요 기능

### 📊 고객 이탈 예측

- 고객 정보 입력
- 이탈 확률 계산
- 예측 결과 시각화

---

### 📈 데이터 분석

- 고객 분포 분석
- Feature Importance
- 주요 통계 정보

---

### 📄 PDF Report

- 고객 정보 요약
- 예측 결과
- 분석 리포트 자동 생성

---

# 5. Machine Learning Pipeline

```
Data Collection

↓

Data Preprocessing

↓

Feature Engineering

↓

LightGBM Model

↓

Prediction

↓

Streamlit Dashboard

↓

PDF Report
```

---

# 6. 사용 모델

- Logistic Regression
- Random Forest
- XGBoost
- **LightGBM (Best Model)**

평가 지표

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC

---

# 7. Tech Stack

| 분야 | 기술 |
| :--- | :--- |
| Language | Python |
| Web | Streamlit |
| ML | Logistic Regression, LightGBM, XGBoost, Random Forest |
| DB | SQLite |
| Visualization | Plotly, Matplotlib |
| Report | ReportLab |

---

# 8. 실행 방법

```bash
git clone https://github.com/ikhyun00/Petcommerce-Chrun-Predict.git

cd Petcommerce-Chrun-Predict

pip install -r requirements.txt

streamlit run app.py
```

---

# 9. 화면 예시

## 메인 Dashboard

(스크린샷 추가)

---

## 고객 이탈 예측

(스크린샷 추가)

---

## PDF Report

(스크린샷 추가)

---

# 10. 프로젝트 특징

✅ 머신러닝 기반 고객 이탈 예측

✅ Streamlit Dashboard 구현

✅ PDF Report 자동 생성

✅ 고객 분석 시각화

✅ Feature Importance 제공

---

# 11. 향후 개선 사항

- SHAP 기반 모델 해석 기능
- 실시간 DB 연동
- 사용자 로그인 기능 강화
- Docker 배포
- AWS 클라우드 배포

---

# 👨‍💻 Developer

**조익현, 김수민, 김새한**

AI · Machine Learning · Data Analysis

GitHub
https://github.com/ikhyun00
