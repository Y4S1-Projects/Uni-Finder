// // src/App.js
// import React from 'react';
// import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
// import HomePage from './pages/HomePage';
// import SignInPage from './pages/SignInPage';
// import RecommendationsPage from './pages/RecommendationsPage';
// import BestRecommendationPage from './pages/BestRecommendationPage'; // Import the new component
// import Header from './components/Header';
// import Footer from './components/Footer';

// function App() {
//   return (
//     <Router>
//       <Header />
//       <Routes>
//         <Route path="/" element={<HomePage />} />
//         <Route path="/signin" element={<SignInPage />} />
//         <Route path="/recommendations" element={<RecommendationsPage />} />
//         {/* Add the new route for the best recommendation page */}
//         <Route path="/best-recommendation" element={<BestRecommendationPage />} />
//       </Routes>
//       <Footer />
//     </Router>
//   );
// }

// export default App;
// src/App.js
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, useLocation } from 'react-router-dom';
import HomePage from './pages/HomePage';
import SignInPage from './pages/SignInPage';
import KeywordsPage from './pages/KeywordsPage'; // Import the new component
import RecommendationsPage from './pages/RecommendationsPage';
import BestRecommendationPage from './pages/BestRecommendationPage';
import BudgetOptimizer from './pages/BudgetOptimizer'; // Import Budget Optimizer
import BudgetOptimizerNew from './pages/BudgetOptimizerNew'; // Import New Budget Optimizer
import Header from './components/Header';
import Footer from './components/Footer';

import AddReview from './pages/AddReview';
import SignUp from './pages/SignUp';
import SignIn from './pages/Signin';
import ProfileAll from './pages/ProfileAll';

import StudentMatcherPage from './scholarship_loan_matcher/StudentMatcherPage';
import ScholarshipMatcherPage from './scholarship_loan_matcher/ScholarshipMatcherPage';
import LoanMatcherPage from './scholarship_loan_matcher/LoanMatcherPage';

function AppContent() {
  const location = useLocation();
  const isHomePage = location.pathname === '/';

  useEffect(() => {
    if (isHomePage) {
      document.body.classList.add('homepage');
      document.body.classList.remove('non-homepage');
    } else {
      document.body.classList.remove('homepage');
      document.body.classList.add('non-homepage');
    }
  }, [isHomePage]);

  return (
    <>
      <Header />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/signin" element={<SignInPage />} />
        <Route path="/keywords" element={<KeywordsPage />} /> {/* New route */}
        <Route path="/recommendations" element={<RecommendationsPage />} />
        <Route path="/best-recommendation" element={<BestRecommendationPage />} />
        <Route path="/budget-optimizer" element={<BudgetOptimizer />} /> {/* Budget Optimizer route */}
        <Route path="/budget-optimizer-new" element={<BudgetOptimizerNew />} /> {/* New AI Budget Optimizer route */}

        {/* Scholarship & Loan Matcher */}
        <Route path="/scholarship-matcher" element={<StudentMatcherPage />} />
        <Route path="/scholarship-matcher/scholarships" element={<ScholarshipMatcherPage />} />
        <Route path="/scholarship-matcher/loans" element={<LoanMatcherPage />} />
 
        <Route path="/addReview" element={<AddReview />} />
        <Route path="/signUp" element={<SignUp />} />
        <Route path="/signInNew" element={<SignIn />} />
        <Route path="/all" element={<ProfileAll />} />

      </Routes>
      <Footer />
    </>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;