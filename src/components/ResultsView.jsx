import React, { useEffect } from 'react';
import confetti from 'canvas-confetti';
import { Trophy, CheckCircle, XCircle, RotateCcw, Home, AlertCircle } from 'lucide-react';

export default function ResultsView({ userName, answers, onRetake, onHome }) {
  const total = answers.length;
  const correctCount = answers.filter((a) => a.isCorrect).length;
  const wrongCount = total - correctCount;
  const percentage = Math.round((correctCount / total) * 100);

  const wrongAnswers = answers.filter((a) => !a.isCorrect);

  useEffect(() => {
    // Fire celebratory confetti for high scores
    if (percentage >= 70) {
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#9CD296', '#7EBF77', '#FFFFFF', '#FFD700']
      });
    }
  }, [percentage]);

  return (
    <div className="relative z-10 w-full max-w-2xl px-4 sm:px-6 my-10">
      <div className="glass-card rounded-[32px] p-6 sm:p-10 shadow-glass-card">
        
        {/* Header with Trophy */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-3xl bg-[#9CD296]/25 border border-[#9CD296]/50 mb-3 shadow-inner">
            <Trophy className="w-8 h-8 text-[#263528]" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#263528] tracking-tight">
            TEST YAKUNLANDI!
          </h1>
          <p className="text-sm font-medium text-[#263528]/70 mt-1">
            Ishtirokchi: <b className="text-[#263528]">{userName}</b>
          </p>
        </div>

        {/* Score Stats Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
          {/* Total */}
          <div className="p-4 rounded-2xl bg-white/50 border border-white/80 text-center">
            <span className="block text-xs text-[#263528]/60 font-semibold mb-1">Jami savollar</span>
            <span className="text-xl sm:text-2xl font-black text-[#263528]">{total}</span>
          </div>

          {/* Correct */}
          <div className="p-4 rounded-2xl bg-[#9CD296]/20 border border-[#9CD296]/40 text-center">
            <span className="block text-xs text-[#1B451A]/80 font-semibold mb-1">To‘g‘ri</span>
            <span className="text-xl sm:text-2xl font-black text-[#1B451A]">{correctCount}</span>
          </div>

          {/* Wrong */}
          <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-center">
            <span className="block text-xs text-red-700 font-semibold mb-1">Noto‘g‘ri</span>
            <span className="text-xl sm:text-2xl font-black text-red-700">{wrongCount}</span>
          </div>

          {/* Percentage */}
          <div className="p-4 rounded-2xl bg-[#9CD296]/30 border border-[#9CD296]/50 text-center">
            <span className="block text-xs text-[#1B451A] font-semibold mb-1">Natija</span>
            <span className="text-xl sm:text-2xl font-black text-[#1B451A]">{percentage}%</span>
          </div>
        </div>

        {/* Mistake Review Section */}
        {wrongAnswers.length > 0 ? (
          <div className="mb-8">
            <h3 className="text-sm font-bold text-[#263528] mb-3 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-600" />
              Xato qilingan savollar tahlili ({wrongAnswers.length} ta)
            </h3>

            <div className="space-y-4 max-h-[380px] overflow-y-auto pr-1">
              {wrongAnswers.map((item, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-2xl bg-white/45 border border-white/80 shadow-sm text-xs sm:text-sm"
                >
                  <p className="font-bold text-[#263528] mb-2">
                    {idx + 1}. {item.question}
                  </p>
                  
                  <div className="space-y-1.5 pl-2 border-l-2 border-red-400">
                    <p className="text-red-700 flex items-center gap-1.5 font-medium">
                      <XCircle className="w-3.5 h-3.5 flex-shrink-0" />
                      <span>Sizning javobingiz: {item.selectedLetter}) {item.selectedText}</span>
                    </p>
                    <p className="text-[#1B451A] flex items-center gap-1.5 font-semibold">
                      <CheckCircle className="w-3.5 h-3.5 flex-shrink-0" />
                      <span>To‘g‘ri javob: {item.correctLetter}) {item.correctText}</span>
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="mb-8 p-6 rounded-2xl bg-[#9CD296]/20 border border-[#9CD296]/40 text-center">
            <p className="text-sm font-bold text-[#1B451A]">
              🎉 Ajoyib natija! Siz birorta ham xato qilmadingiz!
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button
            type="button"
            onClick={onRetake}
            className="glass-button-primary py-4 px-6 rounded-2xl text-sm font-bold tracking-wider uppercase flex items-center justify-center gap-2 cursor-pointer"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Qayta test topshirish</span>
          </button>

          <button
            type="button"
            onClick={onHome}
            className="py-4 px-6 rounded-2xl text-sm font-bold tracking-wider uppercase flex items-center justify-center gap-2 cursor-pointer bg-white/70 hover:bg-white text-[#263528] border border-white/90 shadow-sm transition-all duration-200"
          >
            <Home className="w-4 h-4" />
            <span>Bosh sahifaga qaytish</span>
          </button>
        </div>

        {/* Ephemeral Notice */}
        <p className="text-center text-[11px] text-[#263528]/50 mt-6">
          Natijalar xotirada saqlanmaydi. Sahifa yangilanganda test yakunlanadi.
        </p>
      </div>
    </div>
  );
}

