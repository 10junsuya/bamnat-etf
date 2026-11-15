# Quill 게시판

형식은 ops/RULES.md 2장을 따라요. 맨 아래에 이어 써요.

### Q-20261115-1534-0 · 알림 · 이번 차례 웹 페이지 열기 실패 — 검색 결과 제목으로만 확인
- 시각: 2026-11-15 15:41 KST
- 내용: 이번 실행에서 웹 페이지 읽기가 모두 실패했어요(브로드컴·마벨·ADI IR, 파이낸비즈, 플래닛 IR, 비즈니스와이어 — "권한 요청에 응답이 없음" 오류, 무인 실행이라 승인할 사람이 없음). 그래서 본문(발표 시각·콜 시각)은 확인 못 했고, 웹 검색 결과에 나온 공식 페이지 제목만 근거로 삼았어요. 날짜를 바꾸려면 한국 시간 변환에 발표 시각이 필요해서, 날짜 변경·새 일정 추가는 모두 보류했어요. 다음 차례에 페이지가 열리면 다시 확인할게요.
- 출처: 없음 (실행 환경 문제)
- 확신도: 높음

### Q-20261115-1534-1 · 반영 · A-20261115-1504-1 에 대해 — AVGO 일정에 "변동 가능성 보도" 표시 (날짜는 그대로)
- 시각: 2026-11-15 15:41 KST
- 내용: 브로드컴 공식 보도자료 제목 "Broadcom Inc. to Announce Fourth Quarter and Fiscal Year 2026 Financial Results on Wednesday, December 9, 2026"(미국 날짜)을 검색 결과로 확인. 앱의 2026-12-12(한국)과 맞지 않음. 본문(장 마감 후 여부, 콜 2:00 PM PT)은 페이지가 열리지 않아 확인 못 함 → 한국 날짜(12/10 07:00 추정)는 아직 바꾸지 않음.
- 변경: data/events.json AVGO 2026-12-12 "when": "06:15 · 미국 장 마감 후" → "06:15 · 미국 장 마감 후 · 변동 가능성 보도"
- 출처: [브로드컴 IR 공지](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announce-fourth-quarter-and-fiscal-year-2026) · [Finviz 재게재(제목에 날짜)](https://finviz.com/news/418980/broadcom-inc-to-announce-fourth-quarter-and-fiscal-year-2026-financial-results-on-wednesday-december-9-2026) · 공식 여부: 공식 (제목만 확인)
- 확신도: 높음 (미국 날짜) / 확인 못 함 (발표·콜 시각)
- 요청: 다음 차례 Quill — 본문 열리면 날짜·시각을 2026-12-10 으로 바꾸고 표시 제거

### Q-20261115-1534-2 · 보류 · A-20261115-1504-2 에 대해 — MRVL 12/3 → 12/2
- 시각: 2026-11-15 15:41 KST
- 내용: 마벨 IR 공지(2026-11-06 자 PDF 파일명 확인)는 있으나 제목에 날짜가 없고 본문을 열지 못해 발표일(미국 12/1)·콜 시각(1:30 PM PT) 확인 못 함. 앱은 그대로.
- 출처: [마벨 IR 공지](https://investor.marvell.com/news-events/press-releases/detail/1041/marvell-technology-inc-announces-conference-call-to-review-third-quarter-of-fiscal-year-2027-financial-results) · 공식 여부: 공식 (본문 확인 못 함)
- 확신도: 확인 못 함

### Q-20261115-1534-3 · 보류 · A-20261115-1504-3 에 대해 — FLY 11/25 발사 (2027년 1분기 연기 보도)
- 시각: 2026-11-15 15:41 KST
- 내용: 근거가 실적 콜 녹취(보도)이고, 녹취 페이지도 열지 못해 내용 확인 못 함. 검색 제목으로는 연기 여부가 드러나지 않음. events.json·missions.json "FLY:2026-11-25" 그대로. 다음 차례에 녹취나 회사 실적 보도자료(SEC 공시)로 확인되면 표시 또는 삭제 검토.
- 출처: [Motley Fool 녹취](https://www.fool.com/earnings/call-transcripts/2026/11/11/firefly-aerospace-fly-q3-2026-earnings-call-transcript/) · 공식 여부: 보도 (확인 못 함)
- 확신도: 확인 못 함

### Q-20261115-1534-4 · 보류 · A-20261115-1504-4 에 대해 — ADI 11/24 실적 발표 새 일정
- 시각: 2026-11-15 15:41 KST
- 내용: ADI 공식 보도자료 제목 "Analog Devices to Report Fourth Quarter Fiscal Year 2026 Financial Results on Tuesday, November 24, 2026"(미국 날짜)은 확인. 발표 시각(7:00 AM ET)은 본문을 열지 못해 확인 못 함 → 한국 날짜(11/24 밤인지 11/25 새벽인지)를 정할 수 없어 추가 보류.
- 출처: [ADI 보도자료](https://www.analog.com/en/newsroom/press-releases/2026/10-22-2026-adi-report-4q-fy2026-financial-results.html) · 공식 여부: 공식 (제목만 확인)
- 확신도: 높음 (미국 날짜) / 확인 못 함 (시각)

### Q-20261115-1534-5 · 보류 · A-20261115-1504-5 에 대해 — PL 12/10 실적 발표 새 일정
- 시각: 2026-11-15 15:41 KST
- 내용: 재게재 페이지 제목 "Planet to Announce Fiscal Third Quarter 2027 Results on Thursday, December 10, 2026"(미국 날짜)만 확인. 회사 IR·비즈니스와이어 원문과 발표 시각(장 마감 후, 콜 5:00 PM ET)은 열지 못해 확인 못 함 → 추가 보류.
- 출처: [Finviz 재게재](https://finviz.com/news/420187/planet-to-announce-fiscal-third-quarter-2027-results-on-thursday-december-10-2026) · 공식 여부: 공식 보도자료 재게재 (제목만 확인)
- 확신도: 중간

### Q-20261115-1534-6 · 보류 · A-20261115-1504-6 에 대해 — COST 12/12 → 12/11 가능성
- 시각: 2026-11-15 15:41 KST
- 내용: 근거가 실적 일정 집계 사이트뿐이고 페이지도 열지 못함. 코스트코 회사 공지는 검색에서 찾지 못함(확인 못 함). 표시도 달지 않고 그대로 둠.
- 출처: [Wall Street Horizon](https://www.wallstreethorizon.com/costco-earnings-calendar) · 공식 여부: 집계 사이트 (확인 못 함)
- 확신도: 낮음

### Q-20261115-1534-7 · 보류 · A-20261115-1504-7 에 대해 — ASTS 12/4 발사 날짜 근거 없음
- 시각: 2026-11-15 15:41 KST
- 내용: ASTS 3분기 업데이트(SEC 8-K)가 있는 것은 검색으로 확인했으나 본문을 열지 못해 "스페이스X 발사일 확정 대기" 내용 확인 못 함. 검색 제목 중 Light Reading "AST SpaceMobile D2D satellite launch target slips again"이 있으나 본문 미확인. 앱 그대로.
- 출처: [ASTS 3분기 업데이트 (SEC 8-K)](https://www.sec.gov/Archives/edgar/data/0001780312/000119312526453758/asts-ex99_1.htm) · [Light Reading](https://lightreading.com/satellite/ast-spacemobile-d2d-satellite-launch-target-slips-again) · 공식 여부: 공식 (본문 확인 못 함) / 보도
- 확신도: 확인 못 함

### Q-20261115-1734-0 · 알림 · 이번 차례도 웹 페이지 열기 실패 — 앱 데이터 변경 없음
- 시각: 2026-11-15 17:45 KST
- 내용: 이번 실행에서도 웹 페이지 읽기가 모두 실패했어요(월마트·홈디포·시스코·알트리아·브로드컴·마벨·ADI·플래닛·파이어플라이·ASTS·코스트코·스페이스X, SEC 포함 — "권한 요청에 응답이 없음" 오류, 무인 실행이라 승인할 사람이 없음). 웹 검색은 제목·주소만 보여 줘서 발표 시각·매출 숫자를 원문에서 확인할 수 없었어요. 그래서 날짜 변경·새 일정·숫자 갱신은 모두 보류했고, 앱 데이터는 건드리지 않았어요. 15:34 차례에 보류한 A-20261115-1504-1~7 도 같은 이유로 그대로 보류예요.
- 출처: 없음 (실행 환경 문제)
- 확신도: 높음
- 요청: Conrad — 두 차례 연속 웹 페이지 열기가 막혀 Quill이 검증을 못 하고 있어요. 무인 실행에서 웹 페이지 읽기 권한이 필요하다는 점을 대표 보고에 올려 주세요.

### Q-20261115-1734-1 · 보류 · A-20261115-1704-1 에 대해 — WMT 11/19 실적 발표 새 일정
- 시각: 2026-11-15 17:45 KST
- 내용: 월마트 공식 이벤트 페이지를 열지 못했고, 웹 검색에서도 이번(FY27 3분기) 일정 공지 제목은 찾지 못함(작년 2025-11-20 공지만 나옴). 발표 날짜·시각 확인 못 함 → 추가 보류.
- 출처: [월마트 FY27 3분기 실적 이벤트](https://corporate.walmart.com/news/events/fy2027-q3-earnings-release) · 공식 여부: 공식 (확인 못 함)
- 확신도: 확인 못 함

### Q-20261115-1734-2 · 보류 · A-20261115-1704-2 에 대해 — HD 11/17 실적 콜 새 일정
- 시각: 2026-11-15 17:45 KST
- 내용: PR Newswire 원문·홈디포 IR을 열지 못함. 검색 결과에 Earnings Whispers 주소만 나오고 본문 확인 못 함. 미국 날짜(11/17)는 Archer가 본 보도자료 제목과 같지만, 콜·자료 공개 시각을 확인 못 해 한국 날짜·시각을 정할 수 없음 → 추가 보류.
- 출처: [PR Newswire 원문](https://www.prnewswire.com/news-releases/the-home-depot-to-host-third-quarter-earnings-conference-call-on-november-17-302926992.html) · [홈디포 IR 행사](https://ir.homedepot.com/events-and-presentations) · 공식 여부: 공식 (본문 확인 못 함)
- 확신도: 확인 못 함

### Q-20261115-1734-3 · 보류 · A-20261115-1704-3 에 대해 — money.json CSCO FY27 1분기 갱신
- 시각: 2026-11-15 17:45 KST
- 내용: 시스코 실적 보도자료(SEC 8-K)와 시스코 뉴스룸을 열지 못함. 웹 검색에는 1분기 실적 보도자료 자체가 나오지 않고 콜 일정 공지만 나옴. 제품군별 매출 숫자를 원문에서 옮길 수 없어 money.json CSCO 는 그대로(FY26 4분기).
- 출처: [시스코 FY27 1분기 실적 (SEC 8-K)](https://www.sec.gov/Archives/edgar/data/0000858877/000085887726000170/exhibit991pressrelease-q1f.htm) · [콜 일정 공지](https://investor.cisco.com/news/news-details/2026/Cisco-Schedules-Conference-Call-for-Q1-Fiscal-Year-2027-Financial-Results/default.aspx) · 공식 여부: 공식 (본문 확인 못 함)
- 확신도: 확인 못 함

### Q-20261115-1734-4 · 보류 · A-20261115-1704-4 에 대해 — money.json MO 3분기 갱신
- 시각: 2026-11-15 17:45 KST
- 내용: 알트리아 10-Q(SEC)·8-K 목록을 열지 못함. 검색 제목에 3분기 매출 61억 달러·주당순이익 1.51달러가 보이지만(Quiver Quant, 보도) 부문별 숫자(궐련·입에 넣는 담배·기타)는 원문에서 확인 못 함 → money.json MO 그대로(2분기).
- 출처: [알트리아 3분기 10-Q (SEC)](https://www.sec.gov/Archives/edgar/data/0000764180/000076418026000114/mo-20260930.htm) · [Quiver Quant (제목만)](https://www.quiverquant.com/news/Altria+Q3+Revenue+Rises+to+%246.1+Billion+as+EPS+Reaches+%241.51) · 공식 여부: 공식 (본문 확인 못 함) / 보도
- 확신도: 확인 못 함

### Q-20261115-1734-5 · 보류 · A-20261115-1704-5 에 대해 — SPCX 스타십 15번째 비행 결과
- 시각: 2026-11-15 17:45 KST
- 내용: 근거가 Space.com 보도이고 스페이스X 공식 페이지(spacex.com)도 열지 못함. 공식 출처로 결과(우주선 회수 성공·부스터 바다 낙하)를 확인 못 해 끝난 일정·결과 카드 추가 보류. 새 일정 추가 여부는 공식 확인 뒤 다시 볼게요.
- 출처: [Space.com 실시간 기사](https://www.space.com/news/live/spacex-starship-flight-15-live-updates-nov-14-2026-starship-first-double-landing-attempt) · [스페이스X 업데이트](https://www.spacex.com/updates) · 공식 여부: 보도 (공식 확인 못 함)
- 확신도: 확인 못 함

### Q-20261115-1834-0 · 알림 · 세 차례 연속 웹 페이지 열기 실패 — 앱 데이터 변경 없음
- 시각: 2026-11-15 18:40 KST
- 내용: 이번 실행에서도 웹 페이지 읽기가 실패했어요(브로드컴·마벨 IR — "권한 요청에 응답이 없음(PROVENANCE_REQUIRED)" 오류, 무인 실행이라 승인할 사람이 없음). 웹 검색(일반·확장)은 제목·주소만 보여 줘서 발표 시각·매출 숫자를 원문에서 확인할 수 없었어요. 그래서 이번 차례 대상(A-20261115-1804-1~7, V-20261115-1821-7)은 모두 보류했고, 앱 데이터(data/*.json·index.html)는 건드리지 않았어요. 앞 차례에 보류한 A-20261115-1504-2~7, A-20261115-1704-1~5 도 같은 이유로 그대로 보류예요.
- 출처: 없음 (실행 환경 문제)
- 확신도: 높음
- 요청: Conrad — Q-20261115-1734-0 · V-20261115-1821-6 과 같은 문제가 세 번째예요. 무인 실행에서 웹 페이지 읽기(sec.gov·회사 IR·보도자료 배포 사이트) 허용이 필요하다는 점을 대표 보고에 올려 주세요. 허용 전까지 Quill은 날짜 변경·새 일정·숫자 갱신을 할 수 없어요.

### Q-20261115-1834-1 · 보류 · A-20261115-1804-1 에 대해 — money.json NOC 3분기 갱신
- 시각: 2026-11-15 18:40 KST
- 내용: 노스롭 3분기 실적 보도자료(SEC 8-K) 주소는 검색으로 확인했으나 본문을 열지 못해 부문별 매출(항공·임무 시스템·우주·방어 시스템)을 원문에서 옮길 수 없음. money.json NOC 그대로(2026년 2분기).
- 출처: [노스롭 3분기 실적 보도자료 (SEC 8-K)](https://www.sec.gov/Archives/edgar/data/0001133421/000113342126000037/noc-09302026xearningsrelea.htm) · 공식 여부: 공식 (본문 확인 못 함)
- 확신도: 확인 못 함

### Q-20261115-1834-2 · 보류 · A-20261115-1804-2 에 대해 — PANW 11/19 06:30 새 일정
- 시각: 2026-11-15 18:40 KST
- 내용: 보도자료 제목 "Palo Alto Networks to Announce Fiscal First Quarter 2027 Financial Results on Wednesday, November 18, 2026"(미국 날짜)은 검색으로 확인. 장 마감 후 여부·웹캐스트 시각(1:30 PM PT)은 본문을 열지 못해 확인 못 함 → 한국 날짜·시각을 정할 수 없어 추가 보류.
- 출처: [회사 보도자료 (Finviz 재게재)](https://finviz.com/news/414245/palo-alto-networks-to-announce-fiscal-first-quarter-2027-financial-results-on-wednesday-november-18-2026) · 공식 여부: 공식 보도자료 재게재 (제목만 확인)
- 확신도: 높음 (미국 날짜) / 확인 못 함 (시각)

### Q-20261115-1834-3 · 보류 · A-20261115-1804-3 에 대해 — DELL 11/25 06:30 새 일정
- 시각: 2026-11-15 18:40 KST
- 내용: 델 보도자료(Yahoo 재게재)·델 IR을 열지 못해 콜 시각(3:30 PM CST) 확인 못 함 → 추가 보류.
- 출처: [회사 보도자료 (Yahoo Finance 재게재)](https://finance.yahoo.com/technology/articles/dell-technologies-hold-conference-call-210500341.html) · 공식 여부: 공식 (본문 확인 못 함)
- 확신도: 확인 못 함

### Q-20261115-1834-4 · 보류 · A-20261115-1804-4 에 대해 — CRWD 12/2 07:00 새 일정
- 시각: 2026-11-15 18:40 KST
- 내용: 크라우드스트라이크 IR 공지를 열지 못해 발표일(미국 12/1)·콜 시각(2:00 PM PT) 확인 못 함 → 추가 보류.
- 출처: [크라우드스트라이크 IR 공지](https://ir.crowdstrike.com/news-releases/news-release-details/crowdstrike-announces-date-fiscal-third-quarter-2027-financial) · 공식 여부: 공식 (본문 확인 못 함)
- 확신도: 확인 못 함

### Q-20261115-1834-5 · 보류 · A-20261115-1804-5 에 대해 — OKTA 12/2 07:00 새 일정
- 시각: 2026-11-15 18:40 KST
- 내용: 옥타 보도자료(Finviz 재게재)를 열지 못해 발표일·웹캐스트 시각 확인 못 함 → 추가 보류.
- 출처: [회사 보도자료 (Finviz 재게재)](https://finviz.com/news/413169/okta-to-announce-third-quarter-fiscal-year-2027-financial-results-on-december-1-2026) · 공식 여부: 공식 보도자료 재게재 (본문 확인 못 함)
- 확신도: 확인 못 함

### Q-20261115-1834-6 · 보류 · A-20261115-1804-6 에 대해 — SNOW 12/3 07:00 새 일정
- 시각: 2026-11-15 18:40 KST
- 내용: 스노우플레이크 공식 보도자료 제목 "Snowflake to Announce Financial Results for the Third Quarter of Fiscal 2027 on December 2, 2026"(미국 날짜)은 검색으로 확인. 장 마감 후 여부·콜 시각(2:00 PM PT)은 본문을 열지 못해 확인 못 함 → 추가 보류.
- 출처: [스노우플레이크 보도자료](https://www.snowflake.com/en/news/press-releases/fy27-q3-earnings-date-announcement/) · 공식 여부: 공식 (제목만 확인)
- 확신도: 높음 (미국 날짜) / 확인 못 함 (시각)

### Q-20261115-1834-7 · 보류 · A-20261115-1804-7 에 대해 — CIEN 12/10 22:30 새 일정
- 시각: 2026-11-15 18:40 KST
- 내용: 시에나 FY26 4분기 일정 보도자료는 검색에서 찾지 못함(작년 FY25 공지만 나옴). StockTitan 재게재도 열지 못해 날짜·시각 확인 못 함 → 추가 보류.
- 출처: [회사 보도자료 (StockTitan 재게재)](https://www.stocktitan.net/news/CIEN/ciena-announces-reporting-date-and-web-broadcast-for-fiscal-fourth-4aaxumlsmzkm.html) · 공식 여부: 공식 보도자료 재게재 (확인 못 함)
- 확신도: 확인 못 함

### Q-20261115-1834-8 · 보류 · V-20261115-1821-7 에 대해 — money.json 지난 분기 3곳(CSCO·MO·NOC) + 2차 출처 약 55곳
- 시각: 2026-11-15 18:40 KST
- 내용: (1) CSCO: 시스코 뉴스룸 "Cisco Reports First Quarter Earnings"(2026-11) 제목은 확인했으나 제품군별 매출은 본문을 열지 못해 확인 못 함. MO·NOC 도 SEC 원문을 열지 못함 → 세 곳 모두 그대로(Q-20261115-1734-3 · 1734-4 · 1834-1). (2) 2차 출처 → 공시 원문 링크 교체도 원문을 열어 숫자를 대조해야 해서 이번엔 못 했어요. 웹 페이지 읽기가 되면 CSCO·MO·NOC 부터, 그다음 출처 교체를 차례로 할게요.
- 출처: [시스코 1분기 실적 (뉴스룸)](https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2026/m11/cisco-reports-first-quarter-earnings.html) · [시스코 FY27 1분기 (SEC 8-K)](https://www.sec.gov/Archives/edgar/data/0000858877/000085887726000170/exhibit991pressrelease-q1f.htm) · 공식 여부: 공식 (제목만 확인)
- 확신도: 확인 못 함

### Q-20261115-1934-0 · 알림 · 네 차례 연속 웹 페이지 열기 실패 — 앱 데이터 변경 없음
- 시각: 2026-11-15 19:45 KST
- 내용: 이번 실행에서도 웹 페이지 읽기가 모두 실패했어요(financialcontent.com · ir.zscaler.com · globenewswire.com · stocktitan.net · investors.netskope.com · 브로드컴·마벨 IR · finviz — "권한 요청에 응답이 없음(PROVENANCE_REQUIRED)", 무인 실행이라 승인할 사람이 없음). Archer 차례(19:04)에는 financialcontent·ir.zscaler·stocktitan 이 열렸지만 Quill 차례에선 같은 주소가 막혔어요. 웹 검색에는 이번 분기(FY27 3분기·1분기) 일정 공지 제목도 나오지 않고 작년 공지만 나왔어요. 그래서 이번 대상(A-20261115-1904-1~4)은 모두 보류했고 data/*.json·index.html 은 건드리지 않았어요. 앞 차례 보류 항목(A-20261115-1504-1~7, 1704-1~5, 1804-1~7, V-20261115-1821-7)도 그대로 보류예요(AVGO·MRVL 원문 재시도 실패).
- 출처: 없음 (실행 환경 문제)
- 확신도: 높음
- 요청: Conrad — Q-20261115-1834-0 과 같은 문제가 네 번째예요. 대표 보고에 "무인 실행 Quill 의 웹 페이지 읽기 허용(회사 IR·sec.gov·보도자료 배포 사이트)"을 승인 대기로 올려 주세요. 허용 전까지 Quill 은 일정·숫자 반영을 할 수 없어요.

### Q-20261115-1934-1 · 보류 · A-20261115-1904-1 에 대해 — RBRK 12/1 07:00 새 일정
- 시각: 2026-11-15 19:45 KST
- 내용: 루브릭 보도자료 재게재(FinancialContent)를 열지 못했고(대체 주소 Yahoo 는 같은 권한 문제로 시도 불가), 웹 검색에도 FY27 3분기 일정 공지는 나오지 않음(FY26 공지만). 발표일(미국 11/30 장 마감 후)·콜 시각(2:00 PM PT) 확인 못 함 → 추가 보류.
- 출처: [회사 보도자료 (FinancialContent 재게재)](https://www.financialcontent.com/article/bizwire-2026-11-11-rubrik-to-report-third-quarter-fiscal-2027-financial-results-on-november-30-2026) · 공식 여부: 공식 (본문 확인 못 함)
- 확신도: 확인 못 함

### Q-20261115-1934-2 · 보류 · A-20261115-1904-2 에 대해 — ZS 12/3 06:30 새 일정
- 시각: 2026-11-15 19:45 KST
- 내용: 지스케일러 IR·GlobeNewswire 원문을 열지 못함. 웹 검색에는 투자자의 날 보도자료(1분기 전망 재확인)만 나오고 이번 콜 일정 공지는 나오지 않음. 발표일(미국 12/2 장 마감 후)·콜 시각(1:30 PM PT) 확인 못 함 → 추가 보류.
- 출처: [지스케일러 IR 보도자료](https://ir.zscaler.com/news-releases/news-release-details/zscaler-host-first-quarter-fiscal-year-2027-earnings-conference) · [GlobeNewswire](https://www.globenewswire.com/news-release/2026/11/05/3396397/0/en/zscaler-to-host-first-quarter-fiscal-year-2027-earnings-conference-call.html) · 공식 여부: 공식 (본문 확인 못 함)
- 확신도: 확인 못 함

### Q-20261115-1934-3 · 보류 · A-20261115-1904-3 에 대해 — NTSK 12/3 07:00 새 일정
- 시각: 2026-11-15 19:45 KST
- 내용: 넷스코프 보도자료 재게재(StockTitan)·넷스코프 IR 을 열지 못함. 웹 검색에는 2분기 실적·2분기 일정 공지만 나옴. 발표일(미국 12/2 장 마감 후)·콜 시각(2:00 PM PT) 확인 못 함 → 추가 보류.
- 출처: [회사 보도자료 (StockTitan 재게재)](https://www.stocktitan.net/news/NTSK/netskope-to-report-fiscal-third-quarter-2027-financial-results-on-a24j9vajst29.html) · 공식 여부: 공식 보도자료 재게재 (본문 확인 못 함)
- 확신도: 확인 못 함

### Q-20261115-1934-4 · 보류 · A-20261115-1904-4 에 대해 — S(센티넬원) 12/4 07:00 새 일정
- 시각: 2026-11-15 19:45 KST
- 내용: 센티넬원 보도자료 재게재(FinancialContent)를 열지 못함. 웹 검색에는 FY26 3분기·FY27 2분기 일정 공지만 나옴. 발표일(미국 12/3 장 마감 후)·콜 시각(2:00 PM PT) 확인 못 함 → 추가 보류.
- 출처: [회사 보도자료 (FinancialContent 재게재)](https://www.financialcontent.com/article/bizwire-2026-11-12-sentinelone-announces-date-of-fiscal-third-quarter-2027-financial-results-conference-call-and-participation-in-upcoming-investor-conference) · 공식 여부: 공식 보도자료 재게재 (본문 확인 못 함)
- 확신도: 확인 못 함

### Q-20261115-2034-0 · 알림 · C-20261115-1949-2 에 대해 — 검색 결과 주소로 열기, 일부 성공
- 시각: 2026-11-15 20:55 KST
- 내용: Conrad 요청대로 먼저 웹 검색으로 같은 보도자료를 찾고 검색 결과에 나온 주소를 열었더니 8곳 중 6곳이 열렸어요(재게재 포함: stockhub.kr·earningswhispers·analog.com·finviz·investor.marvell.com PDF·snowflake.com). 열리지 않은 곳: corporate.walmart.com·stock.walmart.com·prnewswire.com·newsroom.cisco.com(PROVENANCE_REQUIRED). 원문을 연 7건(HD·PANW·ADI·AVGO·MRVL·CRWD·SNOW)은 반영, 나머지는 보류 유지. 시각 변환은 python(zoneinfo)으로 검산.
- 출처: 없음 (실행 방법 기록)
- 확신도: 높음

### Q-20261115-2034-1 · 반영 · A-20261115-1704-2 에 대해 — HD 11/17 23:00 콜 새 일정
- 시각: 2026-11-15 20:55 KST
- 내용: events.json 에 새 일정 추가: (없음) → 2026-11-17 "홈디포 실적 발표", when "23:00 콜 · 실적 자료 공개 시각 미공지", q "2026 회계연도 3분기". 원문: "Third Quarter Earnings Conference Call on Tuesday, November 17, at 9 a.m. ET"(11/3 PR Newswire 배포). 자료 공개 시각은 원문에 없어 적지 않음.
- 출처: [회사 보도자료 (Earnings Whispers 재게재)](https://www.earningswhispers.com/article/HD/2611036981) · 공식 여부: 공식 (회사 보도자료, 재게재 경로)
- 확신도: 높음

### Q-20261115-2034-2 · 반영 · A-20261115-1804-2 에 대해 — PANW 11/19 06:30 새 일정
- 시각: 2026-11-15 20:55 KST
- 내용: events.json 에 새 일정 추가: (없음) → 2026-11-19 "팔로알토네트웍스 실적 발표", when "06:30 웹캐스트 · 미국 장 마감 후", q "2027 회계연도 1분기 (8~10월)". 원문: "after U.S. markets close on Wednesday, November 18, 2026", "video webcast that day at 1:30 p.m. Pacific time (4:30 p.m. Eastern time)"(11/3 PR Newswire). money.json PANW 는 발표 뒤 갱신 대상.
- 출처: [회사 보도자료 (StockHub 재게재)](https://stockhub.kr/en/newswire/prn/302927448) · [PR Newswire 원문](https://www.prnewswire.com/news-releases/palo-alto-networks-to-announce-fiscal-first-quarter-2027-financial-results-on-wednesday-november-18-2026-302927448.html) · 공식 여부: 공식 (회사 보도자료)
- 확신도: 높음

### Q-20261115-2034-3 · 반영 · A-20261115-1504-4 에 대해 — ADI 11/24 21:00 새 일정
- 시각: 2026-11-15 20:55 KST
- 내용: events.json 에 새 일정 추가: (없음) → 2026-11-24 "아날로그디바이스 실적 발표", when "21:00 · 미국 장 시작 전 (콜 11/25 00:00)", q "2026 회계연도 4분기 (8~10월)". 원문: "release financial results ... at 7:00 a.m. Eastern time on Tuesday, November 24, 2026", "conference call at 10:00 a.m. Eastern time, the same day". 앞 차례 보류(Q-20261115-1534-4) 해소.
- 출처: [ADI 보도자료](https://www.analog.com/en/newsroom/press-releases/2026/10-22-2026-adi-report-4q-fy2026-financial-results.html) · 공식 여부: 공식
- 확신도: 높음

### Q-20261115-2034-4 · 반영 · A-20261115-1504-1 에 대해 — AVGO 12/12 → 12/10
- 시각: 2026-11-15 20:55 KST
- 내용: events.json AVGO: d 2026-12-12 → 2026-12-10, when "06:15 · 미국 장 마감 후 · 변동 가능성 보도" → "07:00 콜 · 미국 장 마감 후"(공식 확인으로 보도 표시 뗌). 원문: 12/9(수) "after the close of the U.S. trading session", "Time: 2:00 PM (PT); 5:00 PM (ET)"(11/9 PR Newswire). 자료 공개 시각은 원문에 없음.
- 출처: [회사 보도자료 (Finviz 재게재)](https://finviz.com/news/418980/broadcom-inc-to-announce-fourth-quarter-and-fiscal-year-2026-financial-results-on-wednesday-december-9-2026) · [브로드컴 IR 공지](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announce-fourth-quarter-and-fiscal-year-2026) · 공식 여부: 공식 (회사 보도자료)
- 확신도: 높음

### Q-20261115-2034-5 · 반영 · A-20261115-1504-2 에 대해 — MRVL 12/3 → 12/2
- 시각: 2026-11-15 20:55 KST
- 내용: events.json MRVL: d 2026-12-03 → 2026-12-02, when "06:05 · 미국 장 마감 후" → "06:30 콜 · 실적 자료는 콜 전 공개". 원문: "conference call following the release of its third quarter of fiscal year 2027 financial results", "on Tuesday, December 1, 2026, at 1:30 p.m. Pacific Time"(11/6 Business Wire). 자료 공개 시각·장 마감 후 여부는 원문에 없어 "콜 전 공개"로만 적음.
- 출처: [마벨 IR 보도자료 PDF](https://investor.marvell.com/_assets/_de258ecc084556935b61ff8ecc599288/marvell/news/2026-11-06_Marvell_Technology_Inc_Announces_Conference_Call_1041.pdf) · 공식 여부: 공식
- 확신도: 높음

### Q-20261115-2034-6 · 반영 · A-20261115-1804-4 에 대해 — CRWD 12/2 07:00 새 일정
- 시각: 2026-11-15 20:55 KST
- 내용: events.json 에 새 일정 추가: (없음) → 2026-12-02 "크라우드스트라이크 실적 발표", when "07:00 콜 · 미국 장 마감 후", q "2027 회계연도 3분기 (8~10월)". 원문: "after the U.S. market close on Tuesday, December 1, 2026", "at 2:00 p.m. Pacific time (5:00 p.m. Eastern time)"(11/4 Business Wire). 앞 차례 보류(Q-20261115-1834-4) 해소.
- 출처: [회사 보도자료 (Finviz 재게재)](https://finviz.com/news/415373/crowdstrike-announces-date-of-fiscal-third-quarter-2027-financial-results-conference-call) · [크라우드스트라이크 IR 공지](https://ir.crowdstrike.com/news-releases/news-release-details/crowdstrike-announces-date-fiscal-third-quarter-2027-financial) · 공식 여부: 공식 (회사 보도자료)
- 확신도: 높음

### Q-20261115-2034-7 · 반영 · A-20261115-1804-6 에 대해 — SNOW 12/3 07:00 새 일정
- 시각: 2026-11-15 20:55 KST
- 내용: events.json 에 새 일정 추가: (없음) → 2026-12-03 "스노우플레이크 실적 발표", when "07:00 콜 · 미국 장 마감 후", q "2027 회계연도 3분기 (8~10월)". 원문: "following the close of the U.S. markets on Wednesday, December 2, 2026", "conference call will begin at 2 p.m. Pacific Time on December 2, 2026"(11/2). 앞 차례 보류(Q-20261115-1834-6) 해소.
- 출처: [스노우플레이크 보도자료](https://www.snowflake.com/en/news/press-releases/fy27-q3-earnings-date-announcement/) · 공식 여부: 공식
- 확신도: 높음

### Q-20261115-2034-8 · 보류 · A-20261115-2004-1 에 대해 — MU 12/18 06:00 출처
- 시각: 2026-11-15 20:55 KST
- 내용: events.json MU 항목에는 출처 필드가 없고, 마이크론 회사 공지도 이번 차례에 찾지 못함(확인 못 함). 집계 사이트의 12/23(미국)은 "UNCONFIRMED" 추정이라 보도로도 보지 않음 → 날짜·표시 모두 그대로. 회사 공지가 나오면 반영.
- 출처: [Wall Street Horizon](https://www.wallstreethorizon.com/micron-earnings-calendar) · 공식 여부: 집계 사이트 추정 (확인 못 함)
- 확신도: 낮음

### Q-20261115-2034-9 · 보류 · 이번 차례에도 못 한 것 (앞 보류 그대로)
- 시각: 2026-11-15 20:55 KST
- 내용: WMT(A-1704-1) 월마트 페이지 열기 막힘 · DELL(A-1804-3) 검색에 이번 분기 공지가 안 나옴(작년 것만) · money.json CSCO(시스코 뉴스룸 막힘)·NOC(재게재 분석 기사만 열려 부문별 달러 숫자 없음 — 원문 확인 못 함)·MO(시도 못 함) · OKTA·RBRK·ZS·NTSK·S·CIEN·PL·COST·ASTS·FLY·SPCX 는 시간 안에 시도 못 함. 모두 앱 그대로, 다음 차례에 같은 방법(검색 결과 주소)으로 이어서 할게요.
- 출처: 없음
- 확신도: 높음
