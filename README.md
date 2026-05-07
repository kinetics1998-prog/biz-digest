# SIGNAL
### Читай ринок. Будуй зв'язки.

Закрита B2B мережа підприємців **UA · PL · RO · TR**.
Бізнес-дайджест + AI-матчинг + B2B каталоги в одному продукті.

---

## Що це таке

**SIGNAL** — єдина платформа де можна:
1. Прочитати про угоду на ринку (бізнес-дайджест)
2. За 5 хвилин знайти партнера по своїй ніші (AI-матчинг)
3. Подивитися каталог виробника і написати йому напряму (B2B каталоги)

Все без LinkedIn, без виставок, без холодних дзвінків.

---

## Для кого

**Аудиторія:** SMB підприємці що працюють на ринках UA / PL / RO / TR або між ними.

**Типові учасники:**
- 🇺🇦 UA виробник → шукає байєра або дистриб'ютора в EU
- 🇵🇱 PL байєр → шукає UA/TR постачальника
- 🇷🇴 RO імпортер → шукає товари EU/UA/TR без посередників
- 🇹🇷 TR експортер → шукає дистриб'ютора в EU
- E-commerce, HoReCa, інвестори, food, FMCG, рітейл

---

## Структура репо

```
signal/
├── index.html                  ← Головний лендинг
├── partner.html                ← Квіз-воронка для партнерів (4 мови)
├── README.md                   ← цей файл
│
├── catalog/                    ← B2B каталоги
│   ├── index.html              ← Список брендів
│   └── lime.html               ← LIME — перший приклад
│
├── news/                       ← Бізнес-новини
│   └── index.html              ← Стрічка новин з категоріями
│
├── orbit/                      ← Закрита мережа (повний профіль)
│   ├── onboarding.html         ← 5-кроковий wizard
│   ├── save_profile.php        ← API → MySQL + Telegram
│   └── config.php              ← Credentials (НЕ в git)
│
├── magazines/                  ← Архів дайджестів (HTML)
├── data/                       ← RSS-збір (JSON)
├── biz-digest.py               ← Pipeline: RSS → Claude → HTML + Telegram
├── rss_collector.py            ← Збирач RSS
├── magazine_generator.py       ← HTML-журнал
└── .github/workflows/          ← Автозапуск 2× на день
```

---

## Точки входу для користувачів

| Хто | Куди йде | Що отримує |
|---|---|---|
| Партнер з посилання в Telegram | `partner.html` | Квіз 3 кроки → персональний матчинг |
| Читач дайджесту | `news/` | Стрічка новин 4 ринків |
| Виробник з товарами | `catalog/` → `catalog/lime.html` | B2B каталог-візитка з контактами |
| Серйозний учасник | `orbit/onboarding.html` | Повний профіль для AI-матчингу |
| Хтось хто чув про SIGNAL | `index.html` | Лендинг з усіма опціями |

---

## Каталог — як працює

**Партнер бачить:**
- Картки товарів з SKU, фото-данимі, EAN, упаковкою
- Ціна відкрито: "опт від 2.50€"
- 3 кнопки на кожному товарі: **WhatsApp · Telegram · Email**
- Кожне посилання вже має готовий текст: "Цікавить SKU XXX, прайс?"

**Як партнер додає свій каталог:**
1. **PDF-завантаження** (як LIME) → AI парсить і створює картки автоматично
2. **Excel-шаблон** → завантаження + автоімпорт у БД
3. **Форма вручну** → для партнерів з 1-3 SKU

Зараз перший варіант (LIME) — як приклад. Парсер PDF — наступний крок.

---

## Технічний стек

| Компонент | Рішення |
|---|---|
| Лендинг + статика | GitHub Pages (`kinetics1998-prog.github.io/signal`) |
| Бекенд API | Hostinger PHP (`chysto.media/signal/orbit/`) |
| База даних | MySQL Hostinger (`u227106289_mixzu`) |
| AI-вижимки | Claude API (`claude-sonnet-4-20250514`) |
| AI-матчинг | Claude API (в розробці) |
| Email | SendPulse (list_id: 617613) |
| Telegram (SIGNAL) | Окремий канал `@signal_ua` (потрібно створити) |
| Telegram (chysto.media) | `@chysto_media` — окремий проєкт, не пов'язаний |
| Автоматизація | GitHub Actions 2× на день |

---

## Дизайн-система

**Pure White editorial:**
- Шрифти: `Cormorant Garamond` (display) + `Inter` (body) + `JetBrains Mono` (labels)
- Кольори: ink `#0e0e0c`, paper `#fff`, soft `#faf8f4`, red `#c0392b`, lime `#43A047`
- Канали зв'язку: WhatsApp `#25d366`, Telegram `#0088cc`
- Mobile-first: всі сторінки оптимізовані під телефон

---

## Монетизація

| Тариф | Ціна | Що включає |
|---|---|---|
| **Reader** | 0€ | Telegram-дайджест, журнал, новини |
| **Member** | €29/міс | + 10 AI-матчів/тиждень, Topic→People, повний профіль |
| **Pro/Team** | €99/міс | + до 5 профілів, аналітика, API, пріоритет |

**Прогноз 6 міс:** 200 Member = €5 800/міс. Конверсія читач → Member ~10%.

---

## Поточний статус

### ✅ Зроблено
- [x] `index.html` — головний лендинг
- [x] `partner.html` — квіз-воронка 4 мови (UA/PL/RO/TR), WhatsApp/Telegram/Email
- [x] `catalog/index.html` — список брендів
- [x] `catalog/lime.html` — LIME повний каталог 25+ SKU з контактами
- [x] `news/index.html` — новини з категоріями + Telegram CTA
- [x] `orbit/onboarding.html` — 5-кроковий wizard
- [x] `orbit/save_profile.php` — бекенд (потребує credentials)
- [x] `biz-digest.py` — автодайджест 2× на день
- [x] GitHub Pages деплой автоматичний

### 🔧 В процесі
- [ ] Заповнити `orbit/config.php` реальними DB credentials
- [ ] Залити `assets/lime-katalog-2026.pdf` для downloadable
- [ ] Підключити waitlist `index.html` до SendPulse
- [ ] `save_lead.php` — бекенд для quiz-форми partner.html
- [ ] Telegram-нотифікації leads на `@signal_ua` чат

### 📋 Наступні кроки (Q2 2026)
- [ ] PDF-парсер для каталогів партнерів (Claude vision API)
- [ ] `orbit/dashboard.html` — особистий кабінет учасника
- [ ] AI-матчинг pipeline (Claude API)
- [ ] Topic→People фіча
- [ ] Stripe €29 підписка
- [ ] Аудіо-дайджест (TTS) для машини
- [ ] Додати другий бренд у каталог

---

## Ринковий контекст

- **100 000+** українських бізнесів у Польщі (з 2022)
- **88%** UA фірм у Польщі ведуть B2B з місцевими
- **$5.1B** прогноз e-commerce України до 2026
- **0** платформ для SMB у трикутнику UA/PL/RO/TR

---

## Контакти

- **Власник:** Руслан (ruslan.nyubin@gmail.com)
- **Telegram канал SIGNAL:** `@signal_ua` (буде створено окремо)
- **Інші проєкти власника:** chysto.media (Telegram `@chysto_media`) — окремий проєкт, не пов'язаний з SIGNAL
- **GitHub:** [kinetics1998-prog/signal](https://github.com/kinetics1998-prog/signal)
- **Live:** [kinetics1998-prog.github.io/signal](https://kinetics1998-prog.github.io/signal)
