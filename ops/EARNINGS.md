# 실적 카드 고치는 법 (Tally)

회사 화면 맨 위 「실적」 카드의 원본은 `data/earnings.json` 이에요. `index.html` 은 `python3 scripts/check_data.py --embed` 로만 바뀌어요.

## 카드 한 곳의 모양
- `p`: 기간 (예: "3분기 · 2026년 7~9월", 회계연도가 다르면 "2분기 · 2026년 7~9월")
- `tag`: 1년 전보다 매출 증감 (예: "+17%", 모르면 "—")
- `rows`: [이름, 값] 3~4줄 (매출, 핵심 부문, 이익, 전망 등)
- `note`: 1~2문장. 무엇이 이끌었는지 + 주의할 점. **계산한 값(성장률로 거꾸로 구한 1년 전 매출 등)은 반드시 여기 밝혀요.**
- `src`: [이름, 링크] 2~3개. 회사 발표·SEC 공시를 먼저, 예상치 출처를 함께.
- `chart` (금액은 **백만 단위**, `cur` 는 usd·eur·cad·krw·twd·cny 중 하나)
  - `now`: [기간 이름, 이번 매출] · `prev`: ["1년 전", 매출] (모르면 빼요)
  - `est`: 발표 **전** 애널리스트 매출 예상 (모르면 null — 지어내지 않아요)
  - `next`: `label`(다음 분기 이름), `guide`([낮은, 높은] 회사 분기 전망 또는 null), `cons`(다음 분기 애널리스트 예상 또는 null), `asof`("11/3" 처럼 기준일), `when`("2027년 2월 초 (예상)"), `gtext`(분기 전망이 없고 연간 전망만 있을 때 한 줄)
  - `metric`: 매출이 아닌 다른 숫자를 그릴 때만 (예: "소프트웨어 매출")

## 출처 규칙
- 실적 숫자는 회사 발표·SEC 공시가 기준. 언론 정리는 회사 발표와 맞을 때만.
- 애널리스트 예상은 공식이 아니에요. 출처마다 다르면 하나를 고르고 `note` 에 범위를 적어요.
- 확인 못 한 숫자는 넣지 않아요. 매수·매도 표현은 쓰지 않아요.

## 순서
1. `git pull --rebase`
2. `scripts/earnings_card.py` 의 `card()` 로 고치고 `save()`
3. `python3 scripts/check_data.py --embed` 통과
4. `data/earnings.json`, `index.html`, `ops/board/tally.md` 를 한 커밋: `실적 카드: <회사들> (출처: <대표 URL>)`
5. `git pull --rebase` 후 다시 `check_data.py` 확인, push (충돌 시 최대 3번)
