import MatcherFlowPage from './MatcherFlowPage';

export default function ScholarshipMatcherPage() {
  return (
    <MatcherFlowPage
      matchType="scholarship"
      eyebrow="Scholarship Focus"
      title="Scholarship Matching Assistant"
      lead="Provide a snapshot of your academic journey and funding needs to surface scholarships tailored for you."
      submitLabel="Find Scholarships"
      resultsTitle="Recommended Scholarships"
      emptyMessage="Submit the form to view scholarship opportunities."
    />
  );
}


