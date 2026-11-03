# Iqtisodiy Tahlil — Zamonaviy Web Test Platformasi

Apple kompaniyasining **Liquid Glass** dizayn falsafasi asosida yaratilgan, minimalist va mustaqil (serverga bog‘lanmagan) veb-test platformasi.

Platforma **«Iqtisodiy tahlil»** fanidan barcha 84 ta rasmiy test savollarini to‘liq o‘z ichiga oladi.

---

## ✨ Asosiy imkoniyatlar va dizayn

- **Apple Liquid Glass uslubi:** Glassmorphism, shaffof oynasimon kartalar, mayin soyalar va nafis tipografika.
- **Brend ranglari:**
  - Asosiy yashil: `#9CD296`
  - Fon: `#F5F9F4`
  - Matn: `#263528`
  - Oq: `#FFFFFF`
- **Jonli Three.js 3D fon:** Butun sahifa bo‘ylab erkin suzuvchi 3D zarralar, nozik bog‘lovchi chiziqlar va sichqoncha harakatiga yengil sokin reaksiya.
- **5 soniyalik Three.js Particle Orb loading animatsiyasi:** Foydalanuvchi «Testni boshlash» tugmasini bosganda, zarralar markazga to‘planib, aylanuvchi shar (Orb) hosil qiladi va 0% dan 100% gacha silliq tayyorlanadi.
- **100% mustaqil (Server va bazasiz):**
  - Hech qanday ma'lumotlar bazasi yoki backend talab qilinmaydi.
  - Natijalar `localStorage` yoki serverga yozilmaydi.
  - Sahifa yangilansa yoki yopilsa, test sessiyasi tozalangan holda qayta ochiladi.
- **84 ta rasmiy test savollari:**
  - Savollar va A, B, C, D variantlari har safar tasodifiy aralashtiriladi.
  - To‘g‘ri javob matn orqali aniqlangani bois hech qachon adashmaydi.
  - Har bir savolga javob berilishi bilan to‘g‘ri/noto‘g‘ri ekani darhol ko‘rsatiladi.
  - Test yakunida xato qilingan savollar tahlili taqdim etiladi.
- **Vercel / Netlify / Statik hostinglarga 100% tayyor.**

---

## 📂 Loyiha tuzilishi

```text
quizbot/
│
├── index.html                  # Asosiy HTML hujjati
├── package.json                # Loyiha sozlamalari va paketlar
├── vite.config.js              # Vite konfiguratsiyasi (Three.js chunking bilan)
├── tailwind.config.js          # Tailwind CSS sozlamalari
├── postcss.config.js           # PostCSS sozlamalari
├── vercel.json                 # Vercel uchun statik marshrutlash
├── start_web.bat               # 🚀 Saytni mahalliy ishga tushirish (ikki marta bosing)
├── build.bat                   # 📦 Vercel uchun dist/ yaratish
│
├── src/
│   ├── main.jsx                # React boshlang'ich nuqtasi
│   ├── App.jsx                 # Asosiy ilova va holat boshqaruvi
│   ├── index.css               # Apple Liquid Glass sinflari
│   │
│   ├── data/
│   │   └── questions.js        # 84 ta rasmiy test savoli (asl kirill yozuvida)
│   │
│   └── components/
│       ├── ThreeBackground.jsx # 3D suzuvchi zarralar foni
│       ├── LoadingOrb.jsx       # 5 soniyalik Particle Orb Three.js loading animatsiyasi
│       ├── LoginCard.jsx        # Ism va parol kiritiladigan Liquid Glass oyna
│       ├── QuizConfig.jsx       # Savollar sonini tanlash (10, 20, 30, 50, 84)
│       ├── QuizView.jsx         # Test topshirish va darhol to'g'ri/noto'g'ri ko'rsatish
│       └── ResultsView.jsx      # Yakuniy natijalar, foiz va xatolar tahlili
│
└── backup_telegram_bot/        # Eski Telegram bot kodlarining to'liq zaxira nusxasi
```

---

## 🚀 Kompyuterda ishga tushirish (Local Run)

### 1-usul: Oddiygina sichqoncha bilan (Tavsiya etiladi)
Loyiha papkasidagi **`start_web.bat`** faylini ikki marta bosing. U avtomatik tarzda:
1. Mahalliy serverni ishga tushiradi.
2. Brauzeringizda **`http://localhost:3000`** manzilini ochadi.

### 2-usul: Terminal orqali
```bash
npm run dev
```

---

## 🌐 Saytni bepul Vercel hostingiga joylashtirish (Deploy)

Sayt 100% statik frontend bo‘lganligi sababli, uni Vercel, Netlify yoki GitHub Pages platformalariga **mutlaqo bepul** va **cheksiz muddatga** joylashtirish mumkin.

### Vercel veb-sayti orqali (Eng oson yo‘l):
1. **`build.bat`** faylini ikki marta bosing (yoki terminalda `npm run build` deb yozing).
2. Natijada loyihada **`dist`** papkasi hosil bo‘ladi.
3. [Vercel.com](https://vercel.com) saytiga kiring va kiring.
4. `dist` papkasini Vercel oynasiga shunchaki **Drag & Drop** (tortib tashlang).
5. 10 soniyada sizga `https://sizning-saytingiz.vercel.app` ko‘rinishidagi bepul va doimiy ishlovchi havola beriladi!

### GitHub orqali Vercelga ulash:
1. Ushbu loyihani o‘zingizning GitHub hisobingizga yuklang (`git push`).
2. Vercel dashboardida **«Add New Project»** tugmasini bosing va GitHub repozitoriyangizni tanlang.
3. Vercel avtomatik ravishda loyihani yig‘adi (`npm run build`) va doimiy 24/7 ishlaydigan havolani taqdim etadi!
