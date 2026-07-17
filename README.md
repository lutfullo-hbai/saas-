# Disipl — AI-Powered Personal Discipline & Goal Execution System

> "Sizga yo'l ko'rsatuvchi emas, sizni **nazorat qiluvchi** shaxsiy kotib."

## Hujjatlar

Batafsil hujjatlar [`docs/`](./docs/) papkasida:

- [Asosiy README](./docs/README.md) — loyiha vizyonu va arxitekturasi
- [Yo'l Xaritasi](./docs/readmee.md) — milestone'lar va batafsil vazifalar

## Tez boshlash

```bash
# 1. Muhitni sozlash
cp .env.example .env

# 2. Docker bilan ishga tushirish
docker-compose up -d

# 3. Testlarni ishga tushirish
pytest tests/ -v
```

## Loyiha Strukturasi

```
src/
├── domain/          # Biznes logika (freymvorkdan mustaqil)
├── application/     # Use case'lar va interfeyslar
├── infrastructure/  # Tashqi integratsiyalar (DB, LLM, Telegram)
├── presentation/    # API qatlami (FastAPI)
└── config/          # Sozlamalar
```

## Texnologik Stek

| Qatlam | Texnologiya |
|---|---|
| Backend API | FastAPI |
| Bot | aiogram |
| Bazasi | PostgreSQL 16 |
| Cache/Queue | Redis |
| Background | Celery + Beat |
| LLM | Claude API / Ollama |
| Auth | JWT |
| Dashboard | React + Tailwind |

## Litsenziya

Maxfiy — faqat ruxs etilgan shaxslar uchun.
