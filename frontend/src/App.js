import React, { useEffect } from "react";
import { BrowserRouter as Router, Route, Routes, useLocation } from "react-router-dom";
import HomePage from "./pages/HomePage";
import SignInPage from "./pages/SignInPage";
import CareerPath from "./pages/CareerPath";
import CareerLadderPage from "./pages/CareerLadderPage";
import BudgetOptimizer from "./pages/BudgetOptimizer"; // Import Budget Optimizer
import BudgetOptimizerNew from "./pages/BudgetOptimizerNew"; // Import New Budget Optimizer
import Header from "./components/Header";
import Footer from "./components/Footer";
import SignUp from "./pages/SignUp";
import SignIn from "./pages/Signin";

import StudentMatcherPage from "./scholarship_loan_matcher/StudentMatcherPage";
import ScholarshipMatcherPage from "./scholarship_loan_matcher/ScholarshipMatcherPage";
import LoanMatcherPage from "./scholarship_loan_matcher/LoanMatcherPage";
import AdminDatasetPage from "./scholarship_loan_matcher/AdminDatasetPage";
import AdminRouteGuard from "./scholarship_loan_matcher/AdminRouteGuard";

import OnboardingGateway from "./pages/degree-recommendation/DegreeHome";
import ALWizardFlow from "./pages/degree-recommendation/ALWizardFlow";
import OLExplorerFlow from "./pages/degree-recommendation/OLExplorerFlow";

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
		<div className='flex flex-col min-h-screen'>
			<Header />
			<main className='flex-grow'>
				<Routes>
					<Route path='/' element={<HomePage />} />
					<Route path='/signin' element={<SignInPage />} />
					<Route path='/career' element={<CareerPath />} />
					<Route path='/career-ladder' element={<CareerLadderPage />} />
					<Route path='/degree-recommendations' element={<OnboardingGateway />} />
					<Route path='/degree-recommendations/al-students' element={<ALWizardFlow />} />
					<Route path='/degree-recommendations/all-students' element={<OLExplorerFlow />} />
					<Route path='/budget-optimizer' element={<BudgetOptimizer />} /> {/* Budget Optimizer route */}
					<Route path='/budget-optimizer-new' element={<BudgetOptimizerNew />} /> {/* New AI Budget Optimizer route */}
					{/* Scholarship & Loan Matcher */}
					<Route path='/scholarship-matcher' element={<StudentMatcherPage />} />
					<Route path='/scholarship-matcher/scholarships' element={<ScholarshipMatcherPage />} />
					<Route path='/scholarship-matcher/loans' element={<LoanMatcherPage />} />
					<Route
						path='/scholarship-matcher/admin-datasets'
						element={
							<AdminRouteGuard>
								<AdminDatasetPage />
							</AdminRouteGuard>
						}
					/>
					<Route path='/signUp' element={<SignUp />} />
					<Route path='/signInNew' element={<SignIn />} />
				</Routes>
			</main>
			<Footer />
		</div>
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
