# SakhiCare Quality Report

Updated 2026-10-01 after repository inspection and checks in this workspace.

## 1. Code Quality

- **PARTIAL.** Frontend production build passes; `npm run build` runs `tsc -b` and Vite. This checks TypeScript compilation but does not establish strict TypeScript settings or lint cleanliness.
- **PARTIAL.** FastAPI/Pydantic code separates speech, session, rules, and route concerns (`backend/app/services/speech.py`, `backend/app/session_store.py`, `backend/app/rules/`). No backend type checker or linter is configured.
- **Change:** Home screen now exposes “Talk with Sakhi” directly. This fixes an unreachable feature: the existing automated test expected a home-screen entry, but the header previously hid it on the home screen.
- **Change:** Fixed brittle guide test selectors that matched duplicate Skip/Next controls and stale product copy. These changes make the intended guide, handoff, and chat journeys testable.

## 2. Efficiency

- **PARTIAL.** Production frontend bundle from the successful build: 335.95 kB JavaScript (103.10 kB gzip), 43.36 kB CSS (10.74 kB gzip). MediaPipe is statically imported in `src/App.tsx`, so gesture code contributes to the initial JavaScript bundle; it is not lazy-loaded.
- Speech model is loaded lazily and cached once by `_whisper_model()` in `backend/app/services/speech.py` (`lru_cache(maxsize=1)`). Camera frames are processed locally; camera tracks and the landmarker are released by the flow effect cleanup in `src/App.tsx`.
- No runtime performance profile, memory profile, or Core Web Vitals measurement was run.

## 3. Accessibility

- **PARTIAL.** Existing implementation includes semantic native buttons/links, a first-visit Follow Me dialog with real DOM targets, Skip/Replay, keyboard focus styling, reduced-motion CSS, localized English/Tamil flow copy, and touch alternatives to camera gestures (`src/components/Walkthrough.tsx`, `src/styles.css`).
- **PASS (focused regression coverage only).** Frontend UI tests include first-visit guide/skip, replay, question flow, touch fallback, help, camera/microphone unsupported fallbacks, document coach, and confirmed official portal handoff.
- No axe/WCAG automated scan, screen-reader review, contrast measurement, or human assistive-technology test was run. WCAG 2.2 AA conformance is not established.

## 4. Security

- **PARTIAL.** API keys are read server-side from environment variables; `.env` is ignored. Upload routes have content-type and size checks; user text/history are bounded in the backend; external navigation uses fixed government URLs and `noopener,noreferrer`. Camera frames are not sent to the backend. Raw audio is bounded and processed in memory by `/api/voice/chat`.
- **PASS (production frontend dependency audit only).** `npm audit --omit=dev` reported 0 vulnerabilities on 2026-10-01. This excludes development dependencies and does not cover Python packages.
- No Python dependency audit, penetration test, prompt-injection exercise, CORS deployment review, or secret scan was run. CORS currently allows the local Vite origins in `backend/app/main.py`; deployment origins need configuration/review.

## 5. Testing

- Baseline: frontend tests **FAIL (12/12)** due to ambiguous “Skip guide” selector in a shared helper. Backend tests from repository root **FAIL to collect** because tests import `app` and expect the `backend` directory as working directory. Frontend build **PASS**.
- After fixes: frontend **12 passed** (`cd frontend; npm test -- --reporter=dot`); backend **14 passed, 1 Starlette/httpx deprecation warning** (`cd backend; python -m pytest -q`); production build and TypeScript compile **PASS**; frontend production dependency audit **0 vulnerabilities**.
- **Change:** Added root `verify.ps1`, which runs the frontend tests/build/audit and backend tests from their expected working directories.
- No browser automation, browser console inspection, real device checks, permissions-denial tests, or smoke run against live services was performed.

## 6. Problem Statement Alignment

- **PARTIAL.** The MVP supports one scheme (PMMVY), one-question-at-a-time touch answers, a visual tutorial, voice transcription with automatic detected-language metadata, local visual gestures, a document checklist, and explicit confirmed handoff to the official portal. It does not submit forms or claim official eligibility.
- The primary flow and static interface support English and Tamil. The voice transcription provider is OpenAI `gpt-transcribe` when configured (`ASR_PROVIDER=auto` and `OPENAI_API_KEY`), otherwise local `faster-whisper` multilingual `small` by default. Backend fallback language responses exist for `en`, `hi`, `ta`, `te`, `bn`, `kn`, `ml`, `mr`, `gu`, `pa`; actual generated reply/audio depends on configured AI credentials, model support, and device voices. This is not evidence of end-to-end verified support for all those languages.
- Gesture vocabulary is browser MediaPipe hand-landmark heuristics for yes/no/next/back/help. It is visual navigation only, not Indian Sign Language translation.
- The guided voice flow only advances for a recognized yes/no intent; unsupported/uncertain language can still show detected transcript/reply or a retry/fallback, but question-to-answer intent support is narrower than transcription support.

## 7. Browser Testing

- **NOT TESTED.** No browser automation session was available or run. Automated React tests use jsdom and cannot verify layout or camera/microphone permissions in a real browser.
- Viewport widths 320, 360, 390, 414, 768, 1024, 1280, and 1440+ were not visually inspected. No Lighthouse score is claimed.

## 8. Remaining Gaps

- No auth/login exists in this MVP; “first visit” is browser-local onboarding, not first authenticated login.
- Only English/Tamil UI copy is provided; the language picker toggles those two. More voice transcription language codes do not imply translated interface, tested reply language, or synthesized speech coverage.
- Gesture handling and fallback states need real-device camera-denial/unavailable and repeated-trigger validation.
- The 3-question MVP is not sufficient to determine PMMVY eligibility. Results are expressly guidance only; current rules and documents need confirmation at the official portal or with an Anganwadi worker.
- Automated accessibility scan, backend security/dependency scan, production deployment review, and responsive browser inspection remain unverified.
