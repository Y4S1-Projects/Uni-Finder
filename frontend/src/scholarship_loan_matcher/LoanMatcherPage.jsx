import MatcherFlowPage from './MatcherFlowPage';

export default function LoanMatcherPage() {
  return (
    <MatcherFlowPage
      matchType="loan"
      eyebrow="Loan Focus"
      title="Education Loan Matching Assistant"
      lead="Share your repayment comfort, study plans, and financial constraints to find suitable education loans."
      submitLabel="Find Loans"
      resultsTitle="Recommended Loans"
      emptyMessage="Submit the form to view education loan options."
    />
  );
}


