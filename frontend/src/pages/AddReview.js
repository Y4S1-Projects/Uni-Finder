import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import Swal from 'sweetalert2';
import 'bootstrap/dist/css/bootstrap.min.css';

const Addreview = () => {
  const fileRef1 = useRef(null);
  const navigate = useNavigate();
  const { currentUser } = useSelector((state) => state.user);

  const [formData, setFormData] = useState({
    userId: currentUser?._id || '',
    place: '',
    review: '',
  });

  const [formErrors, setFormErrors] = useState({});
  const [error, setError] = useState('');

  const validateForm = () => {
    const errors = {};

    if (!formData.place) {
      errors.place = 'Please select a place.';
    }

    if (!formData.review.trim()) {
      errors.review = 'Please enter a review.';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!validateForm()) return;

    try {
      const res = await fetch('http://localhost:3000/api/auth/add_reviews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.message || 'Failed to submit review');
      }

      Swal.fire({
        icon: 'success',
        title: 'Success',
        text: 'Review submitted successfully!',
      });

    navigate('/all');
    } catch (err) {
      setError('Something went wrong!');
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: err.message || 'Something went wrong.',
      });
    }
  };

  return (
    <div className="container mt-5">
      <div className="card shadow p-4">
        <h2 className="text-center mb-4">Add Review</h2>

        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Place</label>
            <select
              className={`form-select ${formErrors.place && 'is-invalid'}`}
              value={formData.place}
              onChange={(e) => setFormData({ ...formData, place: e.target.value })}
            >
              <option value="">-- Select Place --</option>
              <option value="place 1">Place 1</option>
              <option value="place 10">Place 12</option>
            </select>
            {formErrors.place && <div className="invalid-feedback">{formErrors.place}</div>}
          </div>

          <div className="mb-3">
  <label className="form-label">Review</label>
  <textarea
    className={`form-control ${formErrors.review && 'is-invalid'}`}
    value={formData.review}
    onChange={(e) => setFormData({ ...formData, review: e.target.value })}
    placeholder="Enter your review"
    rows="4"
  ></textarea>
  {formErrors.review && <div className="invalid-feedback">{formErrors.review}</div>}
</div>


          <button type="submit" className="btn btn-primary w-100">
            Submit
          </button>
        </form>
      </div>
    </div>
  );
};

export default Addreview;
