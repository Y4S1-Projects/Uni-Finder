import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner, ProgressBar } from 'react-bootstrap';
import { useSelector } from 'react-redux';
import './BudgetOptimizerNew.css';

const BudgetOptimizerNew = () => {
  // Get current user from Redux store
  const { currentUser } = useSelector((state) => state.user);
  
  // Multi-step form state
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);

  // Form data state
  const [formData, setFormData] = useState({
    // Account Information
    email: currentUser?.email || '',
    password: '',
    full_name: currentUser?.username || '',
    phone: '',
    university: 'SLIIT',
    
    // Academic Profile
    year_of_study: 'Second Year',
    field_of_study: 'IT',
    district: 'Colombo',
    
    // Financial Basics
    monthly_income: 30000,
    accommodation_type: 'Rented Room',
    rent: 10000,
    
    // Food Preferences
    food_type: 'Mixed',
    meals_per_day: '3 meals',
    diet_type: 'Non-Vegetarian',
    cooking_frequency: 'Most days',
    cooking_percentage: 60,
    
    // Transport Details
    distance_uni_accommodation: 5,
    distance_home_uni: 80,
    transport_method: 'Bus',
    days_per_week: '5 days',
    home_visit_frequency: 'Monthly',
    transport_method_home: 'Bus',
    
    // Additional Expenses
    internet: 1500,
    study_materials: 2000,
    entertainment: 2000,
    utilities: 1000,
    healthcare: 1000,
    other: 500
  });

  const backendUrl = 'http://127.0.0.1:5002';

  const districts = [
    'Colombo', 'Gampaha', 'Kalutara', 'Kandy', 'Matale', 'Nuwara Eliya',
    'Galle', 'Matara', 'Hambantota', 'Jaffna', 'Kurunegala', 'Anuradhapura',
    'Ratnapura', 'Batticaloa', 'Trincomalee', 'Badulla'
  ];

  const universities = [
    'SLIIT', 'University of Colombo', 'University of Moratuwa', 
    'University of Kelaniya', 'University of Peradeniya', 'NSBM Green University',
    'IIT Campus', 'Other'
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: ['monthly_income', 'rent', 'distance_uni_accommodation', 'distance_home_uni', 
               'cooking_percentage', 'internet', 'study_materials', 'entertainment', 
               'utilities', 'healthcare', 'other'].includes(name) 
        ? parseInt(value) || 0 
        : value
    }));
  };

  const nextStep = () => {
    setCurrentStep(prev => Math.min(prev + 1, 7));
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const submitAnalysis = async () => {
    setLoading(true);
    setError(null);

    try {
      // Include user information if logged in
      const requestData = {
        ...formData,
        userId: currentUser?._id || null,
        username: currentUser?.username || formData.full_name,
        email: currentUser?.email || formData.email
      };

      // Step 1: Get ML analysis from Flask
      const response = await fetch(`${backendUrl}/api/budget/complete-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      if (response.ok) {
        const result = await response.json();
        setAnalysisResult(result);
        
        // Step 2: Save to MongoDB directly via Node.js API (like SignUp does)
        try {
          const budgetSaveData = {
            // User info
            userId: currentUser?._id || null,
            username: currentUser?.username || formData.full_name,
            email: currentUser?.email || formData.email,
            
            // Personal Information
            monthly_income: formData.monthly_income,
            year_of_study: formData.year_of_study,
            field_of_study: formData.field_of_study,
            university: formData.university,
            district: formData.district,
            accommodation_type: formData.accommodation_type,
            
            // Budget Inputs
            rent: formData.rent,
            internet: formData.internet,
            study_materials: formData.study_materials,
            entertainment: formData.entertainment,
            utilities: formData.utilities,
            healthcare: formData.healthcare,
            other: formData.other,
            
            // Food Details
            food_type: formData.food_type,
            meals_per_day: formData.meals_per_day,
            diet_type: formData.diet_type,
            cooking_frequency: formData.cooking_frequency,
            cooking_percentage: formData.cooking_percentage,
            
            // Transport Details
            distance_uni_accommodation: formData.distance_uni_accommodation,
            distance_home_uni: formData.distance_home_uni,
            transport_method: formData.transport_method,
            transport_method_home: formData.transport_method_home,
            days_per_week: formData.days_per_week,
            home_visit_frequency: formData.home_visit_frequency,
            
            // Calculated Budgets from Flask response
            food_budget: result.calculated_budgets?.food || {},
            transport_budget: result.calculated_budgets?.transport || {},
            
            // ML Prediction Results
            predicted_budget: result.ml_prediction?.predicted_budget || 0,
            ml_confidence: (result.ml_prediction?.confidence || 0) * 100,
            risk_level: result.risk_assessment?.risk_level || 'Medium Risk',
            risk_probability: (result.risk_assessment?.risk_probability || 0) * 100,
            
            // Financial Summary
            total_expenses: result.financial_summary?.total_expenses || 0,
            calculated_savings: result.financial_summary?.monthly_savings || 0,
            savings_rate: result.financial_summary?.savings_rate || 0,
            
            // Recommendations
            recommendations: result.recommendation?.key_recommendations || [],
            actionable_steps: result.recommendation?.action_steps || [],
            
            // Expense Breakdown
            expense_breakdown: result.expense_breakdown || {},
            
            // Metadata
            analysis_date: new Date().toISOString(),
            status: 'active'
          };

          // Save to MongoDB via Node.js API (port 3000) - Same as SignUp
          const saveResponse = await fetch('http://localhost:3000/api/budget/save', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(budgetSaveData)
          });

          if (saveResponse.ok) {
            const saveResult = await saveResponse.json();
            console.log('✅ Budget prediction saved to MongoDB:', saveResult.predictionId);
          } else {
            console.warn('⚠️ Failed to save to MongoDB, but showing results anyway');
          }
        } catch (saveError) {
          console.warn('⚠️ MongoDB save error:', saveError.message);
          // Continue anyway - user still gets analysis results
        }
        
        setCurrentStep(7); // Move to results step
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to analyze budget');
      }
    } catch (error) {
      setError('Network error. Please check if the backend server is running on port 5002.');
    } finally {
      setLoading(false);
    }
  };

  const renderStepIndicator = () => {
    const steps = [
      'Account', 'Academic', 'Financial', 'Food', 'Transport', 'Additional', 'Results'
    ];

    return (
      <div className="step-indicator mb-4">
        <ProgressBar now={(currentStep / 7) * 100} className="mb-3" />
        <div className="d-flex justify-content-between">
          {steps.map((step, index) => (
            <div
              key={index}
              className={`step-item ${currentStep === index + 1 ? 'active' : ''} ${currentStep > index + 1 ? 'completed' : ''}`}
            >
              <div className="step-number">{index + 1}</div>
              <div className="step-label">{step}</div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderStep1 = () => (
    <Card className="shadow-lg border-0">
      <Card.Header className="bg-gradient-primary text-white">
        <h4 className="mb-0">📝 Step 1: Account Information</h4>
      </Card.Header>
      <Card.Body className="p-4">
        <Form>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label><strong>Email Address *</strong></Form.Label>
                <Form.Control
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="student@email.com"
                  required
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label><strong>Password *</strong></Form.Label>
                <Form.Control
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="Min 8 characters"
                  required
                />
              </Form.Group>
            </Col>
          </Row>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label><strong>Full Name *</strong></Form.Label>
                <Form.Control
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  placeholder="Your full name"
                  required
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label><strong>Phone Number *</strong></Form.Label>
                <Form.Control
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="+94 77 123 4567"
                  required
                />
              </Form.Group>
            </Col>
          </Row>

          <Form.Group className="mb-3">
            <Form.Label><strong>University *</strong></Form.Label>
            <Form.Select name="university" value={formData.university} onChange={handleInputChange}>
              {universities.map(uni => (
                <option key={uni} value={uni}>{uni}</option>
              ))}
            </Form.Select>
          </Form.Group>
        </Form>
      </Card.Body>
    </Card>
  );

  const renderStep2 = () => (
    <Card className="shadow-lg border-0">
      <Card.Header className="bg-gradient-primary text-white">
        <h4 className="mb-0">🎓 Step 2: Academic Profile</h4>
      </Card.Header>
      <Card.Body className="p-4">
        <Form>
          <Form.Group className="mb-3">
            <Form.Label><strong>Year of Study *</strong></Form.Label>
            <Form.Select name="year_of_study" value={formData.year_of_study} onChange={handleInputChange}>
              <option value="First Year">First Year</option>
              <option value="Second Year">Second Year</option>
              <option value="Third Year">Third Year</option>
              <option value="Fourth Year">Fourth Year</option>
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label><strong>Field of Study *</strong></Form.Label>
            <Form.Select name="field_of_study" value={formData.field_of_study} onChange={handleInputChange}>
              <option value="Engineering">Engineering</option>
              <option value="IT">IT/Computer Science</option>
              <option value="Business">Business</option>
              <option value="Medicine">Medicine</option>
              <option value="Arts">Arts</option>
              <option value="Science">Science</option>
              <option value="Other">Other</option>
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label><strong>Current District *</strong></Form.Label>
            <Form.Select name="district" value={formData.district} onChange={handleInputChange}>
              {districts.map(dist => (
                <option key={dist} value={dist}>{dist}</option>
              ))}
            </Form.Select>
          </Form.Group>
        </Form>
      </Card.Body>
    </Card>
  );

  const renderStep3 = () => (
    <Card className="shadow-lg border-0">
      <Card.Header className="bg-gradient-primary text-white">
        <h4 className="mb-0">💰 Step 3: Financial Basics</h4>
      </Card.Header>
      <Card.Body className="p-4">
        <Form>
          <Form.Group className="mb-3">
            <Form.Label><strong>Monthly Income (LKR) *</strong></Form.Label>
            <Form.Control
              type="number"
              name="monthly_income"
              value={formData.monthly_income}
              onChange={handleInputChange}
              required
            />
            <Form.Text className="text-muted">
              Total money you receive monthly (allowance, scholarship, part-time job)
            </Form.Text>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label><strong>Accommodation Type *</strong></Form.Label>
            <Form.Select name="accommodation_type" value={formData.accommodation_type} onChange={handleInputChange}>
              <option value="University Hostel">University Hostel</option>
              <option value="Rented Room">Rented Room/Apartment</option>
              <option value="Living with Family">Living with Family (No rent)</option>
              <option value="Boarding">Boarding House</option>
              <option value="Other">Other</option>
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label><strong>Monthly Rent (LKR) *</strong></Form.Label>
            <Form.Control
              type="number"
              name="rent"
              value={formData.rent}
              onChange={handleInputChange}
              required
            />
            <Form.Text className="text-muted">
              Enter 0 if living with family or accommodation is free
            </Form.Text>
          </Form.Group>
        </Form>
      </Card.Body>
    </Card>
  );

  const renderStep4 = () => (
    <Card className="shadow-lg border-0">
      <Card.Header className="bg-gradient-primary text-white">
        <h4 className="mb-0">🍽️ Step 4: Food Preferences</h4>
      </Card.Header>
      <Card.Body className="p-4">
        <Form>
          <Form.Group className="mb-3">
            <Form.Label><strong>Food Type Preference *</strong></Form.Label>
            <Form.Select name="food_type" value={formData.food_type} onChange={handleInputChange}>
              <option value="Home Cooked">Home Cooked (I cook myself)</option>
              <option value="Mixed">Mixed (Cook + Order/Eat out sometimes)</option>
              <option value="Food Delivery">Food Delivery (Uber Eats, PickMe Food)</option>
              <option value="Mostly Canteen/Restaurants">Mostly Canteen/Restaurants</option>
              <option value="Full Meal Plan">Full Meal Plan (Hostel/Boarding included)</option>
            </Form.Select>
          </Form.Group>

          {formData.food_type === 'Mixed' && (
            <Form.Group className="mb-3">
              <Form.Label><strong>Cooking vs Ordering Split</strong></Form.Label>
              <div className="d-flex align-items-center gap-3">
                <span>Cook: {formData.cooking_percentage}%</span>
                <Form.Range
                  name="cooking_percentage"
                  value={formData.cooking_percentage}
                  onChange={handleInputChange}
                  min="0"
                  max="100"
                />
                <span>Order: {100 - formData.cooking_percentage}%</span>
              </div>
            </Form.Group>
          )}

          <Form.Group className="mb-3">
            <Form.Label><strong>Meals Per Day *</strong></Form.Label>
            <Form.Select name="meals_per_day" value={formData.meals_per_day} onChange={handleInputChange}>
              <option value="2 meals">2 meals</option>
              <option value="3 meals">3 meals</option>
              <option value="3 meals + snacks">3 meals + snacks</option>
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label><strong>Diet Type *</strong></Form.Label>
            <Form.Select name="diet_type" value={formData.diet_type} onChange={handleInputChange}>
              <option value="Vegetarian">Vegetarian</option>
              <option value="Non-Vegetarian">Non-Vegetarian</option>
              <option value="Vegan">Vegan</option>
            </Form.Select>
          </Form.Group>

          {(formData.food_type === 'Home Cooked' || formData.food_type === 'Mixed') && (
            <Form.Group className="mb-3">
              <Form.Label><strong>How often do you cook?</strong></Form.Label>
              <Form.Select name="cooking_frequency" value={formData.cooking_frequency} onChange={handleInputChange}>
                <option value="Every day">Every day</option>
                <option value="Most days">Most days</option>
                <option value="Sometimes">Sometimes</option>
                <option value="Rarely">Rarely</option>
                <option value="Never">Never</option>
              </Form.Select>
            </Form.Group>
          )}
        </Form>
      </Card.Body>
    </Card>
  );

  const renderStep5 = () => (
    <Card className="shadow-lg border-0">
      <Card.Header className="bg-gradient-primary text-white">
        <h4 className="mb-0">🚌 Step 5: Transport Details</h4>
      </Card.Header>
      <Card.Body className="p-4">
        <Form>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label><strong>Distance: University to Accommodation (km)</strong></Form.Label>
                <Form.Control
                  type="number"
                  name="distance_uni_accommodation"
                  value={formData.distance_uni_accommodation}
                  onChange={handleInputChange}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label><strong>Distance: Home to University (km)</strong></Form.Label>
                <Form.Control
                  type="number"
                  name="distance_home_uni"
                  value={formData.distance_home_uni}
                  onChange={handleInputChange}
                />
              </Form.Group>
            </Col>
          </Row>

          <Form.Group className="mb-3">
            <Form.Label><strong>Primary Transport Method *</strong></Form.Label>
            <Form.Select name="transport_method" value={formData.transport_method} onChange={handleInputChange}>
              <option value="Walking">Walking</option>
              <option value="Bicycle">Bicycle</option>
              <option value="Bus">Bus</option>
              <option value="Train">Train</option>
              <option value="Tuk-Tuk">Tuk-Tuk/Three-Wheeler</option>
              <option value="Ride-share">Ride-share (Uber/PickMe)</option>
              <option value="Personal Vehicle">Personal Vehicle</option>
              <option value="University Transport">University Transport</option>
              <option value="Mixed">Mixed</option>
            </Form.Select>
          </Form.Group>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label><strong>Days per Week at University</strong></Form.Label>
                <Form.Select name="days_per_week" value={formData.days_per_week} onChange={handleInputChange}>
                  <option value="1 day">1 day</option>
                  <option value="2 days">2 days</option>
                  <option value="3 days">3 days</option>
                  <option value="4 days">4 days</option>
                  <option value="5 days">5 days</option>
                  <option value="6 days">6 days</option>
                  <option value="7 days">7 days</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label><strong>Home Visit Frequency</strong></Form.Label>
                <Form.Select name="home_visit_frequency" value={formData.home_visit_frequency} onChange={handleInputChange}>
                  <option value="Daily">Daily</option>
                  <option value="Weekly">Weekly</option>
                  <option value="Bi-weekly">Bi-weekly</option>
                  <option value="Monthly">Monthly</option>
                  <option value="Once per semester">Once per semester</option>
                  <option value="Rarely/Never">Rarely/Never</option>
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>

          <Form.Group className="mb-3">
            <Form.Label><strong>Transport Method for Home Visits</strong></Form.Label>
            <Form.Select name="transport_method_home" value={formData.transport_method_home} onChange={handleInputChange}>
              <option value="Bus">Bus</option>
              <option value="Train">Train</option>
              <option value="Personal Vehicle">Personal Vehicle</option>
              <option value="Ride-share">Ride-share</option>
            </Form.Select>
          </Form.Group>
        </Form>
      </Card.Body>
    </Card>
  );

  const renderStep6 = () => (
    <Card className="shadow-lg border-0">
      <Card.Header className="bg-gradient-primary text-white">
        <h4 className="mb-0">📊 Step 6: Additional Expenses (Optional)</h4>
      </Card.Header>
      <Card.Body className="p-4">
        <Form>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label><strong>Internet & Mobile (LKR/month)</strong></Form.Label>
                <Form.Control
                  type="number"
                  name="internet"
                  value={formData.internet}
                  onChange={handleInputChange}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label><strong>Study Materials (LKR/month)</strong></Form.Label>
                <Form.Control
                  type="number"
                  name="study_materials"
                  value={formData.study_materials}
                  onChange={handleInputChange}
                />
              </Form.Group>
            </Col>
          </Row>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label><strong>Entertainment & Social (LKR/month)</strong></Form.Label>
                <Form.Control
                  type="number"
                  name="entertainment"
                  value={formData.entertainment}
                  onChange={handleInputChange}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label><strong>Utilities (LKR/month)</strong></Form.Label>
                <Form.Control
                  type="number"
                  name="utilities"
                  value={formData.utilities}
                  onChange={handleInputChange}
                />
              </Form.Group>
            </Col>
          </Row>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label><strong>Healthcare (LKR/month)</strong></Form.Label>
                <Form.Control
                  type="number"
                  name="healthcare"
                  value={formData.healthcare}
                  onChange={handleInputChange}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label><strong>Other Expenses (LKR/month)</strong></Form.Label>
                <Form.Control
                  type="number"
                  name="other"
                  value={formData.other}
                  onChange={handleInputChange}
                />
              </Form.Group>
            </Col>
          </Row>
        </Form>
      </Card.Body>
    </Card>
  );

  const renderStep7 = () => {
    if (!analysisResult) {
      return (
        <Card className="shadow-lg border-0">
          <Card.Body className="p-5 text-center">
            <h4>Ready to analyze your budget!</h4>
            <p>Click "Analyze Budget" to get your personalized financial insights.</p>
          </Card.Body>
        </Card>
      );
    }

    const { financial_summary, expense_breakdown, calculated_budgets, risk_assessment, recommendation } = analysisResult;

    return (
      <div>
        {/* Financial Summary */}
        <Card className="shadow-lg border-0 mb-4">
          <Card.Header className="bg-gradient-success text-white">
            <h4 className="mb-0">💰 Financial Summary</h4>
          </Card.Header>
          <Card.Body className="p-4">
            <Row>
              <Col md={3} className="text-center mb-3">
                <div className="summary-box">
                  <div className="summary-label">Monthly Income</div>
                  <div className="summary-value text-primary">
                    LKR {financial_summary.monthly_income.toLocaleString()}
                  </div>
                </div>
              </Col>
              <Col md={3} className="text-center mb-3">
                <div className="summary-box">
                  <div className="summary-label">Total Expenses</div>
                  <div className="summary-value text-danger">
                    LKR {financial_summary.total_expenses.toLocaleString()}
                  </div>
                </div>
              </Col>
              <Col md={3} className="text-center mb-3">
                <div className="summary-box">
                  <div className="summary-label">Monthly Savings</div>
                  <div className={`summary-value ${financial_summary.monthly_savings >= 0 ? 'text-success' : 'text-danger'}`}>
                    LKR {financial_summary.monthly_savings.toLocaleString()}
                  </div>
                </div>
              </Col>
              <Col md={3} className="text-center mb-3">
                <div className="summary-box">
                  <div className="summary-label">Savings Rate</div>
                  <div className={`summary-value ${financial_summary.savings_rate >= 0 ? 'text-success' : 'text-danger'}`}>
                    {financial_summary.savings_rate}%
                  </div>
                </div>
              </Col>
            </Row>
          </Card.Body>
        </Card>

        {/* Risk Assessment */}
        {risk_assessment && (
          <Alert variant={risk_assessment.risk_level === 'High Risk' ? 'danger' : 'success'} className="mb-4">
            <Alert.Heading>
              {risk_assessment.risk_level === 'High Risk' ? '⚠️ High Financial Risk Detected' : '✅ Low Financial Risk'}
            </Alert.Heading>
            <p>Risk Probability: {risk_assessment.risk_probability}%</p>
            {risk_assessment.recommendations && risk_assessment.recommendations.length > 0 && (
              <div>
                <strong>Recommendations:</strong>
                <ul className="mb-0 mt-2">
                  {risk_assessment.recommendations.map((rec, idx) => (
                    <li key={idx}>
                      <strong>{rec.category}:</strong> {rec.message}
                      {rec.potential_savings > 0 && (
                        <span className="text-success"> (Potential savings: LKR {rec.potential_savings.toLocaleString()})</span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </Alert>
        )}

        {/* AI Recommendation */}
        <Card className="shadow-lg border-0 mb-4">
          <Card.Header className="bg-gradient-info text-white">
            <h4 className="mb-0">🎯 AI Recommendation</h4>
          </Card.Header>
          <Card.Body className="p-4">
            <p className="lead mb-0">{recommendation}</p>
          </Card.Body>
        </Card>

        {/* Expense Breakdown */}
        <Card className="shadow-lg border-0 mb-4">
          <Card.Header className="bg-gradient-primary text-white">
            <h4 className="mb-0">📊 Expense Breakdown</h4>
          </Card.Header>
          <Card.Body className="p-4">
            <Row>
              <Col md={6}>
                <h5 className="mb-3">Monthly Expenses</h5>
                {Object.entries(expense_breakdown).map(([category, amount]) => {
                  if (category === 'total_expenses') return null;
                  const percentage = ((amount / expense_breakdown.total_expenses) * 100).toFixed(1);
                  return (
                    <div key={category} className="d-flex justify-content-between align-items-center py-2 border-bottom">
                      <span className="text-capitalize"><strong>{category.replace('_', ' ')}:</strong></span>
                      <span>
                        LKR {amount.toLocaleString()} 
                        <span className="text-muted ms-2">({percentage}%)</span>
                      </span>
                    </div>
                  );
                })}
                <div className="d-flex justify-content-between align-items-center py-2 mt-3">
                  <span><strong>TOTAL:</strong></span>
                  <span className="fs-5 fw-bold text-primary">
                    LKR {expense_breakdown.total_expenses.toLocaleString()}
                  </span>
                </div>
              </Col>
              <Col md={6}>
                <h5 className="mb-3">Auto-Calculated Budgets</h5>
                {calculated_budgets.food && (
                  <div className="mb-3">
                    <div className="d-flex justify-content-between align-items-center">
                      <span><strong>🍽️ Food Budget:</strong></span>
                      <span className="text-success fw-bold">
                        LKR {calculated_budgets.food.monthly_total.toLocaleString()}
                      </span>
                    </div>
                    <small className="text-muted">
                      Type: {calculated_budgets.food.food_type} | 
                      Daily: LKR {calculated_budgets.food.daily_cost.toLocaleString()}
                    </small>
                  </div>
                )}
                {calculated_budgets.transport && (
                  <div className="mb-3">
                    <div className="d-flex justify-content-between align-items-center">
                      <span><strong>🚌 Transport Budget:</strong></span>
                      <span className="text-success fw-bold">
                        LKR {calculated_budgets.transport.monthly_total.toLocaleString()}
                      </span>
                    </div>
                    <small className="text-muted">
                      Method: {calculated_budgets.transport.transport_method} | 
                      Daily: LKR {calculated_budgets.transport.daily_cost.toLocaleString()}
                    </small>
                    {calculated_budgets.transport.breakdown && (
                      <div className="mt-2">
                        <small className="text-muted d-block">
                          Daily Commute: LKR {calculated_budgets.transport.breakdown.daily_commute.toLocaleString()}
                        </small>
                        <small className="text-muted d-block">
                          Home Visits: LKR {calculated_budgets.transport.breakdown.home_visits.toLocaleString()}
                        </small>
                      </div>
                    )}
                  </div>
                )}
              </Col>
            </Row>
          </Card.Body>
        </Card>

        {/* Action Buttons */}
        <div className="text-center">
          <Button variant="outline-primary" onClick={() => setCurrentStep(1)} className="me-2">
            📝 Edit Profile
          </Button>
          <Button variant="primary" onClick={() => window.print()}>
            🖨️ Print Report
          </Button>
        </div>
      </div>
    );
  };

  const renderNavigationButtons = () => {
    if (currentStep === 7 && analysisResult) {
      return null; // No navigation buttons on results page
    }

    return (
      <div className="d-flex justify-content-between mt-4">
        <Button
          variant="outline-secondary"
          onClick={prevStep}
          disabled={currentStep === 1}
        >
          ← Previous
        </Button>

        {currentStep < 6 ? (
          <Button variant="primary" onClick={nextStep}>
            Next →
          </Button>
        ) : (
          <Button
            variant="success"
            onClick={submitAnalysis}
            disabled={loading}
          >
            {loading ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                Analyzing...
              </>
            ) : (
              '🔍 Analyze Budget'
            )}
          </Button>
        )}
      </div>
    );
  };

  return (
    <div className="budget-optimizer-new-page">
      <Container className="my-5">
        {/* Header */}
        <Row className="mb-5">
          <Col>
            <div className="text-center">
              <h1 className="display-4 gradient-text mb-3">
                🎯 AI-Powered Student Budget Optimizer
              </h1>
              <p className="lead text-muted">
                Complete your profile in 6 simple steps to get personalized budget insights
              </p>
            </div>
          </Col>
        </Row>

        {/* Step Indicator */}
        {renderStepIndicator()}

        {/* Error Display */}
        {error && (
          <Alert variant="danger" onClose={() => setError(null)} dismissible>
            <Alert.Heading>❌ Error</Alert.Heading>
            {error}
          </Alert>
        )}

        {/* Form Steps */}
        <Row>
          <Col lg={10} className="mx-auto">
            {currentStep === 1 && renderStep1()}
            {currentStep === 2 && renderStep2()}
            {currentStep === 3 && renderStep3()}
            {currentStep === 4 && renderStep4()}
            {currentStep === 5 && renderStep5()}
            {currentStep === 6 && renderStep6()}
            {currentStep === 7 && renderStep7()}

            {renderNavigationButtons()}
          </Col>
        </Row>

        {/* Footer Info */}
        <Row className="mt-5">
          <Col>
            <Card className="border-0 bg-light">
              <Card.Body className="p-4">
                <h4 className="text-center mb-4">🇱🇰 Sri Lanka-Specific Features</h4>
                <Row>
                  <Col md={3} className="text-center mb-3">
                    <div className="feature-icon mb-2">💰</div>
                    <h6>LKR Currency</h6>
                    <small className="text-muted">Local currency calculations</small>
                  </Col>
                  <Col md={3} className="text-center mb-3">
                    <div className="feature-icon mb-2">🏙️</div>
                    <h6>District Pricing</h6>
                    <small className="text-muted">25 districts covered</small>
                  </Col>
                  <Col md={3} className="text-center mb-3">
                    <div className="feature-icon mb-2">🎓</div>
                    <h6>Real Student Data</h6>
                    <small className="text-muted">1,020 student responses</small>
                  </Col>
                  <Col md={3} className="text-center mb-3">
                    <div className="feature-icon mb-2">📈</div>
                    <h6>86.89% Accuracy</h6>
                    <small className="text-muted">AI-powered predictions</small>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default BudgetOptimizerNew;
