import React, { useEffect } from "react";
import { BrowserRouter as Router, Route, Routes, useLocation } from "react-router-dom";
import HomePage from "./pages/HomePage";
import SignInPage from "./pages/SignInPage";
import CareerPath from "./pages/CareerPath";
import CareerLadder from "./pages/CareerLadder";
import BudgetOptimizer from "./pages/BudgetOptimizer"; // Import Budget Optimizer
import BudgetOptimizerNew from "./pages/BudgetOptimizerNew"; // Import New Budget Optimizer
import Header from "./components/Header";
import Footer from "./components/Footer";
import SignUp from "./pages/SignUp";
import SignIn from "./pages/Signin";

import StudentMatcherPage from "./scholarship_loan_matcher/StudentMatcherPage";
import ScholarshipMatcherPage from "./scholarship_loan_matcher/ScholarshipMatcherPage";
import LoanMatcherPage from "./scholarship_loan_matcher/LoanMatcherPage";

import DegreeRecommendationsPage from "./pages/DegreeRecommendationsPage";

function AppContent() {
	const location = useLocation();
	const isHomePage = location.pathname === "/";

	useEffect(() => {
		if (isHomePage) {
			document.body.classList.add("homepage");
			document.body.classList.remove("non-homepage");
		} else {
			document.body.classList.remove("homepage");
			document.body.classList.add("non-homepage");
		}
	}, [isHomePage]);

	return (
		<>
			<Header />
			<Routes>
				<Route path='/' element={<HomePage />} />
				<Route path='/signin' element={<SignInPage />} />
				<Route path='/career' element={<CareerPath />} />
				<Route path='/career-ladder' element={<CareerLadder />} />
				<Route path='/degree-recommendations' element={<DegreeRecommendationsPage />} />
				<Route path='/budget-optimizer' element={<BudgetOptimizer />} /> {/* Budget Optimizer route */}
				<Route path='/budget-optimizer-new' element={<BudgetOptimizerNew />} /> {/* New AI Budget Optimizer route */}
				{/* Scholarship & Loan Matcher */}
				<Route path='/scholarship-matcher' element={<StudentMatcherPage />} />
				<Route path='/scholarship-matcher/scholarships' element={<ScholarshipMatcherPage />} />
				<Route path='/scholarship-matcher/loans' element={<LoanMatcherPage />} />
				<Route path='/signUp' element={<SignUp />} />
				<Route path='/signInNew' element={<SignIn />} />
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
