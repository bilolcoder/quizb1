import React, { useState } from 'react';
import { Layers, ArrowRight, BookOpen, Check } from 'lucide-react';

export default function QuizConfig({ userName, totalAvailable = 84, onConfirm }) {
  const [selectedCount, setSelectedCount] = useState(20);
  const [customValue, setCustomValue] = useState('');
  const [isCustom, setIsCustom] = useState(false);
  const [error, setError] = useState('');

  const presets = [10, 20, 30, 50, 84];

  const handleSelectPreset = (num) => {
    setSelectedCount(num);
    setIsCustom(false);
    setCustomValue('');
    setError('');
  };

  const handleCustomChange = (e) => {
    const val = e.target.value.replace(/\D/g, '');
    setCustomValue(val);
    setIsCustom(true);
    if (val) {
      const num = parseInt(val, 10);
      if (num < 1 || num > totalAvailable) {
        setError(`Iltimos, 1 dan ${totalAvailable} gacha son kiriting`);
      } else {
        setSelectedCount(num);
        setError('');
      }
    } else {
      setError('Iltimos, son kiriting');
    }
  };

  const handleStart = () => {
    let finalCount = selectedCount;
    if (isCustom) {
      const num = parseInt(customValue, 10);
      if (!num || num < 1 || num > totalAvailable) {
        setError(`Iltimos, 1 dan ${totalAvailable} gacha bo‘lgan son kiriting`);
        return;
      }
      finalCount = num;
    }
    onConfirm(finalCount);
  };

  return (
    <div className="relative z-10 w-full max-w-lg px-4 sm:px-6">
      <div className="glass-card rounded-[32px] p-8 sm:p-10 shadow-glass-card">
        
        {/* Welcome header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-2xl bg-[#9CD296]/25 border border-[#9CD296]/40 flex items-center justify-center text-[#263528]">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg sm:text-xl font-bold text-[#263528]">
              Xush kelibsiz, {userName}!
            </h2>
            <p className="text-xs text-[#263528]/70">
              Bizda jami {totalAvailable} ta test savoli mavjud
            </p>
          </div>
        </div>

        {/* Question count selector */}
        <div className="mb-6">
          <label className="block text-sm font-semibold text-[#263528] mb-3 flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#263528]" />
            Nechta test savoli ishlamoqchisiz?
          </label>

          {/* Quick preset buttons */}
          <div className="grid grid-cols-5 gap-2 sm:gap-2.5 mb-4">
            {presets.map((num) => {
              const active = !isCustom && selectedCount === num;
              return (
                <button
                  key={num}
                  type="button"
                  onClick={() => handleSelectPreset(num)}
                  className={`py-3 px-2 rounded-2xl text-sm font-bold transition-all duration-200 cursor-pointer ${
                    active
                      ? 'bg-[#9CD296] text-[#263528] border border-white/80 shadow-md transform -translate-y-0.5'
                      : 'glass-input text-[#263528]/80 hover:bg-white/80'
                  }`}
                >
                  {num}
                </button>
              );
            })}
          </div>

          {/* Custom count input */}
          <div className="mt-3">
            <input
              type="text"
              value={customValue}
              onChange={handleCustomChange}
              placeholder={`Boshqa son kiritish (1 - ${totalAvailable})...`}
              className={`glass-input w-full px-4 py-3 rounded-2xl text-sm font-medium text-[#263528] placeholder-[#263528]/40 focus:outline-none ${
                isCustom ? 'border-[#9CD296] bg-white/80' : ''
              }`}
            />
          </div>

          {error && (
            <p className="text-xs text-red-600 font-medium mt-2 ml-1">
              {error}
            </p>
          )}
        </div>

        {/* Feature summary */}
        <div className="p-4 rounded-2xl bg-white/40 border border-white/70 text-xs text-[#263528]/80 space-y-2 mb-6">
          <div className="flex items-center gap-2">
            <Check className="w-3.5 h-3.5 text-[#5BA854]" />
            <span>Savollar va variantlar tasodifiy tartibda aralashtiriladi</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-3.5 h-3.5 text-[#5BA854]" />
            <span>Har bir savoldan keyin to‘g‘ri javob darhol ko‘rsatiladi</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-3.5 h-3.5 text-[#5BA854]" />
            <span>Xato qilingan savollar test yakunida batafsil tahlil qilinadi</span>
          </div>
        </div>

        {/* Confirm and Start Button */}
        <button
          type="button"
          onClick={handleStart}
          className="glass-button-primary w-full py-4 px-6 rounded-2xl text-sm font-bold tracking-wider uppercase flex items-center justify-center gap-2 cursor-pointer"
        >
          <span>SAVOLLARNI BOSHLASH ({selectedCount} TA)</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

