import React, { useState } from 'react';
import { User, Lock, Sparkles, AlertCircle } from 'lucide-react';

export default function LoginCard({ onStart }) {
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) {
      setError('Iltimos, ismingizni kiriting');
      return;
    }
    setError('');
    onStart({ name: trimmed, password });
  };

  return (
    <div className="relative z-10 w-full max-w-md px-4 sm:px-6">
      <div className="glass-card rounded-[32px] p-8 sm:p-10 shadow-glass-card transition-all duration-300">
        
        {/* Apple style badge header */}
        <div className="flex justify-center mb-4">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#9CD296]/20 border border-[#9CD296]/40 text-[#263528] text-xs font-medium tracking-wide">
            <Sparkles className="w-3.5 h-3.5 text-[#263528]" />
            <span>YAKUNIY NAZORAT TESTI</span>
          </div>
        </div>

        {/* Title */}
        <h1 className="text-center text-2xl sm:text-3xl font-extrabold tracking-tight text-[#263528] mb-2">
          IQTISODIY TAHLIL
        </h1>
        <p className="text-center text-xs sm:text-sm text-[#263528]/70 mb-6">
          84 ta rasmiy test savollari asosidagi bilim sinovi
        </p>

        {/* Informative Notice as requested */}
        <div className="mb-6 p-3.5 rounded-2xl bg-[#9CD296]/15 border border-[#9CD296]/30 text-xs leading-relaxed text-[#263528]/85 flex items-start gap-2.5">
          <AlertCircle className="w-4 h-4 text-[#263528] flex-shrink-0 mt-0.5" />
          <p>
            <b>Eslatma:</b> Ismingizni kiriting va esingizda qoladigan parol tanlang. Chunki keyingi safar yana kirganingizda avvalgi natijalaringiz va test urinishlaringiz reytingga qo‘shilib boradi.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name Input */}
          <div>
            <label className="block text-xs font-semibold text-[#263528]/80 mb-1.5 ml-1">
              Ismingizni kiriting
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#263528]/50">
                <User className="w-4 h-4" />
              </div>
              <input
                type="text"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  if (error) setError('');
                }}
                placeholder="Masalan: Alisher Navoiy"
                className="glass-input w-full pl-10 pr-4 py-3 rounded-2xl text-sm font-medium text-[#263528] placeholder-[#263528]/40 focus:outline-none"
                autoComplete="off"
              />
            </div>
          </div>

          {/* Password Input */}
          <div>
            <label className="block text-xs font-semibold text-[#263528]/80 mb-1.5 ml-1">
              Parolingizni kiriting
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#263528]/50">
                <Lock className="w-4 h-4" />
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="glass-input w-full pl-10 pr-4 py-3 rounded-2xl text-sm font-medium text-[#263528] placeholder-[#263528]/40 focus:outline-none"
                autoComplete="off"
              />
            </div>
          </div>

          {error && (
            <p className="text-xs text-red-600 font-medium ml-1">
              {error}
            </p>
          )}

          {/* Action Button */}
          <button
            type="submit"
            className="glass-button-primary w-full py-3.5 px-6 rounded-2xl text-sm font-bold tracking-wider uppercase mt-2 flex items-center justify-center gap-2 cursor-pointer"
          >
            <span>TESTNI BOSHLASH</span>
            <span className="text-base">→</span>
          </button>
        </form>

        {/* Footer info */}
        <div className="mt-6 text-center text-[11px] text-[#263528]/50">
          Jami 84 ta rasmiy test savoli • Minimalistik Liquid Glass
        </div>
      </div>
    </div>
  );
}

