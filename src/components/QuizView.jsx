import React, { useState } from 'react';
import { CheckCircle2, XCircle, ArrowRight, BookOpen } from 'lucide-react';

export default function QuizView({ questions, onFinish }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedLetter, setSelectedLetter] = useState(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [userAnswers, setUserAnswers] = useState([]);

  const currentQ = questions[currentIndex];
  const total = questions.length;
  const progressPercent = Math.round(((currentIndex + 1) / total) * 100);

  const handleSelectOption = (letter) => {
    if (isAnswered) return;

    const isCorrect = letter === currentQ.correctLetter;
    setSelectedLetter(letter);
    setIsAnswered(true);

    const answerRecord = {
      questionId: currentQ.id,
      question: currentQ.question,
      selectedLetter: letter,
      selectedText: currentQ.options[letter],
      correctLetter: currentQ.correctLetter,
      correctText: currentQ.correctText,
      isCorrect
    };

    setUserAnswers((prev) => [...prev, answerRecord]);
  };

  const handleNext = () => {
    if (currentIndex + 1 < total) {
      setCurrentIndex((prev) => prev + 1);
      setSelectedLetter(null);
      setIsAnswered(false);
    } else {
      // Test finished
      onFinish(userAnswers);
    }
  };

  const isCurrentCorrect = selectedLetter === currentQ.correctLetter;

  return (
    <div className="relative z-10 w-full max-w-2xl px-4 sm:px-6">
      <div className="glass-card rounded-[32px] p-6 sm:p-10 shadow-glass-card transition-all duration-300">
        
        {/* Top Header: Category and Progress Counter */}
        <div className="flex items-center justify-between mb-4">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#9CD296]/20 border border-[#9CD296]/40 text-[#263528] text-xs font-semibold tracking-wide">
            <BookOpen className="w-3.5 h-3.5" />
            <span>IQTISODIY TAHLIL</span>
          </div>
          <span className="text-xs sm:text-sm font-bold font-mono text-[#263528]/80">
            Savol {currentIndex + 1} / {total}
          </span>
        </div>

        {/* Apple Style Progress Bar */}
        <div className="w-full h-1.5 bg-white/70 rounded-full overflow-hidden border border-[#9CD296]/30 shadow-inner mb-6">
          <div
            className="h-full bg-gradient-to-r from-[#9CD296] to-[#7EBF77] rounded-full transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        {/* Question Text */}
        <h2 className="text-lg sm:text-xl font-bold text-[#263528] leading-relaxed mb-6">
          {currentQ.question}
        </h2>

        {/* Options List */}
        <div className="space-y-3 mb-6">
          {['A', 'B', 'C', 'D'].map((letter) => {
            const optionText = currentQ.options[letter];
            const isSelected = selectedLetter === letter;
            const isThisCorrect = letter === currentQ.correctLetter;

            let optionClass = 'glass-option';

            if (isAnswered) {
              if (isThisCorrect) {
                optionClass = 'glass-option-correct font-semibold';
              } else if (isSelected && !isThisCorrect) {
                optionClass = 'glass-option-wrong font-semibold';
              } else {
                optionClass = 'glass-option opacity-60';
              }
            } else if (isSelected) {
              optionClass = 'glass-option-selected font-semibold';
            }

            return (
              <button
                key={letter}
                type="button"
                onClick={() => handleSelectOption(letter)}
                disabled={isAnswered}
                className={`w-full p-4 rounded-2xl text-left flex items-start gap-3.5 cursor-pointer disabled:cursor-default ${optionClass}`}
              >
                {/* Letter Badge */}
                <div
                  className={`w-7 h-7 rounded-xl flex items-center justify-center text-xs font-bold flex-shrink-0 transition-colors ${
                    isAnswered && isThisCorrect
                      ? 'bg-[#5BA854] text-white shadow-sm'
                      : isAnswered && isSelected
                      ? 'bg-red-500 text-white shadow-sm'
                      : 'bg-white/70 text-[#263528] border border-white'
                  }`}
                >
                  {letter}
                </div>

                {/* Option Text */}
                <span className="text-sm leading-snug pt-0.5 flex-1">
                  {optionText}
                </span>

                {/* Status Icon */}
                {isAnswered && isThisCorrect && (
                  <CheckCircle2 className="w-5 h-5 text-[#3E8E38] flex-shrink-0 mt-0.5" />
                )}
                {isAnswered && isSelected && !isThisCorrect && (
                  <XCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                )}
              </button>
            );
          })}
        </div>

        {/* Instant Feedback Banner */}
        {isAnswered && (
          <div
            className={`p-4 rounded-2xl mb-6 transition-all duration-300 flex items-start gap-3 ${
              isCurrentCorrect
                ? 'bg-[#9CD296]/20 border border-[#9CD296]/50 text-[#1B451A]'
                : 'bg-red-500/10 border border-red-500/30 text-[#7F1D1D]'
            }`}
          >
            {isCurrentCorrect ? (
              <CheckCircle2 className="w-5 h-5 text-[#3E8E38] flex-shrink-0 mt-0.5" />
            ) : (
              <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            )}
            <div className="text-xs sm:text-sm">
              <p className="font-bold">
                {isCurrentCorrect ? '✅ To‘g‘ri javob!' : '❌ Noto‘g‘ri javob!'}
              </p>
              {!isCurrentCorrect && (
                <p className="mt-1 text-xs opacity-90">
                  To‘g‘ri javob: <b>{currentQ.correctLetter}) {currentQ.correctText}</b>
                </p>
              )}
            </div>
          </div>
        )}

        {/* Next Question / Finish Button */}
        {isAnswered && (
          <button
            type="button"
            onClick={handleNext}
            className="glass-button-primary w-full py-4 px-6 rounded-2xl text-sm font-bold tracking-wider uppercase flex items-center justify-center gap-2 cursor-pointer"
          >
            <span>
              {currentIndex + 1 < total ? 'Keyingi savol' : 'Natijalarni ko‘rish'}
            </span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}

