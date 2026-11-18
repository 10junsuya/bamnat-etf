# 노몬 운영 안내

2026-11-16 기준. 시간은 모두 한국 시간이에요. "AI 팀 역할"과 "내 일정·승인 규칙"을 합친 문서예요. 바꾸고 싶은 게 있으면 말씀만 하시면 이 문서와 AI 설정을 같이 고쳐요. 팀 규칙 원문은 `ops/RULES.md`예요.

## 1. 노몬은 이렇게 돌아가요

| 단계 | 누가 | 무엇을 |
|---|---|---|
| ① 숫자 모으기 | 자동 수집 프로그램 (GitHub) | 미국 시세·종가, 국내 기준가, 환율, 구성종목, 매크로 지표를 정해진 시각마다 받아요 |
| ② 실시간 중계 | 실시간 서버 (Cloudflare) | 2분마다 한국투자증권에서 국내 ETF·미국 종목 시세를 미리 받아 창고에 두고, 앱이 열려 있으면 보고 있는 ETF는 1분마다 직접 받아 와요 (10장 그림) |
| ③ 소식 찾기 | Scout (프로그램) | 10분마다 담긴 회사의 새 기사 제목·링크와 공시를 모아요 |
| ④ 확인하고 반영 | AI 팀 | 공식 출처로 확인한 일정·실적·소식을 앱 데이터에 한국어로 넣어요 |
| ⑤ 점검 | Vernon · Argus · Keene · Sterling | 숫자·서버·화면·팀 전체를 따로 점검해요 |
| ⑤-2 보안 | 보안 검사 (프로그램) | 올릴 때마다·매일 새벽 키 유출·위험한 데이터·서버 방어를 검사해요 (9장) |
| ⑥ 보고 | Conrad | 아침마다 브리핑·회의록을 만들고, 승인이 필요한 것을 번호로 모아요 |
| ⑦ 결정 | 대표님 | 디자인·코드·새 회사·규칙·공개처럼 중요한 것은 대표님 승인 뒤에만 바뀌어요 |

## 2. 하루 흐름

| 시각 | 일 |
|---|---|
| 06:17 | 미국 장 마감 뒤 숫자 받기 + 오늘 ETF 예측을 적중 기록에 저장 (저장한 예측은 고치지 않아요) |
| 06:41 (평일) | 아침 알림: 대표 지수와 많이 오르고 내릴 ETF 예상 (휴대폰) |
| 07:49 | Conrad 일일 브리핑 + 전날 회의록 (알림 · 카카오 메일 · PDF) |
| 08:17~22:17, 2시간마다 | 보고서·회의록 PDF를 바탕화면 GNOMON 폴더에 (컴퓨터가 켜져 있을 때) |
| 08:21 · 18:21 | Vernon 숫자 점검 |
| 09:23 · 22:53 | 매크로 지표 받기 (발표 뒤 30분 시장 반응 포함) |
| 13:37 | 공식 기준가 받기 → 어제 예측 채점 |
| 매시 4분 · 34분 | Archer 일정 리서치 · Quill 편집 |
| 매시 13분 · 43분 | Wren 회사 소식 (소식이 나오고 대략 30~40분 안에 앱에 반영) |
| 03:29 | 보안 검사 (키·개인정보·위험 데이터·서버 방어 시험) |
| 08:07 (평일) | 실시간 서버에 오늘 쓰는 종목 목록 반영 |
| 발표 시간대 매시 23분 · 53분 | Tally 실적 (05~09시 · 14~17시 · 20~23시, 월~토) |
| 월·수·금 19:37 | Archer 시장 공부 |
| 밤 9시까지 | (있으면) 대표님 승인 답장 → 그날 밤 반영 |

## 3. AI 팀 역할

| 이름 | 종류 | 하는 일 | 언제 |
|---|---|---|---|
| **Conrad** | AI · 운영 책임자 | 팀 의견 정리·결정, 아침 브리핑·회의록, 승인 대기 목록, 실수 노트 정리 | 01:49 · 07:49 · 13:49 · 19:49 |
| **Sterling** | AI · 감사 | 팀 전체를 독립적으로 점검해 대표님께 직접 보고 | 토 08:49 |
| **Archer** | AI · 리서치 | 실적 발표·회사 이벤트(제품 발표, 로켓 발사 등) 일정 변동과 결과 찾기 | 매시 4분 |
| **Archer · 시장 공부** | AI · 리서치 | 싱크탱크·연준·주요 매체 분석을 읽고 공부 노트 정리, 금요일엔 적중 기록 보고 계산 개선 제안 | 월·수·금 19:37 |
| **Quill** | AI · 편집 | 확인된 일정·회사 이벤트 결과·사업 매출을 앱에 반영 | 매시 34분 |
| **Tally** | AI · 실적 | 실적이 나오면 실적 카드와 실적 일정 분석을 1시간 안에 갱신 | 발표 시간대 30분마다 |
| **Wren** | AI · 회사 소식 | 기사·공시를 공식 출처로 확인해 회사 화면 「최근 소식」·「주요 제품」을 한국어로 갱신 | 30분마다 |
| **Vernon** | AI · 숫자 품질 | 앱 숫자를 원 출처와 대조, 자동 수집 점검 | 08:21 · 18:21 |
| **Argus** | 프로그램 · 경비 | 서버·자동 수집·큰 움직임·데이터 검사, 보안 감시(서버를 직접 찔러 방어 확인), 긴급이면 바로 알림 | 10분마다 |
| **Scout** | 프로그램 · 소식 감지 | 담긴 회사의 새 기사 제목·링크와 공시를 대기 목록에 | 10분마다 |
| **Keene** | 프로그램 · 화면 QA | 앱이 바뀌면 화면 검사 | 앱이 바뀔 때 |
| **아침 알림** | AI · 알림 | 미국 장 마감 뒤 예상을 휴대폰 알림으로 | 평일 06:41 |
| **폴더 정리** | AI · 비서 | 보고서·회의록 PDF를 바탕화면 폴더에 | 2시간마다 |

**회사 소식 흐름**: Scout가 10분마다 기사·공시를 모아요 → Wren이 중요한 사건만 골라 회사 발표·공시로 확인해요 → 확인되면 "공식", 믿을 만한 언론 보도만 있으면 "보도"로 표시해 우리 말 한 줄로 넣어요. 기사 본문은 옮기지 않아요.

## 4. 대표님이 받는 것과 할 일

| 언제 | 누가 | 받는 것 | 할 일 |
|---|---|---|---|
| 평일 06:41 | 아침 알림 | 오늘 ETF 예상 (휴대폰 알림) | 보기만 |
| 매일 07:49 | Conrad | 일일 브리핑 + 전날 회의록 (알림 · 카카오 메일 · PDF) | 승인할 게 있으면 번호로 답장 |
| 매일 밤 9시까지 | 대표님 | | (있으면) "1번 승인", "2번 보류" → 그날 밤 반영, 다음 날 브리핑에 결과 |
| 아무 때나 | Conrad · Argus | 긴급 알림 (앱 숫자 오류, 데이터 끊김, 회사 이벤트 실패 등) | 필요하면 답장 |
| 토요일 08:49 | Sterling | 주간 감사 보고서 (알림 · 카카오 메일) | 고칠 항목 번호로 답장 (선택) |
| 일요일 21:23 | 주간 백업 | 바탕화면 GNOMON/백업에 저장소 전체 백업 파일 | 없음 |
| 일요일 20~22시 | 대표님 | 19:49에 Conrad가 "이번 주 승인 대기 목록"을 보내요 | 주간 승인 시간: 번호로 정리 |
| 매달 첫째 일요일 | Conrad | 월간 정리 (팀 평가, 규칙 변경 제안) | 규칙 변경 승인 여부 결정 |

- 답이 없으면 그 항목은 보류예요. 자동으로 승인한 것으로 치지 않아요. 7일 넘게 답이 없는 항목은 한 번만 다시 알려요.
- 밤 12시~아침 7시에는 앱 숫자 오류처럼 정말 급한 것만 바로 알리고, 나머지는 아침 브리핑에 넣어요.

## 5. 승인이 필요한 것 / 필요 없는 것

**AI가 바로 하는 것 (하고 나서 보고)**
- 공식 출처로 확인된 일정 변경, 회사 이벤트 결과(제품 발표, 로켓 발사 등), 실적 발표 날짜
- 실적 발표 뒤 실적 카드와 "돈은 어디서 버나" 숫자 갱신
- 공식 출처로 확인된 회사 소식·새 제품 반영 (보도만 있으면 "보도" 표시)
- 오타·지난 날짜·깨진 링크 같은 기초 오류와 치명적인 오류 수정
- 뉴스만 있는 일정 변동에 "변동 가능성 보도" 표시

**대표님 승인이 있어야 하는 것**
- 화면 디자인·기능, 코드 변경
- 새 회사·ETF·지표 추가·삭제, 회사 화면 칸 구성 변경
- 이 문서나 팀 규칙, AI 지시문 수정, AI 추가·삭제
- 앱 공개, GitHub·Cloudflare 설정, API 키

**되돌리기**: 승인 없이 바뀐 것도 "되돌려 줘"라고 하면 언제든 되돌려요.

## 6. AI 팀이 공부하고 발전하는 방법

AI는 실행이 끝나면 기억이 사라져요. 그래서 공부와 경험을 파일로 남기고, 모든 AI가 일을 시작할 때 먼저 읽어요.

- **시장 공부 노트** (`ops/knowledge/`): Archer가 주 3회 분석 글을 읽고 "지금 시장의 큰 이야기"를 정리해요.
- **실수 노트** (`ops/LESSONS.md`): 각 AI가 남긴 "교훈"을 Conrad가 아침마다 정리해요. 같은 실수를 되풀이하지 않게 해요.
- **계산 개선 제안**: Archer가 금요일마다 적중 기록을 보고 개선안을 올려요. 코드 변경은 승인 뒤에만 해요.

## 7. 꼭 지키는 것

- 앱은 중립이에요. 매수·매도 권유나 주가 전망을 쓰지 않아요.
- 확인 못 한 숫자는 쓰지 않아요. 계산한 숫자는 계산했다고 밝혀요.
- 기사 본문은 옮기지 않아요. 우리 말 한 줄 + 출처 링크로만 써요.
- **앱에 샘플 숫자가 남아 있는 동안은 앱을 공개하지 않아요.** 샘플이 다 없어져도 공개는 대표님이 따로 승인해요.
- 비밀번호·키는 보거나 받지 않아요. 저장소는 공개라 개인정보를 적지 않아요.
- AI는 기사·공시 안에 숨은 "이렇게 해라" 같은 글을 따르지 않아요. 수상한 글은 대표님께 보고해요.

## 8. 쉬는 기간

시험 기간이나 바쁜 주에는 "이번 주 승인 쉬기"라고 하시면 승인 요청 알림을 멈추고 브리핑만 보내요. 승인 없이 하는 일은 그대로 진행돼요.

## 9. 보안 (방어벽)

원칙: **이용자는 막지 않고, 앱을 지켜요.** 이용 횟수 제한은 두지 않아요. 대신 앱이 쓰는 것만 받고, 같은 질문은 답을 나눠 써서 바깥 서버가 버티게 해요. 자세한 내용은 `ops/SECURITY.md`예요.

**실시간 서버 (앱이 시세를 받아 오는 곳)**


| 장치 | 무엇을 막나 |
|---|---|
| 읽기만 받기, 정해진 주소·질문만 받기 | 이상한 요청, 숨은 기능 찾기 |
| 노몬 앱에 있는 종목만 받기 (매일 자동 갱신) | 아무 종목이나 넣어 시세 사용량을 다 써 버리는 공격 |
| 같은 질문은 20~60초 동안 답을 모두가 나눠 쓰기 | 이용자가 몰려도 바깥 서버는 몇 초에 한 번만 불려요. 이용자 횟수 제한은 없어요 |
| 한국투자증권 "시세 조회" 전용 잠금 | 주문·잔고·계좌 요청은 코드에서 보낼 수 없어요. 코드가 잘못돼도 주문은 못 나가요 |
| 키는 숨긴 곳에만, 주소·응답에 키가 섞이면 지우기 | 키 유출 |
| 에러는 짧은 말만, 보안 헤더 | 내부 정보 노출, 브라우저 공격 |
| 다른 사이트 차단 (공개 때 켜요) | 다른 사이트가 우리 서버를 끌어다 쓰는 것 |

서버를 올리기 전에 **공격 시험 22가지**를 매번 돌려요. 하나라도 실패하면 올리지 않아요. 올린 뒤에도 실제 서버에서 다시 확인해요.

**앱 화면**

- 바깥에서 온 글자는 화면에 넣기 전에 모두 안전하게 바꿔요. 기사 제목에 나쁜 코드를 숨겨 넣어도 실행되지 않아요 (시험 결과: 실행 0번).
- 앱은 우리 서버와 GitHub 데이터에만 연결해요. 바깥 스크립트·폼 전송은 막혀 있어요.

**데이터·키·저장소**

- 데이터에 화면 코드나 위험한 링크가 있으면 검사가 막아요. 링크는 https만 받아요.
- 키·토큰·비밀번호·주민번호·휴대폰 번호·개인 메일이 공개 저장소에 올라가면 검사가 실패로 알려요. GitHub의 비밀 검사·올리기 차단도 켜져 있어요.
- 자동 수집 프로그램은 필요한 권한만 가지고, 쓰는 부품은 버전을 고정해 바꿔치기를 막아요.

**대표님이 직접 하실 것** (보안 설정이라 AI가 바꾸지 않아요)

1. 한국투자증권 키는 노몬 전용 빈 계좌로 받기 (2026-11-16 완료 · 키 만료 2027-11-16, 10월 중순 갱신)
2. GitHub·Cloudflare 2단계 인증 켜기
3. GitHub main 브랜치 강제 덮어쓰기·삭제 금지 켜기
4. 키가 샜다는 의심이 들면 바로 해지하고 새로 받기
5. Claude 데스크톱 앱에서 "노몬 주간 백업" 작업의 "이 컴퓨터 필요(Require this computer)" 켜기

**감시·사고 대응·백업**

- **보안 감시 (10분마다)**: Argus가 실제 서버를 직접 찔러 봐요. 방어가 꺼졌거나, 서버가 느려졌거나, 저장소에 키가 올라왔거나, 보안 장치가 코드에서 지워졌으면 바로 긴급 알림을 보내요.
- **차단 기록**: 서버가 무엇을 왜 막았는지 Cloudflare 로그에 남겨요. IP 같은 개인 정보는 남기지 않아요.
- **긴급 정지 스위치**: 사고가 나면 서버를 바로 멈춰요. 앱은 계속 열리고, 실시간 시세 대신 저장된 숫자로 보여요. Claude에게 "노몬 긴급 정지해 줘"라고 하거나, 휴대폰 GitHub 앱에서 "실시간 서버 배포"를 lockdown 체크하고 실행하면 돼요. 푸는 건 대표님 승인 뒤에만 해요.
- **사고 대응 계획** (`ops/INCIDENT.md`): 키 유출, 서버 공격, 데이터 이상, 계정 탈취, AI 이상 행동 다섯 가지 상황별로 할 일을 순서대로 정해 뒀어요.
- **백업**: GitHub 변경 기록 + 매주 일요일 바탕화면 GNOMON/백업 폴더에 저장소 전체를 저장해요. GitHub 계정이 막혀도 이 파일로 노몬 전체를 되살릴 수 있어요.
- **방화벽(봇 차단)**: Cloudflare 방화벽은 우리 도메인(예: gnomon.kr)이 있어야 켤 수 있어요. 지금 주소에는 걸 수 없어요. 도메인과 방화벽은 앱을 공개한 뒤에 정해요.

**공개 전에 꼭 할 것**: 다른 사이트 차단 켜기(우리 앱 주소만 허용), 이 작업을 안 본 쪽(예: Fable)에서 따로 보안 점검받기, 시세 데이터 공개 이용 조건 확인.

## 10. 그림으로 보는 노몬 구조

<style>.fig{margin:8pt 0 2pt;page-break-inside:avoid}.fig svg text{font-family:'Noto Sans CJK KR','Noto Sans KR',sans-serif}.cap{font-size:9pt;color:#6E6E73;margin:0 0 10pt;text-align:center}</style>

식당에 빗대면 쉬워요. **시장**(한국투자증권 같은 데이터 출처)에서 재료(숫자)가 나오고, **주방**(Cloudflare 서버)이 재료를 받아 오고, **냉장고**(창고)에 미리 넣어 두면, **손님**(이용자 앱)이 와서 바로 꺼내 받아요. **편집부**(AI 팀)는 메뉴판과 오늘의 추천(일정·분석·뉴스)을 써서 보관함(GitHub)에 넣어요.

<div class="fig"><h3>10-1. 전체 구조</h3><svg viewBox="0 0 680 380" width="100%" xmlns="http://www.w3.org/2000/svg"><defs><marker id="a1" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#5F5E5A" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect x="40" y="55" width="160" height="56" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.8"/><text x="120.0" y="74.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#085041">한국투자증권</text><text x="120.0" y="94.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#0F6E56">ETF·미국 주식 시세</text><rect x="40" y="125" width="160" height="56" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.8"/><text x="120.0" y="144.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#085041">야후 파이낸스</text><text x="120.0" y="164.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#0F6E56">지수 선물·환율</text><rect x="40" y="195" width="160" height="56" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.8"/><text x="120.0" y="214.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#085041">Finnhub</text><text x="120.0" y="234.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#0F6E56">예비·대조용</text><rect x="240" y="20" width="220" height="230" rx="16" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.8"/><text x="350" y="40" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#3C3489">Cloudflare 서버 (주방)</text><rect x="260" y="60" width="180" height="56" rx="8" fill="#F1EFE8" stroke="#888780" stroke-width="0.8"/><text x="350.0" y="79.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#2C2C2A">중계 창구</text><text x="350.0" y="99.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#5F5E5A">키 보관, 대신 물어봄</text><rect x="260" y="170" width="180" height="56" rx="8" fill="#F1EFE8" stroke="#888780" stroke-width="0.8"/><text x="350.0" y="189.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#2C2C2A">창고 (냉장고)</text><text x="350.0" y="209.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#5F5E5A">2분마다 미리 저장</text><line x1="350" y1="116" x2="350" y2="168" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a1)"/><line x1="200" y1="88" x2="258" y2="88" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a1)"/><line x1="200" y1="153" x2="238" y2="153" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a1)"/><line x1="200" y1="223" x2="238" y2="223" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a1)"/><rect x="500" y="110" width="140" height="60" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.8"/><text x="570.0" y="131.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#3C3489">이용자 앱 (손님)</text><text x="570.0" y="151.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#534AB7">창고부터 읽음</text><line x1="460" y1="140" x2="498" y2="140" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a1)"/><rect x="40" y="290" width="160" height="56" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.8"/><text x="120.0" y="309.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#085041">AI 팀</text><text x="120.0" y="329.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#0F6E56">일정·분석·뉴스 작성</text><rect x="260" y="290" width="180" height="56" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.8"/><text x="350.0" y="309.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#3C3489">GitHub 저장소</text><text x="350.0" y="329.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#534AB7">데이터 파일 보관함</text><line x1="200" y1="318" x2="258" y2="318" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a1)"/><path d="M440 318 L570 318 L570 172" fill="none" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a1)"/></svg></div>

<p class="cap">그림 1. 노몬 전체 구조 (2026-11-16 기준)</p>

- **시장 (청록색):** 한국투자증권은 국내 ETF 가격·iNAV·종가와 미국 주식 가격을 줘요. 야후는 나스닥·S&P 선물과 환율을, Finnhub는 예비이자 대조용으로 미국 정규장 가격을 줘요.
- **중계 창구:** 한국투자증권 키는 비밀번호 같은 거라 앱에 넣으면 누구나 볼 수 있어요. 그래서 키는 서버 안에만 두고, 앱 대신 서버가 물어봐요. 주문·잔고 요청은 코드에서 막아 둬서 시세만 물을 수 있어요.
- **창고:** 2분마다 서버가 스스로 시세를 받아 넣어 둬요. 손님이 올 때마다 시장에 뛰어가지 않아도 돼요.
- **이용자 앱:** 받은 숫자로 "내일 예상 기준가"를 앱 안에서 직접 계산해요. 서버는 재료만 나르고, 요리는 앱이 해요.
- **AI 팀 → GitHub:** 매초 바뀌지 않는 것(실적 일정, 지표 분석, 뉴스 한 줄, 구성종목, 공시 기준가 기록)은 파일로 올려요.

<div class="fig"><h3>10-2. 시세가 흐르는 길</h3><svg viewBox="0 0 680 400" width="100%" xmlns="http://www.w3.org/2000/svg"><defs><marker id="a2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#5F5E5A" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect x="40" y="30" width="180" height="56" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.8"/><text x="130.0" y="49.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#085041">한국투자증권</text><text x="130.0" y="69.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#0F6E56">주력 시세</text><rect x="250" y="30" width="180" height="56" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.8"/><text x="340.0" y="49.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#085041">야후 파이낸스</text><text x="340.0" y="69.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#0F6E56">선물·환율</text><rect x="460" y="30" width="180" height="56" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.8"/><text x="550.0" y="49.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#085041">Finnhub</text><text x="550.0" y="69.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#0F6E56">예비·대조</text><line x1="130" y1="86" x2="130" y2="168" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a2)"/><text x="138" y="116" text-anchor="start" font-size="12" fill="#444441">ETF 가격·iNAV</text><text x="138" y="134" text-anchor="start" font-size="12" fill="#444441">미국 주식 가격</text><line x1="340" y1="86" x2="340" y2="168" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a2)"/><text x="348" y="116" text-anchor="start" font-size="12" fill="#444441">나스닥·S&amp;P 선물</text><text x="348" y="134" text-anchor="start" font-size="12" fill="#444441">원/달러 환율</text><line x1="550" y1="86" x2="550" y2="168" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a2)"/><text x="558" y="116" text-anchor="start" font-size="12" fill="#444441">미국 종가</text><text x="558" y="134" text-anchor="start" font-size="12" fill="#444441">(대조용)</text><rect x="40" y="170" width="600" height="56" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.8"/><text x="340.0" y="189.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#3C3489">중계 창구 (Cloudflare 서버)</text><text x="340.0" y="209.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#534AB7">숨긴 키로 대신 물어봄 · 주문과 잔고는 막아 둠</text><line x1="110" y1="226" x2="110" y2="298" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a2)"/><text x="118" y="256" text-anchor="start" font-size="12" fill="#444441">2분마다 저장</text><text x="118" y="274" text-anchor="start" font-size="12" fill="#444441">ETF 54·미국 241종목</text><line x1="470" y1="226" x2="470" y2="298" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a2)"/><text x="478" y="256" text-anchor="start" font-size="12" fill="#444441">열어 둔 ETF만</text><text x="478" y="274" text-anchor="start" font-size="12" fill="#444441">1분마다 직접</text><rect x="40" y="300" width="250" height="56" rx="8" fill="#F1EFE8" stroke="#888780" stroke-width="0.8"/><text x="165.0" y="319.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#2C2C2A">창고 (KV)</text><text x="165.0" y="339.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#5F5E5A">최근 가격 묶음 한 덩어리</text><line x1="290" y1="328" x2="378" y2="328" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a2)"/><text x="334" y="314" text-anchor="middle" font-size="12" fill="#444441">한 번에 전부</text><rect x="380" y="300" width="260" height="56" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.8"/><text x="510.0" y="319.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#3C3489">이용자 앱</text><text x="510.0" y="339.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#534AB7">열자마자 창고부터 읽음</text></svg></div>

<p class="cap">그림 2. 화살표마다 오가는 숫자</p>

| 화살표 | 오가는 것 | 얼마나 자주 |
|---|---|---|
| 한국투자증권 → 중계 창구 | 국내 ETF 54개 가격·iNAV·종가, 미국 종목 가격(주간거래·프리마켓·정규장·애프터마켓) | 2분마다 + 보고 있는 ETF는 1분마다 |
| 야후 → 중계 창구 | 나스닥100·S&P500 선물, 원/달러 환율 | 1분마다 |
| Finnhub → 중계 창구 | 미국 정규장 가격 (한국투자증권과 2% 넘게 다르면 "차이 큼" 표시) | 1분마다 |
| 중계 창구 → 창고 | 받은 가격을 한 덩어리 장부로 저장 ("엔비디아 156.7달러, 받은 시각") | 2분마다 |
| 창고 → 앱 | 장부를 통째로 한 번에 | 앱을 열 때 + 1분마다 |
| 중계 창구 → 앱 | 지금 보고 있는 ETF와 그 종목만 직접 | 1분마다 |

<div class="fig"><h3>10-3. 글·일정이 흐르는 길과 앱의 계산</h3><svg viewBox="0 0 680 500" width="100%" xmlns="http://www.w3.org/2000/svg"><defs><marker id="a3" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#5F5E5A" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect x="40" y="30" width="250" height="56" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.8"/><text x="165.0" y="49.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#085041">AI 팀 (Wren·Tally 등)</text><text x="165.0" y="69.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#0F6E56">정해진 시간마다 일함</text><rect x="390" y="30" width="250" height="56" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.8"/><text x="515.0" y="49.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#3C3489">중계 창구·창고</text><text x="515.0" y="69.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#534AB7">그림 2의 서버</text><line x1="165" y1="86" x2="165" y2="158" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a3)"/><text x="175" y="114" text-anchor="start" font-size="12" fill="#444441">실적 일정·지표 분석</text><text x="175" y="132" text-anchor="start" font-size="12" fill="#444441">뉴스 한 줄·구성종목</text><rect x="40" y="160" width="250" height="56" rx="8" fill="#F1EFE8" stroke="#888780" stroke-width="0.8"/><text x="165.0" y="179.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#2C2C2A">GitHub 저장소</text><text x="165.0" y="199.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#5F5E5A">데이터 파일 보관함</text><path d="M165 216 L165 328 L213 328" fill="none" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a3)"/><text x="175" y="254" text-anchor="start" font-size="12" fill="#444441">공시 기준가 기록</text><text x="175" y="272" text-anchor="start" font-size="12" fill="#444441">일정·분석 파일</text><path d="M515 86 L515 328 L467 328" fill="none" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a3)"/><text x="505" y="180" text-anchor="end" font-size="12" fill="#444441">오늘 종가·iNAV</text><text x="505" y="198" text-anchor="end" font-size="12" fill="#444441">미국 종목 등락</text><text x="505" y="216" text-anchor="end" font-size="12" fill="#444441">선물·환율</text><rect x="215" y="300" width="250" height="56" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.8"/><text x="340.0" y="319.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#3C3489">이용자 앱 (계산)</text><text x="340.0" y="339.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#534AB7">재료를 섞어 요리함</text><line x1="340" y1="356" x2="340" y2="408" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a3)"/><text x="350" y="386" text-anchor="start" font-size="12" fill="#444441">계산 결과</text><rect x="215" y="410" width="250" height="56" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.8"/><text x="340.0" y="429.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#085041">화면</text><text x="340.0" y="449.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#0F6E56">종가 → 내일 예상 기준가</text></svg></div>

<p class="cap">그림 3. 파일과 실시간 숫자가 만나 계산되는 곳</p>

| 화살표 | 오가는 것 |
|---|---|
| AI 팀 → GitHub | Wren 지표 발표 분석, Tally 실적 카드, Archer 일정, 매일 아침 구성종목·공시 기준가 기록 |
| GitHub → 앱 | 위 파일들 (앱이 1분마다 새 파일이 있는지 확인) |
| 서버 → 앱 | 오늘 종가·iNAV, 담긴 미국 종목 등락, 선물, 환율 |
| 앱 → 화면 | 계산 결과: "오늘 종가 → 내일 예상 기준가" |

**앱이 계산하는 순서**

1. **출발점:** 오늘 종가 또는 오늘 장 마감 iNAV (한국투자증권)
2. **미국 쪽 움직임:** 담긴 종목마다 "비중 × 등락률"을 더해요. 장이 안 열렸으면 프리마켓·주간거래 가격, 그것도 모자라면 지수 선물로 추정해요.
3. **환율 움직임:** 달러가 오르면 원화 가치도 올라요. 환헤지(H) ETF는 빼요.
4. **결과:** 출발점 × (1 + 미국 쪽 움직임) × (1 + 환율 움직임)

예시 (숫자는 설명용 · 계산값): 오늘 종가 25,150원, 미국 쪽 −0.60%, 환율 +0.10%라면 25,150 × 0.994 × 1.001 ≈ **25,024원**.

<div class="fig"><h3>10-4. 앱을 열 때 일어나는 순서</h3><svg viewBox="0 0 680 250" width="100%" xmlns="http://www.w3.org/2000/svg"><defs><marker id="a4" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#5F5E5A" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect x="40" y="40" width="125" height="56" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.8"/><text x="102.5" y="59.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#3C3489">앱 열기</text><text x="102.5" y="79.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#534AB7">0초</text><rect x="198" y="40" width="125" height="56" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.8"/><text x="260.5" y="59.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#3C3489">창고 한 번 읽기</text><text x="260.5" y="79.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#534AB7">약 1초</text><rect x="356" y="40" width="125" height="56" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.8"/><text x="418.5" y="59.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#3C3489">계산해서 그리기</text><text x="418.5" y="79.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#534AB7">1~2초</text><rect x="514" y="40" width="125" height="56" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.8"/><text x="576.5" y="59.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#3C3489">보는 ETF 갱신</text><text x="576.5" y="79.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#534AB7">1분마다</text><line x1="165" y1="68" x2="196" y2="68" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a4)"/><line x1="323" y1="68" x2="354" y2="68" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a4)"/><line x1="481" y1="68" x2="512" y2="68" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a4)"/><rect x="198" y="150" width="283" height="56" rx="8" fill="#F1EFE8" stroke="#888780" stroke-width="0.8"/><text x="339.5" y="169.0" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#2C2C2A">서버: 2분마다 창고 채우기</text><text x="339.5" y="189.0" text-anchor="middle" dominant-baseline="central" font-size="12" fill="#5F5E5A">손님이 없어도 혼자 계속 돌아요</text><line x1="260" y1="148" x2="260" y2="98" stroke="#5F5E5A" stroke-width="1.2" marker-end="url(#a4)"/></svg></div>

<p class="cap">그림 4. 위 줄은 손님(앱), 아래 회색은 주방(서버)이 혼자 하는 일</p>

### 10-5. 시간대별로 숫자를 어디서 받나 (한국 시간, 겨울 기준)

| 시간 | 국내 ETF | 미국 주식 | 예상 기준가에 쓰는 것 |
|---|---|---|---|
| 09:00~15:30 | 한국투자증권 실시간 가격·iNAV | 주간거래 (10:00~18:00) | 주간거래 가격, 모자라면 선물 |
| 15:30~18:00 | 종가·장 마감 iNAV | 주간거래 | 주간거래 가격, 모자라면 선물 |
| 18:00~23:30 | (장 마감) | 프리마켓 | 담긴 종목 프리마켓 가격, 모자라면 선물 |
| 23:30~06:00 | (장 마감) | 정규장 (Finnhub로 대조) | 실제 정규장 등락 |
| 06:00~09:00 | (장 마감) | 애프터마켓 (참고만) | 정규장 종가로 확정 · 애프터마켓은 안 넣어요 |

미국 서머타임(3월~11월 초)에는 미국 쪽 시간이 1시간씩 앞당겨져요. 16:00~20:00 한국 시간외(애프터마켓) 가격을 받을 수 있는지는 한국투자증권에 문의 중이에요.

### 10-6. 2026-11-16 연결하며 생긴 문제와 해결

| 증상 | 원인 | 해결 |
|---|---|---|
| 숫자가 전부 0.00% | 한 번에 너무 많이 물어서 무료 한도(요청 한 번에 바깥 호출 50번)를 넘음 | 8개·10개씩 나눠 묻기 |
| 숫자가 몇 분 뒤에야 뜸 | 새 키라 호출 한도가 낮은데, 다 받은 뒤에야 화면을 그림 | 선물 먼저, 오는 대로 바로 그리기 |
| 받은 값이 사라짐 | 1분마다 받는 GitHub 파일이 실시간 값을 덮어씀 | 실시간 값은 그대로 이어 가기 |
| 옛 화면 → 3분 뒤 새 화면 | 그 ETF 차례가 올 때까지 기다림 | 열면 그 ETF만 바로 받기 + 창고 |
| Claude 옆 창에서 전부 0% | claude.ai 아티팩트는 바깥 연결이 막혀 있음 | 실시간 확인은 바탕화면 「노몬 앱.html」로 |
| 토큰 발급 알림이 두 번 | 지역 서버마다 토큰을 따로 받음 | 창고에 토큰 하나만 두고 같이 써요 (하루 1번 원칙) |

### 10-7. 키와 안전: 무엇이 어디에 있나

| 무엇 | 어디에 | 없는 곳 |
|---|---|---|
| App Key · App Secret | GitHub Secrets → 배포 때 Cloudflare 비밀값 | 앱 파일, 공개 저장소, 채팅, 창고 |
| 하루짜리 토큰 | Cloudflare 창고 (23시간 재사용) | 앱, 저장소 |
| 노몬 전용 계좌 | 한국투자증권 (잔고 0원 유지 권장) | 주문 코드는 서버에서 막혀 있어요 |
| 계좌번호 · 비밀번호 | 대표님만 | 어디에도 적지 않아요 |

### 10-8. 무료 한도와 공개 때 바꿀 것

| 한도 | 지금 | 그래서 |
|---|---|---|
| Cloudflare 요청 | 하루 10만 번 | 공개 초기는 충분해요 |
| 요청 한 번에 바깥 호출 | 50번 | 국내 ETF 8개, 미국 10개씩 나눠 받아요 |
| 창고 쓰기 | 하루 1,000번 | 2분마다(하루 720번)가 최선이에요 |
| 한국투자증권 호출 | 초당 한도 있음 (새 키는 처음 며칠 더 낮음) | 창고에 모아서 이용자 수와 상관없이 일정하게 물어요 |
| 한국투자증권 토큰 | 하루 1번 발급 원칙 | 창고에 하나만 둬요 |

**공개할 때 바꿀 것**

1. 앱을 바탕화면 파일에서 웹 주소로 옮기기 (Cloudflare Pages 등, 무료)
2. Cloudflare Workers 유료(월 5달러 안팎, 올릴 때 다시 확인)로 올리기 → 창고 1분 주기, 한도 확대
3. 실시간 연결(웹소켓): 지금 보고 있는 화면의 종목만 1초 단위로
4. 시세를 이용자에게 보여줘도 되는지 한국투자증권 답변 확인 (2026-11-16 이메일 문의)
5. 다른 사이트 차단 켜기 (우리 앱 주소만 허용)

### 10-9. 증권사 앱과 비교

| | 증권사 | 노몬 (지금) |
|---|---|---|
| 시세 출처 | 거래소 원본 (코스콤 전용선, 시세 공급업체) | 한국투자증권 Open API (개인용) |
| 전달 방식 | 바뀔 때마다 밀어주기 (실시간) | 2분마다 미리 받기 + 앱이 1분마다 묻기 |
| 이용 허락 | 거래소 정보이용계약 (유료) | 확인 중 |
| 실시간 범위 | 화면에 보이는 종목·관심종목만 | — |

### 10-11. 새 ETF 넣는 순서 (2026-11-18 정리, 승인 14번)
1. `data/etfs.json` 에 그룹(groups)과 ETF([코드, 이름, 그룹])를 넣어요. 커버드콜이면 `cc`(참여율과 설명), 환헤지면 `hedge: true`.
2. `python3 scripts/check_data.py --embed` → 구성종목 수집(`gh workflow run holdings.yml`).
3. **새로 들어온 구성종목을 `index.html` 의 STOCKS 에 한글 이름으로 추가**해요(빠지면 회사 카드를 못 채우고 Argus 가 계속 알려요). ETF 를 담는 경우(QQQM 등)는 회사 카드 분야를 '다른 ETF'로.
4. `python3 scripts/gen_allow.py` 로 실시간 서버 허용 목록을 다시 만들고 push(서버 자동 배포).
5. 시세 수집(`gh workflow run live.yml`) 뒤 앱 점검 오류 0 확인 → Quill 에게 새 회사 카드 요청.

### 10-10. 용어 사전

| 용어 | 뜻 |
|---|---|
| 기준가 (NAV) | ETF 1주에 담긴 자산의 실제 가치. 하루 한 번 공시돼요 |
| iNAV | 장중에 몇 초마다 추정해 주는 기준가 |
| 선물 | 미래 가격을 미리 사고파는 시장. 미국 장이 닫혀 있을 때 분위기를 보여줘요 |
| 주간거래·프리마켓·애프터마켓 | 미국 정규장 밖에서 거래되는 시간. 거래가 적어 가격이 튈 수 있어요 |
| API | 프로그램끼리 정해진 방식으로 데이터를 주고받는 창구 |
| 서버 | 24시간 켜져 있는 남의 컴퓨터. 노몬은 Cloudflare 것을 빌려 써요 |
| 창고 (KV) | 서버에 붙은 작은 저장소. 이름표(키) 하나에 값 하나를 넣어요 |
| 크론 | "2분마다", "매일 06:17"처럼 정해진 시간에 자동으로 일을 시키는 예약 |
| 토큰 | 한국투자증권이 "이 키는 확인됐어요"라고 주는 하루짜리 입장권 |
| 웹소켓 | 계속 열어 두는 연결. 값이 바뀌면 상대가 바로 밀어줘요 |
| 아티팩트 | Claude 안에서 보는 미리보기 화면. 바깥 연결이 막혀 있어서 실시간 숫자는 안 들어와요 |
