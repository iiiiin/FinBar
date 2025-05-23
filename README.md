## 250522

### 의제

#### 공통
* 역할 분담
* notion을 활용한 개발 계획(backlog) 설정

#### 프론트
* Figma 와이어 프레임 설정 ✅
* 컴포넌트 구조 설정 
* 사용자 로그인, 회원가입 페이지 구현 ✅

#### 백
* 사용자 로그인 구현 ✅
* 사용자 회원가입 구현 ✅

### 이슈 및 결정 사항
* 회원가입 시 입력받는 값
	`username`, `password`, `email`, `nickname`  
	(커뮤니티 기능을 위해, USER 모델에 `nickname` 컬럼 추가)

* local storage 와 pinia 연동, 상태 저장 및 삭제 기능
* Pinia Plugin Persistedstate 문서 확인

* token 인증 방식 사용

* 추후 대댓글 기능(테이블) 추가 예정
* 댓글 수정 기능 (테이블) 추가 완료
* 회원가입 시 나이 입력 받기

* (FE, BE) 회원 정보 수정 기능 구현
* (FE) firebase 배포 시 https 여부 확인 
* (BE) settings.SECRET_KEY `.env`에 추가 ✅
* (BE) API 문서화 ✅


### 다음 의제

* (FE, BE) 커뮤니티 기능 구현 예정
* (FE) 웹 페이지 디자인 선정