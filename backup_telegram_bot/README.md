# Iqtisodiy Tahlil — Telegram Quiz Bot

Professional, to‘liq modulli va mustaqil ishlaydigan Telegram test boti. Bot «Iqtisodiy tahlil» fani bo‘yicha 84 ta rasmiy test savollari bazasiga ega bo‘lib, talabalar va o‘rganuvchilarning bilimlarini sinash, natijalarni tahlil qilish va umumiy reytingni yuritish uchun mo‘ljallangan.

---

## 🛠 Ishlatilgan texnologiyalar

- **Dasturlash tili:** Python 3.12+
- **Asosiy freymvork:** [aiogram 3](https://docs.aiogram.dev/) (Asinxron Telegram Bot freymvorki)
- **Ma'lumotlar bazasi:** SQLite (Asinxron ulanish uchun `aiosqlite`)
- **Konfiguratsiya:** `python-dotenv`
- **Format:** JSON (84 ta to‘liq test savollari)

---

## 📂 Loyiha tuzilishi

```text
iqtisodiy-quiz-bot/
│
├── bot.py                # Asosiy ishga tushiruvchi fayl (Main entrypoint)
├── watchdog.py           # 24/7 Nazoratchi, avto-qayta ishga tushiruvchi servis
├── start_bot.bat         # 🚀 Botni fonda 24/7 ishga tushirish (Sichqoncha bilan 2 marta bosing)
├── stop_bot.bat          # 🛑 Botni xavfsiz to'xtatish
├── status_bot.bat        # 📊 Bot holati, RAM va so'nggi loglarni ko'rish
├── config.py             # Sozlamalar va muhit o'zgaruvchilari
├── database.py           # SQLite ma'lumotlar bazasi (WAL crash-resilient rejimida)
├── keyboards.py          # Reply va Inline tugmalar
├── requirements.txt      # Loyiha uchun zaruriy Python kutubxonalari
├── .env                  # Maxfiy sozlamalar (BOT_TOKEN, ADMIN_ID)
├── .env.example          # Namuna .env fayli
├── .gitignore            # Git uchun e'tiborga olinmaydigan fayllar
├── README.md             # Loyiha qo'llanmasi
│
├── data/
│   ├── questions.json    # 84 ta rasmiy test savollari bazasi
│   └── quizbot.db        # SQLite ma'lumotlar bazasi (avtomatik yaratiladi)
│
├── handlers/             # Telegram xabarlarini qayta ishlovchi modullar
│   ├── __init__.py       # Routerlarni birlashtirish
│   ├── start.py          # /start, /menu va bot haqida
│   ├── quiz.py           # Test jarayoni, javoblarni tekshirish va yakunlash
│   ├── results.py        # Shaxsiy statistika va reyting
│   └── admin.py          # Administrator buyruqlari va boshqaruvi
│
└── services/             # Biznes mantiq qatlami
    ├── __init__.py
    └── quiz_service.py   # Savollarni aralashtirish, formatlash va tahlil
```

---

## 🚀 Ishga tushirish bo‘yicha bosqichma-bosqich qo‘llanma

### 1. Python o‘rnatish

Agar kompyuteringizda Python o‘rnatilmagan bo‘lsa:
- [python.org](https://www.python.org/downloads/) rasmiy veb-saytidan **Python 3.12** yoki undan yuqori versiyasini yuklab oling.
- O‘rnatish jarayonida **«Add python.exe to PATH»** bandiga belgi qo‘yishni unutmang.

Versiyani tekshirish:
```bash
python --version
```

---

### 2. Virtual environment (Virtual muhit) yaratish

Loyiha papkasiga kiring va izolyatsiyalangan virtual muhit yarating:

**Windows uchun:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS uchun:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Kutubxonalarni o‘rnatish

Barcha kerakli kutubxonalarni `requirements.txt` faylidan o‘rnating:

```bash
pip install -r requirements.txt
```

---

### 4. `.env` faylini sozlash

Loyiha ildizidagi `.env` faylini oching (yoki `.env.example` nusxasini `.env` deb nomlang):

```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=7548230903
```

- `BOT_TOKEN`: Telegram’da [@BotFather](https://t.me/BotFather) botiga `/newbot` buyrug‘ini berib olingan token.
- `ADMIN_ID`: Administratorning Telegram ID raqami (masalan: `7548230903`).

---

### 5. Botni fonda 24/7 avtomatik ishga tushirish

Botni boshqarish uchun sichqoncha bilan quyidagi fayllardan birini ikki marta bosish kifoya:

- **`start_bot.bat`** — Botni va uning nazoratchi xizmatini fonda ishga tushiradi.
  - Hech qanday konsol yoki terminal oynasini ochiq saqlash shart emas.
  - Kompyuter qayta yoqilganda (reboot) avtomatik ishga tushishni sozlaydi (`Windows Startup`).
  - Agar bot kutilmaganda to‘xtab qolsa (internet uzilishi, xatolik), nazoratchi uni 5 soniyada avtomatik qayta ishga tushiradi.
- **`status_bot.bat`** — Botning joriy holati (faol/to‘xtatilgan), qancha operativ xotira (RAM) ishlatayotgani va oxirgi log xabarlarini ko‘rsatadi.
- **`stop_bot.bat`** — Botni va nazoratchi xizmatini xavfsiz to‘xtatadi.

---

### 6. Standart usulda terminaldan ishga tushirish (Test uchun)

Agar botni bevosita terminal oynasida kuzatib ishga tushirmoqchi bo‘lsangiz:

```bash
python bot.py
```

- To‘xtatish uchun: `Ctrl + C`

---

## 🎯 Botning asosiy imkoniyatlari

1. **Start menyusi va avtomatik ro‘yxat:**
   - Foydalanuvchi botga ilk bor kirganida ma'lumotlar bazasiga avtomatik qayd etiladi.
   - Qayta kirganda yangi foydalanuvchi sifatida takrorlanmaydi, faqat oxirgi faolligi yangilanadi.

2. **Savollar sonini moslashuvchan tanlash:**
   - Foydalanuvchi 1 dan 84 gacha bo‘lgan istalgan sonni kiritishi mumkin (masalan: 10, 20, 30, 50 yoki 84).
   - Qat'iy validatsiya: 0, manfiy sonlar, 84 dan katta sonlar yoki harflar kiritilganda bot xushmuomalalik bilan ogohlantiradi.

3. **Savollar va javoblarni mustaqil aralashtirish:**
   - Har bir yangi testda savollar tasodifiy tartibda tanlanadi.
   - Har bir savolning A, B, C, D variantlari bir-biridan mustaqil aralashtiriladi.
   - To‘g‘ri javob matn orqali aniqlanadi, shuning uchun hech qachon yo‘qolmaydi.

4. **Tezkor natija va takroriy bosishdan himoya:**
   - Har bir javob tanlanganda bot darhol to‘g‘ri yoki noto‘g‘ri ekanligini ko‘rsatadi.
   - Tugmalar darhol o‘chiriladi va foydalanuvchi javobini o‘zgartira olmaydi.
   - Avtomatik keyingi savol yuboriladi.

5. **Kengaytirilgan xatolar tahlili:**
   - Test yakunida to‘g‘ri/noto‘g‘ri soni va foiz ko‘rsatiladi.
   - Foydalanuvchi xato qilgan har bir savol bo‘yicha: savol matni, foydalanuvchi tanlagan javob va to‘g‘ri javob ko‘rsatib beriladi.

6. **Shaxsiy natijalar va umumiy reyting:**
   - «📊 Mening natijalarim»: Jami testlar soni, eng yaxshi, oxirgi va o‘rtacha foizlar.
   - «🏆 Reyting»: Barcha foydalanuvchilar orasida eng yuqori natijaga erishgan TOP-10 talaba.

7. **Administrator tizimi va xabarnomalar:**
   - Har bir foydalanuvchi testni yakunlashi bilan administratorning shaxsiy Telegramiga batafsil hisobot (Ism, Username, ID, natija, urinish raqami) keladi.
   - Faqat `ADMIN_ID` egalari uchun maxsus buyruqlar:
     - `/admin` — Boshqaruv paneli
     - `/stats` — Botning to‘liq statistikasi
     - `/users` — Barcha foydalanuvchilar ro‘yxati (sahifalangan)
     - `/results` — Barcha test urinishlari tarixi (sahifalangan)
     - `/top` — Eng yaxshi natijalar reytingi

---

## 🔧 Muammolarni bartaraf etish (Troubleshooting)

| Muammo | Sababi | Yechimi |
|---|---|---|
| `[XATOLIK] .env fayliga haqiqiy BOT_TOKEN kiritilmagan!` | `.env` faylida token ko‘rsatilmagan yoki `YOUR_BOT_TOKEN` holatida qolgan | `.env` faylini ochib, BotFather'dan olingan tokenni kiriting |
| `TelegramUnauthorizedError` | Token noto‘g‘ri yoki bekor qilingan | Token to‘g‘ri nusxalanganini tekshiring |
| `ModuleNotFoundError: No module named 'aiogram'` | Kutubxonalar virtual muhitga o‘rnatilmagan | `pip install -r requirements.txt` buyrug‘ini bajaring |
| Admin buyruqlari ishlamayapti | Telegram ID mos emas | `.env` dagi `ADMIN_ID` qiymatini o‘zingizning haqiqiy Telegram ID raqamingizga o‘zgartiring (ID ni bilish uchun [@userinfobot](https://t.me/userinfobot) dan foydalaning) |
| Admin xabarnomasi bormayapti | Administrator botga hali `/start` bosmagan | Administrator botga kamida bir marta kirib `/start` bosishi shart |

