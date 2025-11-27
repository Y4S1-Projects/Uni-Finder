import { useMemo, useState } from 'react';

const initialState = {
  educationLevel: '',
  fieldOfStudy: '',
  familyIncome: '',
  district: '',
  age: '',
  studyInterests: '',
  desiredProgramType: '',
  skills: '',
};

function useValidation(values) {
  return useMemo(() => {
    const errors = {};
    if (!values.educationLevel.trim()) errors.educationLevel = 'Required';
    if (!values.fieldOfStudy.trim()) errors.fieldOfStudy = 'Required';
    if (!values.district.trim()) errors.district = 'Required';
    if (!values.studyInterests.trim()) errors.studyInterests = 'Required';
    if (!values.age || Number(values.age) <= 0) errors.age = 'Enter a valid age';
    if (!values.familyIncome || Number(values.familyIncome) < 0) {
      errors.familyIncome = 'Enter family income (0 if unknown)';
    }
    return errors;
  }, [values]);
}

export default function StudentProfileForm({ onSubmit, isLoading }) {
  const [values, setValues] = useState(initialState);
  const [touched, setTouched] = useState({});
  const errors = useValidation(values);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setValues((prev) => ({ ...prev, [name]: value }));
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

    const formatted = {
      education_level: values.educationLevel,
      field_of_study: values.fieldOfStudy,
      family_income: Number(values.familyIncome),
      district: values.district,
      age: Number(values.age),
      study_interests: values.studyInterests,
      desired_program_type: values.desiredProgramType,
      skills: values.skills
        ? values.skills.split(',').map((skill) => skill.trim())
        : [],
    };
    onSubmit?.(formatted);
  };

  const renderError = (field) =>
    touched[field] && errors[field] ? (
      <span className="matcher-form__error">{errors[field]}</span>
    ) : null;

  return (
    <form className="matcher-form" onSubmit={handleSubmit} noValidate>
      <div className="matcher-form__grid">
        <label>
          Education Level*
          <input
            type="text"
            name="educationLevel"
            value={values.educationLevel}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="Undergraduate / Postgraduate"
          />
          {renderError('educationLevel')}
        </label>

        <label>
          Field of Study*
          <input
            type="text"
            name="fieldOfStudy"
            value={values.fieldOfStudy}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="Computer Science, Finance…"
          />
          {renderError('fieldOfStudy')}
        </label>

        <label>
          District / Region*
          <input
            type="text"
            name="district"
            value={values.district}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="Colombo"
          />
          {renderError('district')}
        </label>

        <label>
          Age*
          <input
            type="number"
            min="0"
            name="age"
            value={values.age}
            onChange={handleChange}
            onBlur={handleBlur}
          />
          {renderError('age')}
        </label>

        <label>
          Family Income (LKR)*
          <input
            type="number"
            min="0"
            name="familyIncome"
            value={values.familyIncome}
            onChange={handleChange}
            onBlur={handleBlur}
          />
          {renderError('familyIncome')}
        </label>

        <label className="matcher-form__full">
          Study Interests / Goals*
          <textarea
            name="studyInterests"
            rows="3"
            value={values.studyInterests}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="E.g., interest in AI, need stipend support…"
          />
          {renderError('studyInterests')}
        </label>

        <label>
          Desired Program Type
          <input
            type="text"
            name="desiredProgramType"
            value={values.desiredProgramType}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="Merit-based, need-based, loan"
          />
        </label>

        <label className="matcher-form__full">
          Skills (comma separated)
          <input
            type="text"
            name="skills"
            value={values.skills}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="Leadership, research, volunteering"
          />
        </label>
      </div>

      <button type="submit" className="matcher-form__submit" disabled={isLoading}>
        {isLoading ? 'Finding matches…' : 'Find Matches'}
      </button>
    </form>
  );
}


