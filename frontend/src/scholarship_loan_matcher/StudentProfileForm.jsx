import { useMemo, useState } from 'react';

// Sri Lankan Districts (25 districts)
const SRI_LANKAN_DISTRICTS = [
  'Ampara',
  'Anuradhapura',
  'Badulla',
  'Batticaloa',
  'Colombo',
  'Galle',
  'Gampaha',
  'Hambantota',
  'Jaffna',
  'Kalutara',
  'Kandy',
  'Kegalle',
  'Kilinochchi',
  'Kurunegala',
  'Mannar',
  'Matale',
  'Matara',
  'Moneragala',
  'Mullaitivu',
  'Nuwara Eliya',
  'Polonnaruwa',
  'Puttalam',
  'Ratnapura',
  'Trincomalee',
  'Vavuniya'
];


// A/L Streams
const AL_STREAMS = [
  'Physical Science',
  'Bio Science',
  'Commerce',
  'Arts',
  'Technology',
  'Other'
];

// English Result Options
const ENGLISH_RESULTS = [
  'A', 'B', 'C', 'S', 'F'
];

// University Registration Status
const UNI_REGISTRATION_STATUS = [
  'Not Registered',
  'State University',
  'Non-State / Private'
];

// Preferred Field of Study
const PREFERRED_FIELDS = [
  'All Fields',
  'IT',
  'Engineering',
  'Medicine',
  'Management',
  'Law',
  'Arts',
  'Science',
  'Other'
];

// A/L Years (2020-2024)
const AL_YEARS = ['2024', '2023', '2022', '2021', '2020'];

// Target Institute Types
const INSTITUTE_TYPES = [
  'NSHEI (Degree Awarding Institute)',
  'Private University',
  'Foreign University'
];

// Guarantor Options
const GUARANTOR_OPTIONS = [
  'None',
  '1 Guarantor',
  '2 Guarantors'
];

// Employment Status
const EMPLOYMENT_STATUS = [
  'Unemployed',
  'Employed Full-time'
];

// Scholarship Form Initial State (prefilled for demo, still editable)
const scholarshipInitialState = {
  alStream: 'Commerce',
  alStreamOther: '',
  zScore: '1.4502',
  district: 'Colombo',
  englishResult: 'B',
  uniRegistrationStatus: 'Not Registered',
  annualHouseholdIncome: '600000',
  samurdhiRecipient: 'No',
  siblingsStudying: '1',
  preferredFieldOfStudy: 'Arts',
  preferredFieldOther: '',
};

// Loan Form Initial State (prefilled for demo, still editable)
const loanInitialState = {
  alYear: '2024',
  generalTestScore: '80',
  alQualification: 'passedAll3',
  zScore: '1.2000',
  targetInstituteType: 'Private University',
  loanAmountRequired: '800000',
  guarantorAvailability: '1 Guarantor',
  employmentStatus: 'Unemployed',
  preferredFieldOfStudy: 'Management',
  preferredFieldOther: '',
};

// Scholarship Form Validation
function useScholarshipValidation(values) {
  return useMemo(() => {
    const errors = {};
    if (!values.alStream.trim()) errors.alStream = 'Required';
    if (values.alStream === 'Other' && !values.alStreamOther.trim()) {
      errors.alStreamOther = 'Please specify';
    }
    if (!values.zScore || Number(values.zScore) <= 0) {
      errors.zScore = 'Enter a valid Z-Score';
    }
    if (!values.district.trim()) errors.district = 'Required';
    if (!values.annualHouseholdIncome || Number(values.annualHouseholdIncome) < 0) {
      errors.annualHouseholdIncome = 'Enter annual household income';
    }
    return errors;
  }, [values]);
}

// Loan Form Validation
function useLoanValidation(values) {
  return useMemo(() => {
    const errors = {};
    if (!values.alYear.trim()) errors.alYear = 'Required';
    if (!values.generalTestScore || Number(values.generalTestScore) < 0) {
      errors.generalTestScore = 'Enter General Test Score';
    }
    if (!values.guarantorAvailability.trim()) {
      errors.guarantorAvailability = 'Required';
    }
    if (!values.loanAmountRequired || Number(values.loanAmountRequired) <= 0) {
      errors.loanAmountRequired = 'Enter a valid loan amount';
    }
    return errors;
  }, [values]);
}

export default function StudentProfileForm({ 
  onSubmit, 
  isLoading, 
  submitLabel = 'Find Matches',
  matchType = 'scholarship'
}) {
  const isScholarship = matchType === 'scholarship';

  const [scholarshipValues, setScholarshipValues] = useState(scholarshipInitialState);
  const [loanValues, setLoanValues] = useState(loanInitialState);
  const [touched, setTouched] = useState({});

  const scholarshipErrors = useScholarshipValidation(scholarshipValues);
  const loanErrors = useLoanValidation(loanValues);

  const errors = isScholarship ? scholarshipErrors : loanErrors;
  const values = isScholarship ? scholarshipValues : loanValues;

  const handleChange = (event) => {
    const { name, value } = event.target;
    
    if (isScholarship) {
      setScholarshipValues((prev) => ({ ...prev, [name]: value }));
    } else {
      setLoanValues((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleBlur = (event) => {
    const { name } = event.target;
    setTouched((prev) => ({ ...prev, [name]: true }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setTouched(
      Object.keys(values).reduce((acc, key) => ({ ...acc, [key]: true }), {})
    );
    if (Object.keys(errors).length) return;

    let formatted;

    if (isScholarship) {
      // Normalize scholarship form data for backend
      formatted = {
        education_level: 'undergraduate', // Default for A/L students
        field_of_study:
          scholarshipValues.preferredFieldOfStudy === 'Other'
            ? scholarshipValues.preferredFieldOther
            : scholarshipValues.preferredFieldOfStudy === 'All Fields'
            ? ''
            : scholarshipValues.preferredFieldOfStudy,
        family_income: Number(scholarshipValues.annualHouseholdIncome),
        district: scholarshipValues.district,
        age: 18, // Default age for A/L students
        z_score: Number(scholarshipValues.zScore),
        al_stream: scholarshipValues.alStream === 'Other' 
          ? scholarshipValues.alStreamOther 
          : scholarshipValues.alStream,
        english_result: scholarshipValues.englishResult,
        uni_registration_status: scholarshipValues.uniRegistrationStatus,
        samurdhi_recipient: scholarshipValues.samurdhiRecipient === 'Yes',
        siblings_studying: Number(scholarshipValues.siblingsStudying) || 0,
        study_interests:
          scholarshipValues.preferredFieldOfStudy && scholarshipValues.preferredFieldOfStudy !== 'All Fields'
            ? `${scholarshipValues.preferredFieldOfStudy} scholarship`
            : 'Scholarships for any field',
        desired_program_type: 'scholarship',
        skills: [],
      };
    } else {
      // Normalize loan form data for backend
      formatted = {
        education_level: 'undergraduate',
        field_of_study:
          loanValues.preferredFieldOfStudy === 'Other'
            ? loanValues.preferredFieldOther
            : loanValues.preferredFieldOfStudy === 'All Fields'
            ? ''
            : loanValues.preferredFieldOfStudy,
        family_income: 0, // Not collected in loan form
        district: '', // Not collected in loan form
        age: 18,
        z_score: Number(loanValues.zScore) || 0,
        al_year: loanValues.alYear,
        general_test_score: Number(loanValues.generalTestScore),
        al_passed_all_3: loanValues.alQualification === 'passedAll3',
        al_at_least_s: loanValues.alQualification === 'atLeastS',
        target_institute_type: loanValues.targetInstituteType,
        loan_amount_required: Number(loanValues.loanAmountRequired),
        guarantor_availability: loanValues.guarantorAvailability,
        employment_status: loanValues.employmentStatus,
        study_interests:
          loanValues.preferredFieldOfStudy && loanValues.preferredFieldOfStudy !== 'All Fields'
            ? `Loan for ${loanValues.preferredFieldOfStudy} at ${loanValues.targetInstituteType}`
            : `Loan for ${loanValues.targetInstituteType || 'higher education'}`,
        desired_program_type: 'loan',
        skills: [],
      };
    }

    onSubmit?.(formatted);
  };

  const renderError = (field) =>
    touched[field] && errors[field] ? (
      <span className="matcher-form__error">{errors[field]}</span>
    ) : null;

  // Scholarship Form
  if (isScholarship) {
    return (
      <form className="matcher-form" onSubmit={handleSubmit} noValidate>
        <div className="matcher-form__section">
          <h3 className="matcher-form__section-title">Academic Profile (G.C.E. A/L)</h3>
          <div className="matcher-form__grid">
            <label>
              A/L Stream*
              <select
                name="alStream"
                value={scholarshipValues.alStream}
                onChange={handleChange}
                onBlur={handleBlur}
              >
                <option value="">Select Stream</option>
                {AL_STREAMS.map((stream) => (
                  <option key={stream} value={stream}>
                    {stream}
                  </option>
                ))}
              </select>
              {renderError('alStream')}
            </label>

            {scholarshipValues.alStream === 'Other' && (
              <label className="matcher-form__full">
                Specify A/L Stream*
                <input
                  type="text"
                  name="alStreamOther"
                  value={scholarshipValues.alStreamOther}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  placeholder="Enter your A/L stream"
                />
                {renderError('alStreamOther')}
              </label>
            )}

            <label>
              Z-Score*
              <input
                type="number"
                step="0.0001"
                name="zScore"
                value={scholarshipValues.zScore}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="e.g., 1.4502"
              />
              {renderError('zScore')}
            </label>

            <label>
              District*
              <select
                name="district"
                value={scholarshipValues.district}
                onChange={handleChange}
                onBlur={handleBlur}
              >
                <option value="">Select District</option>
                {SRI_LANKAN_DISTRICTS.map((district) => (
                  <option key={district} value={district}>
                    {district}
                  </option>
                ))}
              </select>
              {renderError('district')}
            </label>

            <label>
              English Result
              <select
                name="englishResult"
                value={scholarshipValues.englishResult}
                onChange={handleChange}
                onBlur={handleBlur}
              >
                <option value="">Select Grade</option>
                {ENGLISH_RESULTS.map((grade) => (
                  <option key={grade} value={grade}>
                    {grade}
                  </option>
                ))}
              </select>
            </label>

            <label>
              University Registration Status
              <select
                name="uniRegistrationStatus"
                value={scholarshipValues.uniRegistrationStatus}
                onChange={handleChange}
                onBlur={handleBlur}
              >
                <option value="">Select Status</option>
                {UNI_REGISTRATION_STATUS.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>

        <div className="matcher-form__section">
          <h3 className="matcher-form__section-title">Financial Background</h3>
          <div className="matcher-form__grid">
            <label>
              Annual Household Income (LKR)*
              <input
                type="number"
                min="0"
                name="annualHouseholdIncome"
                value={scholarshipValues.annualHouseholdIncome}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="e.g., 500000"
              />
              {renderError('annualHouseholdIncome')}
            </label>

            <label>
              Samurdhi Recipient
              <select
                name="samurdhiRecipient"
                value={scholarshipValues.samurdhiRecipient}
                onChange={handleChange}
                onBlur={handleBlur}
              >
                <option value="">Select</option>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
              </select>
            </label>

            <label>
              Number of Siblings Studying or Under 18
              <input
                type="number"
                min="0"
                name="siblingsStudying"
                value={scholarshipValues.siblingsStudying}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="0"
              />
            </label>
          </div>
        </div>

        <div className="matcher-form__section">
          <h3 className="matcher-form__section-title">Target Preferences</h3>
          <div className="matcher-form__grid">
            <label>
              Preferred Field of Study
              <select
                name="preferredFieldOfStudy"
                value={scholarshipValues.preferredFieldOfStudy}
                onChange={handleChange}
                onBlur={handleBlur}
              >
                <option value="">Select Field</option>
                {PREFERRED_FIELDS.map((field) => (
                  <option key={field} value={field}>
                    {field}
                  </option>
                ))}
              </select>
            </label>

            {scholarshipValues.preferredFieldOfStudy === 'Other' && (
              <label className="matcher-form__full">
                Specify Field of Study
                <input
                  type="text"
                  name="preferredFieldOther"
                  value={scholarshipValues.preferredFieldOther}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  placeholder="Enter your field of study"
                />
              </label>
            )}
          </div>
        </div>

        <button type="submit" className="matcher-form__submit" disabled={isLoading}>
          {isLoading ? 'Finding matches…' : submitLabel}
        </button>
      </form>
    );
  }

  // Loan Form
  return (
    <form className="matcher-form" onSubmit={handleSubmit} noValidate>
      <div className="matcher-form__section">
        <h3 className="matcher-form__section-title">Qualifying Criteria (IFSLS & Bank Loans)</h3>
        <div className="matcher-form__grid">
          <label>
            G.C.E. A/L Year*
            <select
              name="alYear"
              value={loanValues.alYear}
              onChange={handleChange}
              onBlur={handleBlur}
            >
              <option value="">Select Year</option>
              {AL_YEARS.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
            {renderError('alYear')}
          </label>

          <label>
            General Test Score*
            <input
              type="number"
              min="0"
              name="generalTestScore"
              value={loanValues.generalTestScore}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Enter score"
            />
            {renderError('generalTestScore')}
          </label>

          <label className="matcher-form__full">
            <div className="matcher-form__radio-group">
              <span className="matcher-form__radio-label-title">A/L Subject Results</span>
              <div className="matcher-form__radio-options">
                <label className="matcher-form__radio-label">
                  <input
                    type="radio"
                    name="alQualification"
                    value="passedAll3"
                    checked={loanValues.alQualification === 'passedAll3'}
                    onChange={handleChange}
                    onBlur={handleBlur}
                  />
                  <span>Passed all 3 subjects</span>
                </label>
                <label className="matcher-form__radio-label">
                  <input
                    type="radio"
                    name="alQualification"
                    value="atLeastS"
                    checked={loanValues.alQualification === 'atLeastS'}
                    onChange={handleChange}
                    onBlur={handleBlur}
                  />
                  <span>At least "S" passes</span>
                </label>
              </div>
            </div>
          </label>

          <label>
            Z-Score
            <input
              type="number"
              step="0.0001"
              name="zScore"
              value={loanValues.zScore}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="e.g., 1.4502"
            />
          </label>
        </div>
      </div>

      <div className="matcher-form__section">
        <h3 className="matcher-form__section-title">Loan Requirements</h3>
        <div className="matcher-form__grid">
          <label>
            Target Institute Type
            <select
              name="targetInstituteType"
              value={loanValues.targetInstituteType}
              onChange={handleChange}
              onBlur={handleBlur}
            >
              <option value="">Select Type</option>
              {INSTITUTE_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </label>

          <label>
            Loan Amount Required (LKR)*
            <input
              type="number"
              min="0"
              name="loanAmountRequired"
              value={loanValues.loanAmountRequired}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="e.g., 500000"
            />
            {renderError('loanAmountRequired')}
          </label>

          <label>
            Guarantor Availability*
            <select
              name="guarantorAvailability"
              value={loanValues.guarantorAvailability}
              onChange={handleChange}
              onBlur={handleBlur}
            >
              <option value="">Select</option>
              {GUARANTOR_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
            {renderError('guarantorAvailability')}
          </label>

          <label>
            Employment Status
            <select
              name="employmentStatus"
              value={loanValues.employmentStatus}
              onChange={handleChange}
              onBlur={handleBlur}
            >
              <option value="">Select Status</option>
              {EMPLOYMENT_STATUS.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div className="matcher-form__section">
        <h3 className="matcher-form__section-title">Target Preferences</h3>
        <div className="matcher-form__grid">
          <label>
            Preferred Field of Study
            <select
              name="preferredFieldOfStudy"
              value={loanValues.preferredFieldOfStudy}
              onChange={handleChange}
              onBlur={handleBlur}
            >
              <option value="">Select Field</option>
              {PREFERRED_FIELDS.map((field) => (
                <option key={field} value={field}>
                  {field}
                </option>
              ))}
            </select>
          </label>

          {loanValues.preferredFieldOfStudy === 'Other' && (
            <label className="matcher-form__full">
              Specify Field of Study
              <input
                type="text"
                name="preferredFieldOther"
                value={loanValues.preferredFieldOther}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="Enter your field of study"
              />
            </label>
          )}
        </div>
      </div>

      <button type="submit" className="matcher-form__submit" disabled={isLoading}>
        {isLoading ? 'Finding matches…' : submitLabel}
      </button>
    </form>
  );
}
