# 🔑 NEXTVIBE Backend

<img alt="0" src="https://github.com/user-attachments/assets/1de04707-aaef-4cd1-9e8b-eabae55b93a1" />

### 초등학생을 위한 미래형 완전체 컴퓨팅 사고력 학습 플랫폼, NEXTVIBE

순차, 조건, 반복 등의 컴퓨팅 사고 핵심 개념을 개념 학습, 개념 검토, 개념 확장의 3단계로 구성하여 표준화된 학습 흐름을 제공한다. 이때 게임형 시나리오와 자연어 프롬프트 기반의 바이브코딩을 통해 흥미와 접근성을 높이고, 생성형 AI가 전반적인 학습 과정을 안내하여 자율성과 개인화를 보장하되 학습 방향은 교육 목표에 부합하도록 유지하였다. 즉, 생성형 AI가 제공하는 안전한 상호작용 속에서 스스로 개념을 익히고, 오류를 진단 및 수정한 뒤, 규칙의 확장 및 설계까지 경험하게 함으로써 개념의 피상적 이해를 넘어 코딩적 사고 구조를 마련할 수 있도록 하였다.

🔨 기획·디자인·개발 기간 2025.09.04.-2025.11.28.

🔗 [NEXTVIBE 바로가기](https://nextv1be.netlify.app)

🎨 [기획·디자인 보러가기](https://github.com/VibeNext#-plan--design)

## 👾 Member

블라인드

## 👾 Tech Stack

<table>
  <tbody>
    <tr><td>Language</td><td><img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white" /></td></tr>
    <tr><td>Framework</td><td><img src="https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white" /> <img src="https://img.shields.io/badge/Django REST Framework-8D1D13?style=for-the-badge&logo=Django-REST-Framework&logoColor=white" /></td></tr>
    <tr><td>Database</td><td><img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=PostgreSQL&logoColor=white" /></td></tr>
    <tr><td>Cache</td><td><img src="https://img.shields.io/badge/Redis-FF4438?style=for-the-badge&logo=Redis&logoColor=white" /></td></tr>
    <tr><td>Authentication</td><td><img height="30" alt="jwt icon" src="https://github.com/user-attachments/assets/19faeacb-093d-40d7-89c7-68385cf8d9d0" /></td></tr>
    <tr><td>Cloud Infrastructure</td><td><img src="https://img.shields.io/badge/Railway-0B0D0E?style=for-the-badge&logo=Railway&logoColor=white" /></td></tr>
  </tbody>
</table>

## 👾 Directory Structure

```
backend/
│
├── .github/                       # GitHub 관리
│   ├── ISSUE_TEMPLATE/            # 이슈 템플릿
│   └── PULL_REQUEST_TEMPLATE.md   # PR 템플릿
│
├── configs/                       # config 관리
│   ├── settings/                  # Django 설정 관리
│   │   ├── __init__.py            # 어떤 환경인지 파악하고 어떤 설정을 적용할지 결정
│   │   ├── base.py                # 공통 Django 설정
│   │   ├── dev.py                 # 개발환경 Django 설정
│   │   └── prod.py                # 배포환경 Django 설정
│   ├── asgi.py                    # ASGI 설정
│   ├── routing.py                 # 웹소켓 라우팅 설정
│   ├── urls.py                    # URL 설정
│   └── wsgi.py                    # WSGI 설정
│
├── accounts/                      # Django App
│   ├── migrations/                # 데이터베이스 마이그레이션
│   ├── __init__.py                # 이 폴더가 패키지임을 표시
│   ├── admin.py                   # Admin 사이트 설정
│   ├── apps.py                    # App 설정
│   ├── forms.py                   # Form 정의
│   ├── managers.py                # Manager 정의
│   ├── models.py                  # Model 정의
│   ├── serializers.py             # Serializer 정의
│   ├── services.py                # 비즈니스 로직
│   ├── tests.py                   # 테스트 코드
│   ├── urls.py                    # App URL 설정
│   └── views.py                   # View 정의
│
├── chat/                          # Django App
│   ├── ai/                        # ai 관련 설정 관리
│   │   └── genhelper.py           # Gemini Live API 연결 헬퍼
│   ├── migrations/                # 데이터베이스 마이그레이션
│   ├── __init__.py                # 이 폴더가 패키지임을 표시
│   ├── admin.py                   # Admin 사이트 설정
│   ├── apps.py                    # App 설정
│   ├── consumer.py                # 메시지 송수신 로직
│   ├── models.py                  # Model 정의
│   ├── routing.py                 # 웹소켓 라우팅 URL 설정
│   ├── services.py                # 비즈니스 로직
│   ├── tests.py                   # 테스트 코드
│   └── views.py                   # View 정의
│
├── missions/                      # Django App
│   ├── datas/                     # 기획자가 설계한 학습단계 등의 데이터
│   ├── management/commands        # 커스텀 커맨드
│   │   └── insertdata             # missions/datas의 데이터를 DB에 삽입하는 커맨드
│   ├── migrations/                # 데이터베이스 마이그레이션
│   ├── __init__.py                # 이 폴더가 패키지임을 표시
│   ├── admin.py                   # Admin 사이트 설정
│   ├── apps.py                    # App 설정
│   ├── models.py                  # Model 정의
│   ├── serializers.py             # Serializer 정의
│   ├── services.py                # 비즈니스 로직
│   ├── tests.py                   # 테스트 코드
│   ├── urls.py                    # App URL 설정
│   └── views.py                   # View 정의
│
├── solutions/                     # Django App
│   ├── migrations/                # 데이터베이스 마이그레이션
│   ├── __init__.py                # 이 폴더가 패키지임을 표시
│   ├── admin.py                   # Admin 사이트 설정
│   ├── apps.py                    # App 설정
│   ├── models.py                  # Model 정의
│   ├── serializers.py             # Serializer 정의
│   ├── services.py                # 비즈니스 로직
│   ├── tests.py                   # 테스트 코드
│   ├── urls.py                    # App URL 설정
│   └── views.py                   # View 정의
│
├── utils/                         # 공통 유틸리티
│   ├── decorators/                # 커스텀 데코레이터
│   │   ├── service.py             # 서비스 전용 데코레이터
│   │   └── view.py                # 뷰 전용 데코레이터
│   ├── __init__.py                # 이 폴더가 패키지임을 표시
│   ├── authentication.py          # 커스텀 Authentication Class
│   ├── choices.py                 # 커스텀 Choices
│   ├── constants.py               # 상수
│   ├── helpers.py                 # 공통 헬퍼 함수
│   └── serializer_fields.py       # 커스텀 시리얼라이저 필드
│
├── env_example/                   # 환경변수 목록
│   ├── .env.base                  # 공통 환경변수
│   ├── .env.dev                   # 개발환경 환경변수
│   └── .env.prod                  # 배포환경 환경변수
│
├── .gitignore                     # Git 제외 설정
├── README.md                      # 리드미
├── manage.py                      # 명령어 실행 도구
└── requirements.txt               # 의존성 목록
```
