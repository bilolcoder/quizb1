import React, { useState } from 'react';
import ThreeBackground from './components/ThreeBackground';
import LoadingOrb from './components/LoadingOrb';
import LoginCard from './components/LoginCard';
import QuizConfig from './components/QuizConfig';
import QuizView from './components/QuizView';
import ResultsView from './components/ResultsView';
import { QUESTIONS } from './data/questions';

export default function App() {
  // Navigation states: 'login' | 'loading' | 'config' | 'quiz' | 'results'
  const [view, setView] = useState('login');
  const [user, setUser] = useState({ name: '', password: '' });
  const [activeQuestions, setActiveQuestions] = useState([]);
  const [finalAnswers, setFinalAnswers] = useState([]);

  // Generate shuffled questions and options
  const generateQuiz = (count) => {
    const totalAvailable = QUESTIONS.length;
    const safeCount = Math.max(1, Math.min(count, totalAvailable));

    // 1. Randomly sample 'safeCount' unique questions
    const shuffledPool = [...QUESTIONS].sort(() => Math.random() - 0.5);
    const selected = shuffledPool.slice(0, safeCount);

    const labels = ['A', 'B', 'C', 'D'];

    // 2. For each question, shuffle options independently
    return selected.map((q) => {
      const origCorrectText = q.options[q.correct_index];
      const shuffledOptions = [...q.options].sort(() => Math.random() - 0.5);
      const newCorrectIndex = shuffledOptions.indexOf(origCorrectText);
      const correctLetter = labels[newCorrectIndex];

      const optionsMap = {
        A: shuffledOptions[0],
        B: shuffledOptions[1],
        C: shuffledOptions[2],
        D: shuffledOptions[3],
      };

      return {
        id: q.id,
        question: q.question,
        options: optionsMap,
        correctLetter,
        correctText: origCorrectText,
      };
    });
  };

  // 1. User clicks 'TESTNI BOSHLASH' on login card
  const handleLoginStart = (loginData) => {
    setUser(loginData);
    // Transition to 5-second Three.js particle orb loading animation
    setView('loading');
  };

  // 2. 5-second loading animation completes
  const handleLoadingComplete = () => {
    // Transition smoothly to question count selection
    setView('config');
  };

  // 3. User selects number of questions
  const handleConfigConfirm = (count) => {
    const quizData = generateQuiz(count);
    setActiveQuestions(quizData);
    setView('quiz');
  };

  // 4. User completes the quiz
  const handleQuizFinish = (answers) => {
    setFinalAnswers(answers);
    setView('results');
  };

  // 5. Retake quiz with same user
  const handleRetake = () => {
    setFinalAnswers([]);
    setView('config');
  };

  // 6. Return to home / login
  const handleHome = () => {
    setUser({ name: '', password: '' });
    setActiveQuestions([]);
    setFinalAnswers([]);
    setView('login');
  };

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center p-4 selection:bg-[#9CD296]/40">
      {/* 3D Living Three.js Particle Background on all screens */}
      <ThreeBackground />

      {/* Main View Router */}
      <main className="w-full flex items-center justify-center">
        {view === 'login' && <LoginCard onStart={handleLoginStart} />}

        {view === 'loading' && <LoadingOrb onComplete={handleLoadingComplete} />}

        {view === 'config' && (
          <QuizConfig
            userName={user.name}
            totalAvailable={QUESTIONS.length}
            onConfirm={handleConfigConfirm}
          />
        )}

        {view === 'quiz' && (
          <QuizView
            questions={activeQuestions}
            onFinish={handleQuizFinish}
          />
        )}

        {view === 'results' && (
          <ResultsView
            userName={user.name}
            answers={finalAnswers}
            onRetake={handleRetake}
            onHome={handleHome}
          />
        )}
      </main>
    </div>
  );
}

