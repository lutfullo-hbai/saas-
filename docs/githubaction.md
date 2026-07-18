# Professional GitHub Workflow — Qo'llanma (Inson va AI Agentlar uchun)

> Bu hujjat ikki auditoriya uchun yozilgan: (1) **siz** — professional Git/GitHub odatlarini o'rganish uchun, (2) **AI agentlar** (Claude Code va h.k.) — shu repo ustida ishlaganda qat'iy rioya qilishi kerak bo'lgan qoidalar to'plami sifatida. Shuning uchun ba'zi qismlar "qoida" shaklida, imperativ tarzda yozilgan — bu tasodif emas.

---

## 1. Nega bu muhim — professional va havaskor farqi

Havaskor development va professional development orasidagi eng katta farq kod sifatida emas, balki **jarayonda** ko'rinadi:

| Havaskor | Professional |
|---|---|
| `main`ga to'g'ridan-to'g'ri push | Har o'zgarish branch + Pull Request orqali |
| "fix", "update", "asd" commit xabarlari | Aniq, standartlashgan commit xabarlari |
| Kod review qilinmaydi | Har PR kamida bitta review'dan o'tadi |
| Test yo'q yoki qo'lda tekshiriladi | CI avtomatik test/lint/build qiladi |
| Bug qachon paydo bo'lganini bilib bo'lmaydi | Git tarixi orqali aniq kuzatiladi (`git bisect`, aniq commit'lar) |
| Hujjat yo'q yoki eskirgan | README, CONTRIBUTING, CHANGELOG doim yangilanadi |

Bu qo'llanma sizni chapdan o'ngga o'tkazish uchun.

---

## 2. Commit Xabarlari — Conventional Commits Standarti

Professional loyihalarning deyarli barchasi **Conventional Commits** formatidan foydalanadi:

```
<type>(<scope>): <qisqa tavsif>

<batafsil tavsif — ixtiyoriy>

<footer — ixtiyoriy, masalan BREAKING CHANGE yoki Closes #12>
```

### Type'lar

| Type | Qachon ishlatiladi |
|---|---|
| `feat` | Yangi funksiya qo'shilganda |
| `fix` | Bug tuzatilganda |
| `refactor` | Xatti-harakat o'zgarmasdan kod tuzilishi yaxshilanganda |
| `docs` | Faqat hujjat o'zgarganda |
| `test` | Test qo'shilganda/o'zgartirilganda |
| `chore` | Dependency yangilash, config o'zgarishi — foydalanuvchiga ta'sir qilmaydigan ishlar |
| `perf` | Ishlash tezligini yaxshilash |
| `ci` | CI/CD konfiguratsiyasi o'zgarishi |

### Misollar

```
feat(checkin): add idempotency check for duplicate check-ins

fix(scheduler): correct timezone conversion for notification timing

Bug DST (yozgi vaqt) o'zgarishida notification 1 soat noto'g'ri
vaqtda yuborilishiga sabab bo'layotgan edi. UTC saqlash va faqat
ko'rsatishda konvertatsiya qilish tarziga o'tkazildi.

Closes #47
```

```
refactor(domain): extract ScoreFormula into separate value object
```

**Nima uchun bu muhim:** Yaxshi commit tarixi — bu loyihaning "xotirasi". 6 oydan keyin "nega bu kod shunday yozilgan" degan savolga javob commit tarixida topiladi, odamning xotirasida emas.

### AI Agentlar uchun qoida
> Agent hech qachon `"update"`, `"fix stuff"`, `"changes"` kabi ma'nosiz commit xabarlarini yozmaydi. Har commit yuqoridagi formatga qat'iy rioya qiladi. Agar bir commit ichida bir nechta mantiqiy o'zgarish bo'lsa, agent ularni **alohida commit'larga bo'lishi** kerak (`git add -p` orqali qisman stage qilish).

---

## 3. Branching Strategiya

Kichik jamoa/yolg'iz developer uchun eng mos yondashuv — **Trunk-Based Development (soddalashtirilgan)**:

```
main (doim deploy qilinadigan holatda, "yashil")
 └── feature/goal-creation-flow
 └── fix/timezone-bug-in-scheduler
 └── refactor/extract-score-formula
```

### Qoidalar

1. **`main` branch har doim ishlaydigan holatda bo'lishi kerak** — hech qachon to'g'ridan-to'g'ri commit qilinmaydi
2. Har yangi ish uchun **yangi branch** ochiladi, nomlash konventsiyasi:
   - `feature/<qisqa-tavsif>` — yangi funksiya
   - `fix/<qisqa-tavsif>` — bug tuzatish
   - `refactor/<qisqa-tavsif>` — kod tozalash
   - `chore/<qisqa-tavsif>` — yordamchi ishlar
3. Branch **kichik va tez tugaydigan** bo'lishi kerak (1-3 kun ichida PR ochiladigan) — uzoq yashovchi branch'lar merge conflict va integratsiya og'rig'ini keltirib chiqaradi
4. Merge qilingandan keyin branch **o'chiriladi** (repo'ni toza saqlash uchun)

Katta jamoa/murakkab release siklida **GitFlow** (`main` + `develop` + `release/*` + `hotfix/*`) ishlatiladi, lekin bu loyiha hajmi uchun ortiqcha murakkablik — trunk-based yetarli.

### AI Agentlar uchun qoida
> Agent hech qachon `main` branch'ga to'g'ridan-to'g'ri commit qilmaydi yoki push qilmaydi, hatto kichik o'zgarish bo'lsa ham. Har vazifa boshida agent yangi branch yaratadi (`git checkout -b feature/...`), ish tugagach Pull Request oqimi orqali taklif qiladi. Agent `git push --force` ni faqat o'zining shaxsiy feature branch'ida, va faqat aniq sabab bilan (masalan rebase qilingandan keyin) ishlatadi — **hech qachon `main`da force push qilmaydi**.

---

## 4. Pull Request (PR) — Professional Jarayon

PR — shunchaki "kodni ulash" emas, balki **muloqot vositasi**.

### Yaxshi PR quyidagilarga ega:

1. **Aniq sarlavha** — commit konventsiyasiga mos (`feat: add weekly insight generation`)
2. **Tavsif** — nima o'zgardi, nega, qanday test qilindi:
   ```markdown
   ## Nima o'zgardi
   Haftalik Insight generatsiyasi uchun Celery job qo'shildi.

   ## Nega
   README M5 milestone talabi — foydalanuvchi progress naqshlarini
   avtomatik tahlil qilish kerak.

   ## Qanday test qilindi
   - Unit test: `test_weekly_insight_generation.py`
   - Qo'lda tekshirildi: local muhitda 2 haftalik fake data bilan

   ## Screenshot / Misol (agar UI o'zgargan bo'lsa)
   ...

   Closes #23
   ```
3. **Kichik hajm** — ideal holda 200-400 qatordan kam o'zgarish. Katta PR review qilishni qiyinlashtiradi va sifatni pasaytiradi
4. **CI yashil** — barcha avtomatik testlar o'tgan bo'lishi shart, review so'ralishidan oldin

### PR Template (`.github/pull_request_template.md`)

```markdown
## Nima o'zgardi


## Nega


## Qanday test qilindi


## Checklist
- [ ] Testlar yozilgan/yangilangan
- [ ] Lokal muhitda ishga tushirib ko'rildi
- [ ] Hujjat (agar kerak bo'lsa) yangilangan
- [ ] Breaking change yo'q (yoki pastda ta'kidlangan)
```

### AI Agentlar uchun qoida
> Agent PR ochganda yuqoridagi shablonga to'liq rioya qiladi. Agent hech qachon "review qilindi" deb o'zini o'zi belgilamaydi — bu inson (yoki belgilangan reviewer) vazifasi. Agent PR tavsifida qilingan har bir muhim arxitektura qarorini tushuntiradi (masalan "nega bu formula shunday yozildi"), chunki reviewer kontekstni bilmasligi mumkin.

---

## 5. Code Review — Qanday Review Qilish va Qabul Qilish

### Review qilayotganda (agar jamoada ishlasangiz)

- **Kodni emas, muammoni tanqid qiling** — "Bu funksiya juda uzun, chunki..." emas, "Bu yerda bo'lishi mumkin bo'lgan muammo..."
- Har izoh uchun **daraja** ko'rsating: `nit:` (kichik, ixtiyoriy), `blocking:` (albatta tuzatilishi kerak), `question:` (tushunmadim, tushuntiring)
- Yaxshi ishni ham qayd eting — faqat salbiy izoh emas

### Review qabul qilayotganda

- Har bir izohga javob bering (hatto rozi bo'lmasangiz ham — "Nega bu tarzda qildim..." deb tushuntiring)
- Himoyaga o'tmang — review shaxsga emas, kodga qaratilgan

### Branch Protection Rules (GitHub sozlamalari)

`Settings → Branches → Branch protection rules` orqali `main` uchun:
- [ ] "Require a pull request before merging" — yoqilgan
- [ ] "Require approvals" — kamida 1 ta (yolg'iz ishlasangiz ham, o'zingizga PR yozib, keyin merge qilish odatiy amaliyot — bu sizni sekinlashtirib, xatoni oldindan ko'rish imkonini beradi)
- [ ] "Require status checks to pass before merging" — CI (lint, test) majburiy
- [ ] "Do not allow bypassing the above settings" — hatto repo egasi ham qoidani buzolmaydi

### AI Agentlar uchun qoida
> Agent branch protection qoidalarini hech qachon o'chirish yoki chetlab o'tishga urinmaydi, hatto texnik jihatdan iloji bo'lsa ham. Agar CI muvaffaqiyatsiz bo'lsa, agent muammoni albatta tuzatadi — "CI'ni skip qilish" yoki "keyinroq tuzataman" degan yondashuvni qabul qilmaydi.

---

## 6. Issue Tracking va Loyiha Boshqaruvi

### Issue turlari (Labels)

| Label | Ma'no |
|---|---|
| `bug` | Nosozlik |
| `enhancement` | Yangi funksiya so'rovi |
| `documentation` | Hujjat bilan bog'liq |
| `good first issue` | Yangi qo'shilganlar uchun oson vazifa |
| `priority: high/medium/low` | Muhimlik darajasi |
| `blocked` | Boshqa ishga bog'liq, hozircha to'xtatilgan |

### Issue Template (`.github/ISSUE_TEMPLATE/bug_report.md`)

```markdown
## Muammo tavsifi


## Qayta hosil qilish qadamlari
1.
2.

## Kutilgan xatti-harakat


## Haqiqiy xatti-harakat


## Muhit (versiya, OS, va h.k.)
```

### GitHub Projects (Kanban board)

Milestone'larni GitHub Projects orqali vizualizatsiya qilish tavsiya etiladi: `To Do → In Progress → In Review → Done` ustunlari, har bir vazifa alohida Issue sifatida, Milestone'larga (`M0`, `M1`, ...) bog'langan holda.

### AI Agentlar uchun qoida
> Agent katta vazifani boshlashdan oldin, agar tegishli Issue mavjud bo'lmasa, avval Issue yaratadi (yoki foydalanuvchidan Issue raqamini so'raydi) — bu ishning "nima uchun" qilinayotganini kelajakda kuzatib borish imkonini beradi. Har commit/PR tegishli Issue raqamiga (`Closes #12`, `Refs #12`) havola qiladi.

---

## 7. Semantic Versioning va Release Jarayoni

Versiya raqamlash: `MAJOR.MINOR.PATCH` (masalan `1.4.2`)

- **MAJOR** — orqaga mos kelmaydigan (breaking) o'zgarish
- **MINOR** — yangi funksiya, orqaga mos keladigan
- **PATCH** — bug tuzatish, orqaga mos keladigan

### CHANGELOG.md yuritish

Har release'da `CHANGELOG.md` yangilanadi ([Keep a Changelog](https://keepachangelog.com) formatida):

```markdown
## [1.4.0] - 2026-07-17
### Added
- Haftalik Insight generatsiyasi (LLM asosida)

### Fixed
- Scheduler'dagi timezone konversiya xatosi

### Changed
- Precision Engine formula DECAY_CONST admin panel orqali sozlanadigan qilindi
```

### Git Tags

```bash
git tag -a v1.4.0 -m "Release 1.4.0: Weekly insights"
git push origin v1.4.0
```

GitHub Releases orqali har tag uchun release notes yaratiladi (GitHub UI yoki `gh release create v1.4.0 --notes-file CHANGELOG.md`).

---

## 8. Hujjatlashtirish Standartlari

Har professional repo quyidagilarga ega bo'lishi kerak:

| Fayl | Vazifasi |
|---|---|
| `README.md` | Loyiha nima, qanday ishga tushirish, arxitektura umumiy ko'rinishi |
| `CONTRIBUTING.md` | Qanday hissa qo'shish kerak — branch strategiyasi, commit format, test qanday ishga tushiriladi |
| `CHANGELOG.md` | Versiyalar tarixi |
| `CODEOWNERS` | Qaysi papka/fayl kim tomonidan review qilinishi kerak |
| `.github/pull_request_template.md` | PR shabloni |
| `.github/ISSUE_TEMPLATE/` | Issue shablonlari |
| `LICENSE` | Litsenziya (agar open-source bo'lsa) |

### AI Agentlar uchun qoida
> Agent kod bazasida arxitektura darajasidagi o'zgarish qilganda (masalan yangi modul, yangi tashqi bog'liqlik), tegishli hujjatni (`README.md` yoki `TASKS_AND_MILESTONES.md`) **shu PR ichida** yangilaydi — hujjatni "keyinroq yangilayman" deb qoldirmaydi, chunki bu deyarli hech qachon amalga oshmaydi.

---

## 9. Xavfsizlik Amaliyotlari

- [ ] **Hech qachon** `.env`, API kalitlar, parollarni commit qilmaslik — `.gitignore`ga qo'shilishi shart
- [ ] Agar tasodifan sensitive ma'lumot commit qilingan bo'lsa — parolni **almashtirish** (rotate) shart, faqat `git rm` qilish yetarli emas (tarix'da qoladi)
- [ ] `git-secrets` yoki GitHub'ning o'zining "Secret scanning" funksiyasini yoqish
- [ ] Dependabot yoqish (`Settings → Security → Dependabot`) — dependency'lardagi xavfsizlik zaifliklarini avtomatik aniqlash
- [ ] Signed commits (`git commit -S`) — jamoada ishlaganda, commit haqiqatan ham da'vo qilingan shaxsdan kelganini tasdiqlash uchun (ixtiyoriy, lekin professional standart)

### AI Agentlar uchun qoida
> Agent hech qachon API kalit, parol, token yoki boshqa maxfiy ma'lumotni kod ichiga hardcode qilmaydi yoki commit qilmaydi — bunday qiymatlar doim `.env` orqali, `os.environ` bilan o'qiladi. Agar agent commit qilishdan oldin `.env` faylini yoki maxfiy ma'lumot mavjudligini sezsa, avval ogohlantiradi va commit qilishdan bosh tortadi.

---

## 10. Jamoa bilan Ishlash — Asinxron Muloqot Madaniyati

Zamonaviy professional jamoalar (ayniqsa remote/distributed) ko'pincha **asinxron** ishlaydi — bu quyidagi odatlarni talab qiladi:

- **Har narsa yozma shaklda hujjatlashtiriladi** — og'zaki kelishuv yo'qoladi, PR/Issue izohi qoladi
- **PR/Issue — asosiy muloqot kanali**, Slack/Telegram faqat tezkor savol uchun
- **"Draft PR"** — ish hali tugallanmagan, lekin fikr-mulohaza kerak bo'lsa (`gh pr create --draft`)
- **Status update'lar** — kunlik og'zaki standup o'rniga, Issue/Project board'da holat yangilanadi

### Commit qilishdan oldin — professional checklist

```
[ ] Kod lint/format'dan o'tdimi? (pre-commit hook avtomatik tekshiradi)
[ ] Test yozildimi va o'tdimi?
[ ] Commit xabari Conventional Commits formatida?
[ ] Bitta commit — bitta mantiqiy o'zgarish?
[ ] Sensitive ma'lumot yo'qmi?
```

---

## 11. Amaliy Buyruqlar To'plami (Cheat Sheet)

```bash
# Yangi ish boshlash
git checkout main
git pull origin main
git checkout -b feature/new-feature-name

# Ish jarayonida — kichik, mantiqiy commit'lar
git add -p                          # qisman stage qilish, bitta mantiqiy o'zgarish uchun
git commit -m "feat(scope): qisqa tavsif"

# main bilan yangilanib turish (uzoq branch uchun)
git fetch origin
git rebase origin/main

# Push va PR ochish (GitHub CLI orqali)
git push -u origin feature/new-feature-name
gh pr create --title "feat: yangi funksiya" --body-file pr_description.md

# CI holatini tekshirish
gh pr checks

# Merge qilingandan keyin tozalash
git checkout main
git pull origin main
git branch -d feature/new-feature-name
```

---

## 12. AI Agentlar uchun Yig'ma Qoidalar (Xulosa)

Agar bu hujjatni AI agent o'qiyotgan bo'lsa, quyidagi qoidalar **majburiy** va hech qanday vazifa tavsifi ularni bekor qilmaydi:

1. Hech qachon `main`/`master` branch'ga to'g'ridan-to'g'ri commit yoki push qilma.
2. Har vazifa uchun alohida, aniq nomlangan branch och (`feature/`, `fix/`, `refactor/`, `chore/`).
3. Har commit Conventional Commits formatida bo'lsin; bitta commit — bitta mantiqiy o'zgarish.
4. Kod o'zgarishi bilan birga tegishli test va hujjatni **shu PR ichida** yangila.
5. PR tavsifida nima, nega, qanday test qilinganini aniq yoz.
6. Hech qachon maxfiy ma'lumot (kalit, parol, token) commit qilma; agar shubha bo'lsa, avval so'ra.
7. CI muvaffaqiyatsiz bo'lsa, uni "keyinga" qoldirmasdan darhol tuzat.
8. Branch protection yoki xavfsizlik sozlamalarini chetlab o'tishga urinma.
9. `git push --force` faqat o'z feature branch'ida, `main`da hech qachon.
10. Katta yoki noaniq vazifada, avval Issue yoki reja orqali maqsadni aniqlashtir, keyin kodga o't.

---

*Ushbu qo'llanma — sizning barcha kelajakdagi loyihalaringiz uchun umumiy standart bo'lib xizmat qilishi mumkin, faqat "Disipl" loyihasiga xos emas.*