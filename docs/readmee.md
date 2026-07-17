# Loyiha Yo'l Xaritasi — Milestonlar va Batafsil Vazifalar

Bu hujjat `README.md`da tavsiflangan arxitekturani **bajariladigan** bosqichlarga bo'ladi. Har bir milestone: aniq maqsad, backend/frontend/AI/devops vazifalari, **qanday qilish** bo'yicha texnik ko'rsatma, va "tugallandi" mezoni (Definition of Done) bilan beriladi.

**Tartib qat'iy:** Har bir milestone o'zidan oldingisiga bog'liq. Milestone tugamaguncha keyingisiga o'tmang — bu Clean Architecture'ning "pastdan yuqoriga qurish" tamoyiliga mos (domain → application → infrastructure → presentation).

---

## MILESTONE 0 — Fundament va Muhit (Taxminiy: 3-5 kun)

**Maqsad:** Kod yozishdan oldin, butun jamoa (yoki yolg'iz o'zingiz) bir xil muhitda ishlay oladigan asos qurish.

### Vazifalar

**Repo va struktura**
- [ ] Git repo yaratish, `main`/`develop` branch strategiyasi belgilash (masalan trunk-based yoki GitFlow — yolg'iz ishlasangiz oddiy `main` + feature branch yetarli)
- [ ] `README.md`dagi papka strukturasini jismonan yaratish (`src/domain`, `src/application`, `src/infrastructure`, `src/presentation`, `src/config`)
- [ ] `.gitignore`, `.env.example` fayllarini tayyorlash (haqiqiy `.env` hech qachon commit qilinmaydi)

**Docker muhiti**
- [ ] `docker-compose.yml` — quyidagi xizmatlar bilan:
  ```yaml
  services:
    postgres:
      image: postgres:16
      environment:
        POSTGRES_DB: discipline_db
      volumes:
        - pgdata:/var/lib/postgresql/data
    redis:
      image: redis:7-alpine
    api:
      build: .
      depends_on: [postgres, redis]
    worker:
      build: .
      command: celery -A src.infrastructure.scheduler.celery_app worker
    beat:
      build: .
      command: celery -A src.infrastructure.scheduler.celery_app beat
  ```
- [ ] `Dockerfile` — Python 3.12 slim asosida, `pip install --break-system-packages` yoki Poetry/uv orqali dependency boshqaruvi

**Sifat nazorati asboblari**
- [ ] `ruff` yoki `flake8` — linting
- [ ] `black` — formatting
- [ ] `mypy` — static type checking (Clean Architecture'da tip xavfsizligi muhim, chunki interfeys/portlar aniq bo'lishi kerak)
- [ ] `pytest` + `pytest-asyncio` — test freymvorki
- [ ] Pre-commit hook (`.pre-commit-config.yaml`) — har commit'da lint+format avtomatik ishga tushishi

**CI skeleton**
- [ ] GitHub Actions: `.github/workflows/ci.yml` — har push'da: lint → test → build (hozircha deploy yo'q, faqat tekshiruv)

### Definition of Done
`docker-compose up` buyrug'i xatosiz ishga tushadi, bo'sh FastAPI `/health` endpoint javob beradi, CI pipeline yashil.

---

## MILESTONE 1 — Domain Layer va Ma'lumotlar Bazasi (Taxminiy: 1 hafta)

**Maqsad:** Biznes logikaning "yuragi" — hech qanday tashqi bog'liqliksiz sof Python obyektlari.

### Vazifalar

**Domain Entities (`src/domain/entities/`)**
- [ ] `Goal`, `Plan`, `TaskTemplate`, `ScheduledTask`, `CheckIn`, `ScoreEvent` — har biri oddiy `dataclass` yoki Pydantic `BaseModel` (freymvorkka bog'lanmagan holda) sifatida
- [ ] Har bir entity uchun **invariant qoidalar** yozish (masalan: `TaskTemplate.tolerance_minutes` manfiy bo'lolmaydi) — bu qoidalar entity ichida validatsiya qilinadi, tashqarida emas

**Value Objects (`src/domain/value_objects/`)**
- [ ] `TimeWindow` — boshlanish/tugash vaqti, `contains(timestamp)` metodi bilan
- [ ] `ScoreFormula` — README 3-bo'limdagi formulani sof funksiya sifatida implement qilish, **birlik testlari bilan** (turli kechikish/erta holatlar uchun)

**Qanday qilish — TDD yondashuvi tavsiya etiladi:**
```python
# test_score_formula.py — avval test yoziladi
def test_on_time_gives_full_score():
    result = calculate_score(
        scheduled_time=t(14, 30), checkin_time=t(14, 32),
        tolerance_minutes=10, task_weight=1.0
    )
    assert result == 1.0

def test_late_beyond_tolerance_decays():
    result = calculate_score(
        scheduled_time=t(14, 30), checkin_time=t(16, 30),
        tolerance_minutes=10, task_weight=1.0
    )
    assert 0 < result < 0.5
```
Keyin shu testlarni o'tkazadigan funksiyani yozasiz. Bu formula nozik bo'lgani uchun (README 3.4-bo'lim) testlar birinchi himoya chizig'i.

**Ma'lumotlar bazasi**
- [ ] PostgreSQL jadvallarini README 5-bo'limdagi ER-diagrammaga mos SQLAlchemy modellari sifatida yozish (`src/infrastructure/db/models/`)
- [ ] Alembic sozlash: `alembic init migrations`, keyin `alembic revision --autogenerate -m "initial schema"`
- [ ] Indekslar qo'shish: `scheduled_task.scheduled_datetime`, `user.telegram_id` (tez-tez so'raladigan ustunlar)
- [ ] Repository interfeyslari (`src/application/interfaces/`) — masalan `IGoalRepository` (abstract), keyin `src/infrastructure/db/repositories/` da PostgreSQL implementatsiyasi

### Definition of Done
Barcha domain testlar o'tadi (`pytest src/domain -v`), migratsiyalar toza bazada muvaffaqiyatli ishlaydi, repository orqali oddiy CRUD operatsiyalar test qilingan.

---

## MILESTONE 2 — Backend Core API (Taxminiy: 1.5-2 hafta)

**Maqsad:** Foydalanuvchi, maqsad, reja va vazifalarni boshqaradigan to'liq ishlaydigan REST API.

### Vazifalar

**Auth**
- [ ] JWT-based autentifikatsiya: Telegram orqali ro'yxatdan o'tish (`telegram_id` asosida), token generatsiya
- [ ] `src/presentation/api/dependencies.py` — `get_current_user` dependency, har himoyalangan endpoint'da ishlatiladi

**Use Case'lar (`src/application/use_cases/`)**
- [ ] `CreateGoalUseCase` — foydalanuvchi maqsad kiritganda
- [ ] `CreatePlanManuallyUseCase` — foydalanuvchi o'zi reja tuzsa
- [ ] `AddTaskTemplateUseCase`
- [ ] `ProcessCheckInUseCase` — bu eng muhimi: check-in kelganda Precision Engine chaqiriladi, `ScoreEvent` yaratiladi

**Qanday qilish — Use Case naqshi:**
```python
class ProcessCheckInUseCase:
    def __init__(self, task_repo: ITaskRepository, score_repo: IScoreRepository):
        self._task_repo = task_repo
        self._score_repo = score_repo

    async def execute(self, scheduled_task_id: UUID, checkin_time: datetime) -> ScoreEvent:
        task = await self._task_repo.get(scheduled_task_id)
        if task.status != "pending":
            raise AlreadyCheckedInError()  # idempotency himoyasi

        score = calculate_score(task.scheduled_datetime, checkin_time,
                                  task.tolerance_minutes, task.weight)
        event = ScoreEvent.create(task.id, score)
        await self._score_repo.save(event)
        return event
```
Bu qatlam FastAPI'ni bilmaydi — uni istalgan interfeys (bot, web, CLI) chaqira oladi.

**API Endpoints (`src/presentation/api/v1/`)**
- [ ] `POST /goals`, `GET /goals/{id}`
- [ ] `POST /goals/{id}/plans`
- [ ] `POST /plans/{id}/task-templates`
- [ ] `POST /checkins`
- [ ] `GET /users/{id}/progress`

**Testlar**
- [ ] Har bir use case uchun unit test (repository'lar mock qilingan holda)
- [ ] Integration testlar — haqiqiy test bazasi bilan (Docker orqali test uchun alohida Postgres konteyner)

### Definition of Done
Swagger/OpenAPI hujjatlari (`/docs`) to'liq ishlaydi, Postman/curl orqali to'liq oqim sinovdan o'tkaziladi: goal yaratish → reja qo'shish → check-in yuborish → score olish.

---

## MILESTONE 3 — Telegram Bot Integratsiyasi (Taxminiy: 1 hafta)

**Maqsad:** Foydalanuvchining asosiy interfeysi — bot orqali to'liq muloqot.

### Vazifalar

- [ ] `aiogram` bilan bot skeleton (`src/infrastructure/telegram/bot.py`)
- [ ] `/start` — ro'yxatdan o'tish, backend API bilan bog'lanish (bot alohida process, lekin FastAPI'ga HTTP orqali murojaat qiladi — yoki to'g'ridan-to'g'ri use case'larni chaqiradi, agar bir monolit ichida bo'lsa)
- [ ] Maqsad qo'shish suhbat oqimi (FSM — Finite State Machine, aiogram'ning `FSMContext` orqali)
- [ ] Check-in tugmalari (Inline Keyboard) — notification kelganda "Bajardim" tugmasi
- [ ] Progress so'rovi — `/progress` buyrug'i

**Qanday qilish — FSM misoli:**
```python
class GoalCreationStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_target_date = State()
    waiting_for_plan_choice = State()  # o'zi tuzadimi yoki AI tuzsinmi

@router.message(Command("newgoal"))
async def start_goal_creation(message: Message, state: FSMContext):
    await state.set_state(GoalCreationStates.waiting_for_title)
    await message.answer("Maqsadingiz nima?")
```

- [ ] Webhook yoki polling tanlash (production'da webhook tavsiya etiladi — Nginx orqali)

### Definition of Done
Foydalanuvchi botda to'liq oqimni real vaqtda bajara oladi: ro'yxatdan o'tish → maqsad qo'shish → check-in qilish → progress ko'rish.

---

## MILESTONE 4 — Scheduler, Notification va Precision Engine Ulash (Taxminiy: 1-1.5 hafta)

**Maqsad:** Tizimning "jonlanishi" — vaqt bo'yicha avtomatik ishlaydigan qism.

### Vazifalar

- [ ] Celery + Celery Beat sozlash (`src/infrastructure/scheduler/celery_app.py`)
- [ ] Kunlik `generate_scheduled_tasks` job — har `TaskTemplate.recurrence_rule` (RRULE) asosida ertangi kun uchun `ScheduledTask` yaratadi
- [ ] `send_notifications` job — har daqiqada ishga tushadi, `scheduled_datetime` yaqinlashgan vazifalar uchun Telegram orqali xabar yuboradi
- [ ] **Idempotency** — bir xil notification ikki marta yuborilmasligi uchun `notification_sent_at` tekshiriladi (README 8.3-bo'lim)
- [ ] **Retry mexanizmi** — Celery'ning `autoretry_for` va `retry_backoff` parametrlari orqali, Telegram API vaqtincha ishlamasa

**Qanday qilish — RRULE parsing:**
```python
from dateutil.rrule import rrulestr

def generate_next_occurrences(recurrence_rule: str, dtstart: datetime, count: int = 1):
    rule = rrulestr(recurrence_rule, dtstart=dtstart)
    return list(rule)[:count]
```

- [ ] Kechikkan check-in bo'lmagan (foydalanuvchi umuman javob bermagan) holatlarni "missed" deb belgilaydigan job — masalan `scheduled_datetime`dan 3 soat o'tsa, avtomatik `ScoreEvent(score=0)` yaratiladi

### Definition of Done
Test rejasi tuzilib, botga real vaqtda notification keladi, check-in qilinganda yoki qilinmaganda to'g'ri score hisoblanadi, server qayta ishga tushirilsa ham (restart) hech qanday notification takrorlanmaydi yoki yo'qolmaydi.

---

## MILESTONE 5 — LLM Integratsiyasi: Reja va Tahlil (Taxminiy: 1.5-2 hafta)

**Maqsad:** Tizimning "aql" qismi — AI orqali reja tuzish va naqsh topish.

### Vazifalar

**LLM Provider abstraktsiyasi**
- [ ] `ILLMProvider` interfeysi (`src/application/interfaces/`) — `generate_plan()`, `analyze_progress()` metodlari bilan
- [ ] `ClaudeProvider` va `OllamaProvider` implementatsiyalari (README'da ta'kidlanganidek — narx/lokal balansi uchun ikkalasi ham)

**Reja generatsiyasi**
- [ ] Suhbat orqali ma'lumot yig'ish (bot FSM orqali): maqsad, joriy daraja, mavjud vaqt, muddat
- [ ] Prompt tuzish — **structured output** talab qilish (JSON formatida qaytarish, README'dagi "structured_outputs_in_xml" texnikasiga o'xshash — lekin JSON'da):
  ```
  Faqat quyidagi JSON formatda javob ber, boshqa hech narsa yozma:
  {
    "tasks": [
      {"title": "...", "recurrence": "FREQ=DAILY", "time": "HH:MM", "weight": 0.0-1.0}
    ]
  }
  ```
- [ ] LLM javobini validatsiya qilish (Pydantic orqali parse, xato bo'lsa qayta so'rash logikasi)
- [ ] Foydalanuvchiga taklif qilingan rejani ko'rsatish va tasdiqlash/tahrirlash imkoniyati (AI hech qachon so'zsiz avtomatik qo'llanilmasligi kerak)

**Haftalik Insight generatsiyasi**
- [ ] Celery Beat job — har yakshanba, foydalanuvchining haftalik `ScoreEvent` va `CheckIn` tarixini yig'ib, LLM'ga tahlil uchun yuboradi
- [ ] Prompt: "Qaysi kunlar/vazifalar eng ko'p muvaffaqiyatsiz bo'lgan, nima uchun bo'lishi mumkinligini taxmin qil, foydalanuvchiga bitta aniq savol ber"
- [ ] Natija `Insight` jadvaliga saqlanadi va bot orqali yuboriladi

**Xarajat nazorati**
- [ ] Har bir LLM chaqiruvi log qilinadi (token soni, narx) — README 10-bo'limdagi ochiq savolga javob topish uchun ma'lumot yig'ish

### Definition of Done
Foydalanuvchi botda "bilmayman" deb javob bersa, AI mantiqiy reja taklif qiladi; hafta oxirida kamida bitta ma'noli insight generatsiya qilinadi va yetkaziladi.

---

## MILESTONE 6 — Web Dashboard (Taxminiy: 1.5-2 hafta)

**Maqsad:** Vizual ko'rinish va batafsil sozlamalar uchun qo'shimcha interfeys (bot asosiy bo'lib qoladi).

### Vazifalar

**Frontend Setup**
- [ ] React + Vite loyihasi, Tailwind CSS sozlash
- [ ] `frontend-design` skill'iga murojaat qilib, vizual yo'nalish tanlash (shablon ko'rinishdan qochish)
- [ ] Auth — Telegram Login Widget yoki bot orqali generatsiya qilingan bir martalik token bilan kirish

**Sahifalar**
- [ ] Dashboard — joriy progress, umumiy ball, haftalik grafik (Recharts)
- [ ] Goals sahifasi — barcha maqsadlar, har birining progress holati
- [ ] Plan tahrirlash — TaskTemplate'larni qo'lda o'zgartirish (vaqt, tolerantlik, og'irlik)
- [ ] Insights tarixi — LLM tomonidan topilgan barcha naqshlar ro'yxati
- [ ] Sozlamalar — timezone, notification tercihlari

**API integratsiyasi**
- [ ] `src/presentation/api/v1/` ga dashboard uchun qo'shimcha endpoint'lar (`GET /progress/weekly-chart-data` kabi, frontend uchun tayyor formatlangan ma'lumot)

### Definition of Done
Foydalanuvchi web orqali kirib, o'z progressini vizual ko'radi va rejasini tahrirlay oladi.

---

## MILESTONE 7 — DevOps Qattiqlashtirish va Observability (Taxminiy: 1-1.5 hafta)

**Maqsad:** Tizimni ishonchli qilish — README 8-bo'limdagi non-functional talablarni amalga oshirish.

### Vazifalar

**Monitoring**
- [ ] Prometheus + Grafana — Docker Compose'ga qo'shish
- [ ] Metrikalar: notification yuborilish muvaffaqiyat foizi, LLM chaqiruv vaqti/narxi, API response time, Celery queue uzunligi
- [ ] Alerting (masalan Grafana Alerting yoki oddiy Telegram xabar) — agar notification yuborish 5 daqiqadan ortiq kechiksa

**Logging**
- [ ] Strukturaviy logging (`structlog` yoki oddiy JSON formatter) — har bir log yozuvida `user_id`, `request_id` bo'lishi kerak (traceability uchun)
- [ ] Log aggregatsiyasi (kichik miqyosda — oddiy fayl + `docker logs`; kattaroq bo'lsa Loki)

**Backup va Disaster Recovery**
- [ ] PostgreSQL avtomatik backup (kunlik `pg_dump`, alohida saqlash joyiga — masalan S3-compatible storage)
- [ ] Backup'dan tiklashni **sinab ko'rish** (backup borligi kifoya emas, uni tiklab ko'rish shart)

**Xavfsizlik**
- [ ] Nginx reverse proxy + Let's Encrypt SSL
- [ ] Rate limiting (Redis orqali, IP va user darajasida)
- [ ] Sensitive ma'lumotlarni (Goal description, notes) encryption at rest — masalan `pgcrypto` yoki application-level encryption

**Load testing**
- [ ] `locust` yoki `k6` orqali API'ga yuklama testi — necha foydalanuvchi bir vaqtda check-in qilganda tizim qanday ishlashini tekshirish

### Definition of Done
Grafana dashboard'da real vaqt metrikalar ko'rinadi, backup tiklash test qilingan va ishlaydi, load test natijalari hujjatlashtirilgan.

---

## MILESTONE 8 — SaaS'ga Tayyorlash: Multi-tenancy va To'lov (Taxminiy: 2 hafta)

**Maqsad:** Bitta foydalanuvchi uchun ishlagan tizimni minglab foydalanuvchi uchun xavfsiz qilish.

### Vazifalar

- [ ] Multi-tenant xavfsizlik audit — har bir so'rovda `user_id` filtrlanganini tekshirish (boshqa foydalanuvchi ma'lumotiga kirish mumkin emasligini avtomatik test bilan tasdiqlash)
- [ ] To'lov integratsiyasi (Payme/Click) — obuna modeli (Free tier + Pro tier)
- [ ] Onboarding oqimi — birinchi marta kirgan foydalanuvchi uchun qadamma-qadam yo'riqnoma (bot ichida)
- [ ] Admin panel — Precision Engine formula parametrlarini (`DECAY_CONST`, bonus koeffitsientlari) kod o'zgartirmasdan sozlash imkoniyati (README 3.4-bo'limdagi tavsiya)
- [ ] Foydalanuvchi limitlar — Free tier uchun maqsadlar/vazifalar soni cheklovi

### Definition of Done
Yangi foydalanuvchi ro'yxatdan o'tib, to'lov qilib, Pro tier'ga o'tishi to'liq avtomatik ishlaydi; admin panel orqali formula sozlanganda darhol ta'sir qiladi.

---

## MILESTONE 9 — Marketing va Ishga Tushirish (Taxminiy: 1-2 hafta)

**Maqsad:** Siz aytganingizdek — mahsulot qattiq/og'riqli ekanligini bila turib, odamlar o'zi xohlab kiradigan pozitsionerlash.

### Vazifalar

- [ ] Landing page (oddiy HTML/React, mahsulotning "qattiqligi"ni to'g'ridan-to'g'ri aytadigan messaging bilan)
- [ ] Beta test guruhi (10-20 kishi) — real foydalanuvchi ma'lumotlarini yig'ish, ayniqsa Precision Engine formulasini sozlash uchun (README 10-bo'limdagi ochiq savol)
- [ ] Referral/invite mexanizmi
- [ ] Feedback yig'ish kanali (bot ichida `/feedback` buyrug'i)

### Definition of Done
Beta guruh 2 hafta davomida tizimni ishlatadi, formula parametrlari real ma'lumot asosida sozlanadi, keyingi ochiq chiqarish (public launch) uchun tayyor.

---

## Umumiy Vaqt Jadvali

| Milestone | Taxminiy davomiylik | Kümulativ |
|---|---|---|
| M0 — Fundament | 3-5 kun | ~1 hafta |
| M1 — Domain & DB | 1 hafta | ~2 hafta |
| M2 — Backend Core | 1.5-2 hafta | ~4 hafta |
| M3 — Telegram Bot | 1 hafta | ~5 hafta |
| M4 — Scheduler & Notification | 1-1.5 hafta | ~6.5 hafta |
| M5 — LLM Integratsiya | 1.5-2 hafta | ~8.5 hafta |
| M6 — Web Dashboard | 1.5-2 hafta | ~10.5 hafta |
| M7 — DevOps Qattiqlashtirish | 1-1.5 hafta | ~12 hafta |
| M8 — SaaS Tayyorlash | 2 hafta | ~14 hafta |
| M9 — Marketing/Launch | 1-2 hafta | ~16 hafta |

**Eslatma:** Bu — yolg'iz, to'liq band bo'lmagan holda ishlaydigan developer uchun realistik taxmin (~3.5-4 oy). Agar kuniga 2-3 soat ajratilsa, bu muddat 1.5-2 barobar cho'zilishi mumkin — bu me'yoriy holat, muhimi izchillik.

---

*Har bir milestone tugagach, shu hujjatga qaytib, haqiqiy sarflangan vaqt va duch kelingan muammolarni qayd etish tavsiya etiladi — bu keyingi loyihalar uchun kalibrlash imkonini beradi.*