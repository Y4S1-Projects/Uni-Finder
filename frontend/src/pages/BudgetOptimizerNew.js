import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner, ProgressBar, Modal } from 'react-bootstrap';
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

  // Gemini AI Enhanced Strategy state
  const [geminiInsight, setGeminiInsight] = useState(null);
  const [displayedText, setDisplayedText] = useState(''); // For streaming effect
  const [isStreaming, setIsStreaming] = useState(false);
  const [geminiLoading, setGeminiLoading] = useState(false);
  const [geminiError, setGeminiError] = useState(null);
  const [aiProvider, setAiProvider] = useState(null); // Track which AI was used
  const aiSectionRef = useRef(null); // Target for scroll-to-AI button

  // Distance warning modal state
  const [distanceWarning, setDistanceWarning] = useState({ show: false, pendingValue: '' });

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
    home_money: 0,           // Money received from family/home
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
      [name]: ['monthly_income', 'home_money', 'rent', 'distance_uni_accommodation', 'distance_home_uni', 
               'cooking_percentage', 'internet', 'study_materials', 'entertainment', 
               'utilities', 'healthcare', 'other'].includes(name) 
        ? (value === '' ? '' : (parseInt(value) || 0))
        : value
    }));
  };

  // ── Gemini AI Enhanced Strategy ─────────────────────────────
  const fetchGeminiInsight = async (result, isRetry = false) => {
    setGeminiLoading(true);
    setGeminiError(null);
    if (!isRetry) {
      setGeminiInsight(null);
    }
    try {
      const payload = {
        financial_summary:  result.financial_summary,
        expense_breakdown:  result.expense_breakdown,
        risk_assessment:    result.risk_assessment,
        optimal_strategy:   result.optimal_strategy,
        student_profile: {
          university:          formData.university,
          year_of_study:       formData.year_of_study,
          field_of_study:      formData.field_of_study,
          district:            formData.district,
          accommodation_type:  formData.accommodation_type,
          food_type:           formData.food_type,
          transport_method:    formData.transport_method
        }
      };
      const resp = await fetch(`${backendUrl}/api/budget/gemini-strategy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      
      if (resp.ok && data.success) {
        const content = data.ai_strategy || data.gemini_strategy;
        setGeminiInsight(content); // Store full text
        setDisplayedText(''); // Reset displayed text
        setIsStreaming(true); // Start streaming animation
        setAiProvider(data.ai_provider || data.model_used || 'AI');
        if (data.cached) {
          console.log(`✅ Using cached ${data.ai_provider} response`);
        }
      } else {
        // Use user-friendly message if available
        const errorMessage = data.user_message || data.error || 'Gemini AI temporarily unavailable';
        setGeminiError({
          message: errorMessage,
          canRetry: data.retry_suggested || resp.status === 429,
          technical: data.technical_details,
          isRateLimit: resp.status === 429
        });
      }
    } catch (e) {
      setGeminiError({
        message: 'Could not reach Gemini service. Please check your connection.',
        canRetry: true,
        technical: e.message,
        isRateLimit: false
      });
    } finally {
      setGeminiLoading(false);
    }
  };

  const handleDistanceHomeChange = (e) => {
    const val = e.target.value;
    const num = parseInt(val) || 0;
    if (num > 800) {
      setDistanceWarning({ show: true, pendingValue: val === '' ? '' : num });
    } else {
      setFormData(prev => ({ ...prev, distance_home_uni: val === '' ? '' : num }));
    }
  };

  const confirmDistanceWarning = () => {
    setFormData(prev => ({ ...prev, distance_home_uni: distanceWarning.pendingValue }));
    setDistanceWarning({ show: false, pendingValue: '' });
  };

  const cancelDistanceWarning = () => {
    setDistanceWarning({ show: false, pendingValue: '' });
  };

  const nextStep = () => {
    setCurrentStep(prev => Math.min(prev + 1, 7));
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const scrollToAISection = () => {
    if (aiSectionRef.current) {
      aiSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  // ── Streaming Text Effect (like ChatGPT) ─────────────────────
  useEffect(() => {
    if (!isStreaming || !geminiInsight) return;

    let currentIndex = 0;
    const fullText = geminiInsight;
    const charsPerFrame = 3; // Characters to add per interval (adjust speed)
    
    const streamInterval = setInterval(() => {
      if (currentIndex >= fullText.length) {
        setIsStreaming(false);
        clearInterval(streamInterval);
        return;
      }
      
      currentIndex += charsPerFrame;
      setDisplayedText(fullText.substring(0, Math.min(currentIndex, fullText.length)));
    }, 30); // 30ms interval for smooth streaming

    return () => clearInterval(streamInterval);
  }, [isStreaming, geminiInsight]);

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
        // Don't automatically fetch AI insights - user must click button
        
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
          {steps.map((step, index) => {
            const stepNum = index + 1;
            const isCompleted = currentStep > stepNum;
            const isActive = currentStep === stepNum;
            const isClickable = isCompleted;
            return (
              <div
                key={index}
                className={`step-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''} ${isClickable ? 'clickable' : ''}`}
                onClick={() => isClickable && setCurrentStep(stepNum)}
                title={isClickable ? `Go back to Step ${stepNum}: ${step}` : undefined}
              >
                <div className="step-number">
                  {isCompleted ? (
                    <span className="step-done">
                      <span className="step-check">✓</span>
                      <span className="step-num-badge">{stepNum}</span>
                    </span>
                  ) : (
                    stepNum
                  )}
                </div>
                <div className="step-label">
                  <span className="step-num-text">Step {stepNum}</span>
                  <span className="step-name-text">{step}</span>
                </div>
              </div>
            );
          })}
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
              onFocus={e => e.target.select()}
              required
            />
            <Form.Text className="text-muted">
              Total money you receive monthly (allowance, scholarship, part-time job)
            </Form.Text>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label><strong>💌 Money Received from Home / Family (LKR)</strong></Form.Label>
            <Form.Control
              type="number"
              name="home_money"
              value={formData.home_money}
              onChange={handleInputChange}
              onFocus={e => e.target.select()}
              placeholder="0"
            />
            <Form.Text className="text-muted">
              Enter the monthly amount your family sends you (leave 0 if none). 
              This will be added to your effective income.
            </Form.Text>
            {formData.home_money > 0 && (
              <div className="alert alert-info mt-2 py-1 px-3 mb-0" style={{fontSize:'0.85rem'}}>
                💡 Effective total income: <strong>LKR {(Number(formData.monthly_income) + Number(formData.home_money)).toLocaleString()}</strong>/month
              </div>
            )}
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
              onFocus={e => e.target.select()}
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
                  onFocus={e => e.target.select()}
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
                  onChange={handleDistanceHomeChange}
                  onFocus={e => e.target.select()}
                  isInvalid={Number(formData.distance_home_uni) > 800}
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
                  onFocus={e => e.target.select()}
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
                  onFocus={e => e.target.select()}
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
                  onFocus={e => e.target.select()}
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
                  onFocus={e => e.target.select()}
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
                  onFocus={e => e.target.select()}
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
                  onFocus={e => e.target.select()}
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
                  {financial_summary.home_money > 0 && (
                    <div style={{fontSize:'0.72rem',color:'#777',marginTop:2}}>
                      Base: LKR {(financial_summary.base_income||0).toLocaleString()} + 
                      Family: LKR {financial_summary.home_money.toLocaleString()}
                    </div>
                  )}
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

        {/* Expense Breakdown */}
        <Card className="shadow-lg border-0 mb-4">
          <Card.Header style={{background:'linear-gradient(135deg,#667eea 0%,#764ba2 100%)'}} className="text-white">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <h4 className="mb-0">📊 Expense Breakdown</h4>
                <small style={{opacity:0.85}}>Where your money goes each month</small>
              </div>
              <div className="text-end">
                <div style={{fontSize:'0.8rem',opacity:0.85}}>Total Monthly</div>
                <div style={{fontSize:'1.5rem',fontWeight:700}}>LKR {expense_breakdown.total_expenses?.toLocaleString()}</div>
              </div>
            </div>
          </Card.Header>
          <Card.Body className="p-4">
            <Row>
              <Col md={6}>
                <h5 className="mb-3 fw-bold" style={{color:'#4a5568'}}>💸 Monthly Expenses</h5>
                {(() => {
                  const icons = {
                    accommodation: {icon:'🏠', color:'#6c63ff'},
                    food:          {icon:'🍽️', color:'#38b2ac'},
                    transport:     {icon:'🚌', color:'#ed8936'},
                    education:     {icon:'📚', color:'#4299e1'},
                    entertainment: {icon:'🎉', color:'#ed64a6'},
                    utilities:     {icon:'💡', color:'#ecc94b'},
                    healthcare:    {icon:'🏥', color:'#fc8181'},
                    other:         {icon:'📦', color:'#a0aec0'},
                    internet:      {icon:'📶', color:'#667eea'},
                    study_materials:{icon:'✏️', color:'#4299e1'},
                  };
                  const total = expense_breakdown.total_expenses || 1;
                  return Object.entries(expense_breakdown)
                    .filter(([k]) => k !== 'total_expenses' && expense_breakdown[k] > 0)
                    .sort(([,a],[,b]) => b - a)
                    .map(([category, amount]) => {
                      const pct = ((amount / total) * 100).toFixed(1);
                      const meta = icons[category] || {icon:'💰', color:'#718096'};
                      const label = category.replace(/_/g,' ').replace(/\b\w/g, c => c.toUpperCase());
                      return (
                        <div key={category} className="mb-3">
                          <div className="d-flex justify-content-between align-items-center mb-1">
                            <span style={{fontWeight:600, color:'#2d3748'}}>
                              {meta.icon} {label}
                            </span>
                            <span style={{fontWeight:700, color: meta.color}}>
                              LKR {amount.toLocaleString()}
                              <span className="ms-2 text-muted fw-normal" style={{fontSize:'0.8rem'}}>({pct}%)</span>
                            </span>
                          </div>
                          <div style={{background:'#edf2f7', borderRadius:'999px', height:'8px', overflow:'hidden'}}>
                            <div style={{
                              width: `${Math.min(pct, 100)}%`,
                              height:'100%',
                              background: meta.color,
                              borderRadius:'999px',
                              transition:'width 0.8s ease'
                            }}/>
                          </div>
                        </div>
                      );
                    });
                })()}
                <div className="d-flex justify-content-between align-items-center mt-4 pt-3"
                     style={{borderTop:'2px dashed #e2e8f0'}}>
                  <span style={{fontWeight:700, fontSize:'1rem', color:'#2d3748'}}>TOTAL EXPENSES</span>
                  <span style={{fontWeight:800, fontSize:'1.2rem',
                    background:'linear-gradient(135deg,#667eea,#764ba2)',
                    WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent'}}>
                    LKR {expense_breakdown.total_expenses?.toLocaleString()}
                  </span>
                </div>
              </Col>
              <Col md={6}>
                <h5 className="mb-3 fw-bold" style={{color:'#4a5568'}}>🤖 Calculated Budgets</h5>
                {calculated_budgets.food && (
                  <div className="mb-3 p-3 rounded" style={{background:'#f0fff4', border:'1px solid #9ae6b4'}}>
                    <div className="d-flex justify-content-between align-items-center mb-1">
                      <span><strong>🍽️ Food Budget:</strong></span>
                      <span className="text-success fw-bold fs-6">
                        LKR {calculated_budgets.food.monthly_total.toLocaleString()}
                      </span>
                    </div>
                    <div className="d-flex justify-content-between">
                      <small className="text-muted">Type: {calculated_budgets.food.food_type}</small>
                      <small className="text-muted">Daily avg: LKR {calculated_budgets.food.daily_cost.toLocaleString()}</small>
                    </div>
                    {/* Grocery / Outside split */}
                    {calculated_budgets.food.breakdown && (
                      <div className="mt-2 ps-2 border-start border-success border-2">
                        {calculated_budgets.food.breakdown.groceries !== undefined && (
                          <small className="text-muted d-block">
                            🛒 Grocery (cooking portion): <strong>LKR {Math.round(calculated_budgets.food.breakdown.groceries).toLocaleString()}</strong>
                            {calculated_budgets.food.grocery_note && <span className="ms-1 text-secondary">({calculated_budgets.food.grocery_note})</span>}
                          </small>
                        )}
                        {calculated_budgets.food.breakdown.outside_meals !== undefined && (
                          <small className="text-muted d-block">
                            🍜 Outside meals: <strong>LKR {Math.round(calculated_budgets.food.breakdown.outside_meals).toLocaleString()}</strong>
                            {calculated_budgets.food.outside_note && <span className="ms-1 text-secondary">({calculated_budgets.food.outside_note})</span>}
                          </small>
                        )}
                        {calculated_budgets.food.breakdown.daily_commute === undefined && 
                         calculated_budgets.food.breakdown.estimate_based_on_income !== undefined && (
                          <small className="text-muted d-block">
                            📊 Estimated from income profile
                          </small>
                        )}
                      </div>
                    )}
                  </div>
                )}
                {calculated_budgets.transport && (
                  <div className="mb-3 p-3 rounded" style={{background:'#eff6ff', border:'1px solid #bfdbfe'}}>
                    {/* Header row */}
                    <div className="d-flex justify-content-between align-items-center mb-2">
                      <span><strong>🚌 Transport Budget:</strong></span>
                      <span className="text-success fw-bold fs-6">
                        LKR {calculated_budgets.transport.monthly_total.toLocaleString()}
                        <small className="text-muted fw-normal">/month</small>
                      </span>
                    </div>

                    {/* Mode badge */}
                    <div className="mb-2">
                      <span className="badge bg-secondary me-1">
                        {calculated_budgets.transport.transport_method}
                      </span>
                      {calculated_budgets.transport.commute_days_per_month && (
                        <span className="badge bg-light text-dark border">
                          {calculated_budgets.transport.commute_days_per_month} commute days/month
                        </span>
                      )}
                    </div>

                    {/* Per-trip cost — clearly labelled */}
                    {calculated_budgets.transport.daily_cost > 0 && (
                      <div className="d-flex align-items-center gap-2 mb-2 p-2 rounded"
                           style={{background:'#e8f4fd', border:'1px solid #bee3f8'}}>
                        <span style={{fontSize:'1.1rem'}}>🔄</span>
                        <div className="flex-grow-1">
                          <div style={{fontSize:'0.78rem', color:'#4a5568', fontWeight:600}}>
                            Round-trip fare &nbsp;
                            <span style={{fontWeight:400, color:'#718096'}}>
                              (Accommodation → Campus → Accommodation)
                            </span>
                          </div>
                          <div style={{fontSize:'0.82rem', color:'#2d3748'}}>
                            <strong>LKR {calculated_budgets.transport.daily_cost.toLocaleString()}</strong>
                            &nbsp;per trip
                            {calculated_budgets.transport.one_way_trip_cost > 0 && (
                              <span className="text-muted ms-2">
                                (one-way: LKR {calculated_budgets.transport.one_way_trip_cost.toLocaleString()})
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Monthly breakdown */}
                    {calculated_budgets.transport.breakdown && (
                      <div className="ps-2 border-start border-primary border-2">
                        {calculated_budgets.transport.breakdown.daily_commute > 0 && (
                          <div className="d-flex justify-content-between">
                            <small className="text-muted">
                              🏫 Campus commute
                              <span className="ms-1 text-muted" style={{fontSize:'0.73rem'}}>
                                (round-trip × {calculated_budgets.transport.commute_days_per_month || '~22'} days)
                              </span>
                            </small>
                            <small><strong>LKR {calculated_budgets.transport.breakdown.daily_commute.toLocaleString()}</strong></small>
                          </div>
                        )}
                        {calculated_budgets.transport.breakdown.misc_trips > 0 && (
                          <div className="d-flex justify-content-between">
                            <small className="text-muted">
                              🌧️ Emergency / weekend trips
                              <span className="ms-1 text-muted" style={{fontSize:'0.73rem'}}>(rain, late nights, city)</span>
                            </small>
                            <small><strong>LKR {calculated_budgets.transport.breakdown.misc_trips.toLocaleString()}</strong></small>
                          </div>
                        )}
                        {calculated_budgets.transport.breakdown.home_visits > 0 && (
                          <div className="d-flex justify-content-between">
                            <small className="text-muted">🏡 Home visits</small>
                            <small><strong>LKR {calculated_budgets.transport.breakdown.home_visits.toLocaleString()}</strong></small>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
                {/* Show home_money contribution if present */}
                {financial_summary.home_money > 0 && (
                  <div className="alert alert-info py-2 px-3 mb-0" style={{fontSize:'0.82rem'}}>
                    💌 Includes LKR {financial_summary.home_money.toLocaleString()} family support
                    {' '}(base: LKR {financial_summary.base_income.toLocaleString()} + home: LKR {financial_summary.home_money.toLocaleString()})
                  </div>
                )}
              </Col>
            </Row>
          </Card.Body>
        </Card>

        {/* 🆕 OPTIMAL BUDGET STRATEGY SECTION */}
        {analysisResult.optimal_strategy && (
          <Card className="shadow-lg border-0 mb-4 border-success border-3">
            <Card.Header className="bg-gradient-success text-white">
              <h4 className="mb-0">🎯 YOUR PERSONALIZED OPTIMAL BUDGET STRATEGY</h4>
              <p className="mb-0 mt-2">AI-powered recommendations to maximize your savings</p>
            </Card.Header>
            <Card.Body className="p-4">
              {/* Strategy Overview */}
              <Row className="mb-4">
                <Col md={4}>
                  <div className="text-center p-3 bg-light rounded">
                    <h6 className="text-muted">📊 Current Expenses</h6>
                    <h4 className="text-danger mb-0">
                      LKR {analysisResult.optimal_strategy.current_situation.total_expenses.toLocaleString()}
                    </h4>
                    <small className="text-muted">
                      {analysisResult.optimal_strategy.current_situation.savings_rate}% savings now
                    </small>
                  </div>
                </Col>
                <Col md={4}>
                  <div className="text-center p-3 bg-success text-white rounded">
                    <h6>🎯 Optimised Target</h6>
                    <h4 className="mb-0">
                      LKR {analysisResult.optimal_strategy.optimal_target.target_expenses.toLocaleString()}
                    </h4>
                    <small>
                      {analysisResult.optimal_strategy.optimal_target.target_savings_rate}% savings rate
                    </small>
                    <div style={{fontSize:'0.72rem',opacity:0.85,marginTop:3}}>
                      (what you could spend after optimising)
                    </div>
                  </div>
                </Col>
                <Col md={4}>
                  {analysisResult.optimal_strategy.potential_improvement.extra_savings > 0 ? (
                    <div className="text-center p-3 bg-warning rounded">
                      <h6 className="text-dark">💰 Potential Improvement</h6>
                      <h4 className="text-success mb-0">
                        +LKR {analysisResult.optimal_strategy.potential_improvement.extra_savings.toLocaleString()}
                      </h4>
                      <small className="text-dark">Extra you could save/month</small>
                      <div style={{fontSize:'0.72rem',color:'#555',marginTop:3}}>
                        Expense reduction: LKR {analysisResult.optimal_strategy.potential_improvement.expense_reduction.toLocaleString()}
                      </div>
                    </div>
                  ) : (
                    <div className="text-center p-3 bg-info text-white rounded">
                      <h6>✅ Already Optimised!</h6>
                      <h5 className="mb-0">Great Budget</h5>
                      <small>Your spending is well-controlled</small>
                    </div>
                  )}
                </Col>
              </Row>

              {/* Maximum Savings Potential */}
              {analysisResult.optimal_strategy.maximum_savings_potential > 0 && (
                <Alert variant="success" className="mb-4">
                  <h5>💰 Total Savings Potential: LKR {analysisResult.optimal_strategy.maximum_savings_potential.toLocaleString()}/month</h5>
                  <p className="mb-0">By implementing all recommendations below, you could save this amount monthly!</p>
                </Alert>
              )}

              {/* ── Journey to Optimised Target flow strip ── */}
              {analysisResult.optimal_strategy.optimal_alternatives &&
               analysisResult.optimal_strategy.optimal_alternatives.length > 0 && (
                <div className="opt-journey-wrap">
                  <div className="opt-journey-header">
                    <span className="opt-journey-badge">Step 1</span>
                    <span className="opt-journey-title">🗺️ Your Path to the Optimised Target</span>
                    <span className="opt-journey-hint">
                      Follow these changes first; then let the AI build your detailed action plan.
                    </span>
                  </div>

                  {/* Step nodes rail (no percentage text) */}
                  <div className="opt-step-rail">
                    {analysisResult.optimal_strategy.optimal_alternatives.slice(0, 5).map((alt, idx) => (
                      <React.Fragment key={idx}>
                        <div className={`opt-step-node opt-step-node--${alt.priority === 'High' ? 'high' : alt.priority === 'Medium' ? 'mid' : 'low'}`}>
                          <div className="opt-step-num">{idx + 1}</div>
                          <div className="opt-step-icon">
                            {alt.category.toLowerCase().includes('food')   ? '🍱' :
                             alt.category.toLowerCase().includes('trans')  ? '🚌' :
                             alt.category.toLowerCase().includes('accom')  ? '🏠' :
                             alt.category.toLowerCase().includes('internet')? '📶' :
                             alt.category.toLowerCase().includes('util')   ? '💡' :
                             alt.category.toLowerCase().includes('study') || alt.category.toLowerCase().includes('material') ? '📚' :
                             alt.category.toLowerCase().includes('entertain')? '🎮' :
                             alt.category.toLowerCase().includes('health')  ? '🏥' :
                             alt.category.toLowerCase().includes('income') || alt.category.toLowerCase().includes('earn') ? '💼' : '⚡'}
                          </div>
                          <div className="opt-step-name">{alt.category}</div>
                          {alt.estimated_savings > 0 && (
                            <div className="opt-step-save">-LKR {alt.estimated_savings.toLocaleString()}/mo</div>
                          )}
                          <div className={`opt-step-priority opt-step-priority--${alt.priority === 'High' ? 'high' : alt.priority === 'Medium' ? 'mid' : 'low'}`}>
                            {alt.priority}
                          </div>
                        </div>
                        {idx < Math.min(analysisResult.optimal_strategy.optimal_alternatives.length, 5) - 1 && (
                          <div className="opt-step-connector">
                            <div className="opt-connector-line" />
                            <div className="opt-connector-arrow">▶</div>
                          </div>
                        )}
                      </React.Fragment>
                    ))}
                    {/* Final target node */}
                    <div className="opt-step-connector">
                      <div className="opt-connector-line" />
                      <div className="opt-connector-arrow">▶</div>
                    </div>
                    <div className="opt-step-node opt-step-node--target">
                      <div className="opt-step-num opt-step-num--target">🎯</div>
                      <div className="opt-step-icon" style={{fontSize:'1.5rem'}}>✅</div>
                      <div className="opt-step-name" style={{fontWeight:700, color:'#155724'}}>Optimised!</div>
                      <div className="opt-step-save" style={{color:'#155724',fontWeight:700}}>
                        LKR {analysisResult.optimal_strategy.optimal_target.target_expenses.toLocaleString()}
                      </div>
                      <div className="opt-step-priority opt-step-priority--target">
                        {analysisResult.optimal_strategy.optimal_target.target_savings_rate}% saved
                      </div>
                    </div>
                  </div>

                  <div className="opt-journey-footer">
                    <p className="opt-journey-footer-text">
                      When you are ready for a guided plan, jump to the
                      <strong> OpenAI AI Enhanced Strategy</strong> section. There the AI will convert this path
                      into a clear, step-by-step routine you can follow.
                    </p>
                    <div className="opt-journey-footer-btn">
                      <Button
                        size="sm"
                        variant="success"
                        onClick={scrollToAISection}
                      >
                        Go to OpenAI AI Enhanced Strategy 🚀
                      </Button>
                    </div>
                  </div>
                </div>
              )}

              {/* Optimal Alternatives */}
              {analysisResult.optimal_strategy.optimal_alternatives && 
               analysisResult.optimal_strategy.optimal_alternatives.length > 0 && (
                <div className="mb-4">
                  <h5 className="mb-3">🔄 Smart Budget Alternatives</h5>
                  {analysisResult.optimal_strategy.optimal_alternatives.map((alt, index) => (
                    <Card key={index} className={`mb-3 border-${alt.priority === 'High' ? 'danger' : alt.priority === 'Medium' ? 'warning' : 'info'}`}>
                      <Card.Body>
                        <Row>
                          <Col md={12}>
                            <div className="d-flex align-items-start mb-2">
                              <span className={`badge bg-${alt.priority === 'High' ? 'danger' : alt.priority === 'Medium' ? 'warning' : 'info'} me-2`}>
                                {alt.priority} Priority
                              </span>
                              <h6 className="mb-0">{alt.category}</h6>
                            </div>
                            <p className="mb-2">
                              <strong>Current:</strong> {alt.current_choice}
                            </p>
                            <p className="mb-2 text-success">
                              <strong>✨ Optimal:</strong> {alt.optimal_choice}
                            </p>
                            <p className="text-muted mb-3">
                              <small><strong>Why?</strong> {alt.reasoning}</small>
                            </p>
                            
                            {/* Action Steps */}
                            {alt.action_steps && alt.action_steps.length > 0 && (
                              <div>
                                <strong>Action Steps:</strong>
                                <ol className="mb-0 mt-2">
                                  {alt.action_steps.map((step, idx) => (
                                    <li key={idx}><small>{step}</small></li>
                                  ))}
                                </ol>
                              </div>
                            )}
                            
                            {alt.note && (
                              <p className="text-info mt-2 mb-0">
                                <small><strong>Note:</strong> {alt.note}</small>
                              </p>
                            )}
                          </Col>
                        </Row>
                      </Card.Body>
                    </Card>
                  ))}
                </div>
              )}

              {/* Implementation Plan */}
              {analysisResult.optimal_strategy.implementation_plan && (
                <div className="mb-4">
                  <h5 className="mb-3">� Your Action Plan</h5>
                  <Row>
                    {analysisResult.optimal_strategy.implementation_plan.immediate_actions && 
                     analysisResult.optimal_strategy.implementation_plan.immediate_actions.length > 0 && (
                      <Col md={4}>
                        <Card className="border-danger mb-3">
                          <Card.Header className="bg-danger text-white">
                            <h6 className="mb-0">🚨 Immediate (This Week)</h6>
                          </Card.Header>
                          <Card.Body>
                            <ul className="mb-0 ps-3">
                              {analysisResult.optimal_strategy.implementation_plan.immediate_actions.map((action, idx) => (
                                <li key={idx} className="mb-2">
                                  <small>{action.action}</small>
                                  <div className="text-success">
                                    <small><strong>Save: LKR {action.savings.toLocaleString()}</strong></small>
                                  </div>
                                </li>
                              ))}
                            </ul>
                          </Card.Body>
                        </Card>
                      </Col>
                    )}
                    
                    {analysisResult.optimal_strategy.implementation_plan.this_month_actions && 
                     analysisResult.optimal_strategy.implementation_plan.this_month_actions.length > 0 && (
                      <Col md={4}>
                        <Card className="border-warning mb-3">
                          <Card.Header className="bg-warning">
                            <h6 className="mb-0">⏰ This Month</h6>
                          </Card.Header>
                          <Card.Body>
                            <ul className="mb-0 ps-3">
                              {analysisResult.optimal_strategy.implementation_plan.this_month_actions.map((action, idx) => (
                                <li key={idx} className="mb-2">
                                  <small>{action.action}</small>
                                  <div className="text-success">
                                    <small><strong>Save: LKR {action.savings.toLocaleString()}</strong></small>
                                  </div>
                                </li>
                              ))}
                            </ul>
                          </Card.Body>
                        </Card>
                      </Col>
                    )}
                    
                    {analysisResult.optimal_strategy.implementation_plan.long_term_actions && 
                     analysisResult.optimal_strategy.implementation_plan.long_term_actions.length > 0 && (
                      <Col md={4}>
                        <Card className="border-info mb-3">
                          <Card.Header className="bg-info text-white">
                            <h6 className="mb-0">🎯 Long-term (3-6 months)</h6>
                          </Card.Header>
                          <Card.Body>
                            <ul className="mb-0 ps-3">
                              {analysisResult.optimal_strategy.implementation_plan.long_term_actions.map((action, idx) => (
                                <li key={idx} className="mb-2">
                                  <small>{action.action}</small>
                                  <div className="text-success">
                                    <small><strong>Save: LKR {action.savings.toLocaleString()}</strong></small>
                                  </div>
                                </li>
                              ))}
                            </ul>
                          </Card.Body>
                        </Card>
                      </Col>
                    )}
                  </Row>
                </div>
              )}

              {/* ── AI strategy connector bridge ── */}
              <div className="opt-ai-bridge">
                <div className="opt-ai-bridge-left">
                  <div className="opt-ai-bridge-icon">✨</div>
                  <div>
                    <div className="opt-ai-bridge-heading">Want a Deeper, Step-by-Step Action Plan?</div>
                    <div className="opt-ai-bridge-sub">
                      The <strong>AI Enhanced Strategy</strong> below will generate personalised guidance — exactly how to execute each step above based on your full profile.
                    </div>
                  </div>
                </div>
                <div className="opt-ai-bridge-arrow">
                  <div className="opt-ai-bridge-arrow-line" />
                  <div className="opt-ai-bridge-arrow-bounce">↓ Scroll down</div>
                </div>
              </div>

            </Card.Body>
          </Card>
        )}

        {/* ════════════════════════════════════════════════════════ */}
        {/*   ✨ GEMINI / OPENAI AI ENHANCED STRATEGY               */}
        {/* ════════════════════════════════════════════════════════ */}
        <div className="gemini-section mb-4" ref={aiSectionRef}>
          {/* Header */}
          <div className="gemini-header">
            <div className="gemini-logo-wrap">
              <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
                <defs>
                  <linearGradient id="gGrad" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#4285F4"/>
                    <stop offset="33%" stopColor="#EA4335"/>
                    <stop offset="66%" stopColor="#FBBC05"/>
                    <stop offset="100%" stopColor="#34A853"/>
                  </linearGradient>
                </defs>
                <path d="M14 3 L14 25 M3 14 L25 14 M6.5 6.5 L21.5 21.5 M21.5 6.5 L6.5 21.5"
                  stroke="url(#gGrad)" strokeWidth="2.5" strokeLinecap="round"/>
              </svg>
            </div>
            <div>
              <h4 className="gemini-title mb-0">
                {aiProvider ? `${aiProvider} AI` : 'AI'} Enhanced Strategy
                {aiProvider === 'Gemini' && ' ✨'}
                {aiProvider === 'OpenAI' && ' 🚀'}
              </h4>
              <p className="gemini-subtitle mb-0">Personalized advice analysing your full financial profile</p>
            </div>
          </div>

          {/* Loading state */}
          {geminiLoading && (
            <div className="gemini-loading">
              <div className="gemini-loading-dots">
                <span /><span /><span /><span />
              </div>
              <p className="gemini-loading-text">AI is analysing your budget profile…</p>
            </div>
          )}

          {/* Initial state - attractive flow CTA */}
          {!geminiInsight && !geminiLoading && !geminiError && (
            <div className="ai-cta-zone">
              {/* Title */}
              <div className="ai-cta-title-row">
                <svg width="32" height="32" viewBox="0 0 28 28" fill="none">
                  <defs>
                    <linearGradient id="aiGrad2" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stopColor="#4285F4"/>
                      <stop offset="50%" stopColor="#FBBC05"/>
                      <stop offset="100%" stopColor="#34A853"/>
                    </linearGradient>
                  </defs>
                  <path d="M14 3 L14 25 M3 14 L25 14 M6.5 6.5 L21.5 21.5 M21.5 6.5 L6.5 21.5"
                    stroke="url(#aiGrad2)" strokeWidth="2.5" strokeLinecap="round"/>
                </svg>
                <div>
                  <h5 className="ai-cta-heading">Unlock Your Personalized Strategy</h5>
                  <p className="ai-cta-sub">AI will analyse your full financial profile and craft a step-by-step enhancement plan</p>
                </div>
              </div>

              {/* 3-step flow diagram */}
              <div className="ai-flow-row">
                <div className="ai-flow-node">
                  <div className="ai-flow-icon">📊</div>
                  <div className="ai-flow-label">Your Budget Data</div>
                  <div className="ai-flow-desc">Income · Expenses · Goals</div>
                </div>
                <div className="ai-flow-connector">
                  <div className="ai-flow-arrow-line"/>
                  <div className="ai-flow-arrow-head">▶</div>
                </div>
                <div className="ai-flow-node ai-flow-node--center">
                  <div className="ai-flow-icon ai-flow-icon--glow">🤖</div>
                  <div className="ai-flow-label">AI Deep Analysis</div>
                  <div className="ai-flow-desc">Patterns · Risks · Opportunities</div>
                </div>
                <div className="ai-flow-connector">
                  <div className="ai-flow-arrow-line"/>
                  <div className="ai-flow-arrow-head">▶</div>
                </div>
                <div className="ai-flow-node ai-flow-node--out">
                  <div className="ai-flow-icon">🗺️</div>
                  <div className="ai-flow-label">Strategy Roadmap</div>
                  <div className="ai-flow-desc">Steps · Targets · Timeline</div>
                </div>
              </div>

              {/* Feature pills */}
              <div className="ai-features-row">
                <div className="ai-feature-pill"><span>💰</span> Savings Opportunities</div>
                <div className="ai-feature-pill"><span>📉</span> Risk Reduction Plan</div>
                <div className="ai-feature-pill"><span>🎯</span> Action Steps</div>
                <div className="ai-feature-pill"><span>🔮</span> Future Projections</div>
                <div className="ai-feature-pill"><span>🏦</span> Investment Hints</div>
              </div>

              {/* Generate button */}
              <div className="ai-cta-btn-wrap">
                <button
                  className="ai-generate-btn"
                  onClick={() => fetchGeminiInsight(analysisResult)}
                >
                  <span className="ai-generate-btn-glow"/>
                  <span className="ai-generate-btn-text">✨ Generate AI Enhanced Strategy</span>
                </button>
                <p className="ai-cta-hint">Powered by {aiProvider ? `${aiProvider} AI` : 'Gemini / OpenAI'} · Usually takes 5-10 seconds</p>
              </div>
            </div>
          )}

          {/* Error / API key not set */}
          {geminiError && !geminiLoading && (
            <div className="gemini-error-box">
              {(typeof geminiError === 'string' && (geminiError.includes('not configured') || geminiError.includes('GEMINI_API_KEY'))) ||
               (typeof geminiError === 'object' && geminiError.message && geminiError.message.includes('not configured')) ? (
                <>
                  <div className="gemini-error-icon">🔑</div>
                  <h5>Set Up AI Services (Free Options Available)</h5>
                  <p>Add an AI API key to <code>backend/.env</code> to unlock this feature.</p>
                  
                  <div className="border rounded p-3 mb-3 bg-light">
                    <strong>Option 1: Google Gemini (Recommended - FREE)</strong>
                    <ol className="gemini-setup-steps mb-0 mt-2">
                      <li>Visit <a href="https://aistudio.google.com/apikey" target="_blank" rel="noreferrer">aistudio.google.com/apikey</a></li>
                      <li>Sign in → Click <strong>"Create API key"</strong></li>
                      <li>Add to <code>backend/.env</code>: <code>GEMINI_API_KEY=your_key</code></li>
                    </ol>
                    <p className="text-success small mb-0 mt-2">✅ 1,500 requests/day · No credit card needed</p>
                  </div>
                  
                  <div className="border rounded p-3 bg-light">
                    <strong>Option 2: OpenAI (Paid Backup)</strong>
                    <ol className="gemini-setup-steps mb-0 mt-2">
                      <li>Visit <a href="https://platform.openai.com/api-keys" target="_blank" rel="noreferrer">platform.openai.com/api-keys</a></li>
                      <li>Create API key (requires payment method)</li>
                      <li>Add to <code>backend/.env</code>: <code>OPENAI_API_KEY=your_key</code></li>
                    </ol>
                    <p className="text-info small mb-0 mt-2">💰 ~$0.0001 per request (gpt-4o-mini)</p>
                  </div>
                  
                  <p className="text-muted small mb-0 mt-3">💡 Set both keys for automatic fallback when Gemini hits rate limits</p>
                </>
              ) : typeof geminiError === 'object' && geminiError.isRateLimit ? (
                <>
                  <div className="gemini-error-icon">⏰</div>
                  <h5>Rate Limit Exceeded</h5>
                  <p className="mb-3">{geminiError.message}</p>
                  <Alert variant="info" className="mb-3">
                    <strong>What happened?</strong><br/>
                    The Gemini API free tier has daily/per-minute request limits. Your quota has been temporarily exceeded.
                  </Alert>
                  <Alert variant="success" className="mb-3">
                    <strong>✅ Good news:</strong> Your budget analysis is complete! The AI insights are just an extra bonus.
                  </Alert>
                  <div className="d-flex gap-2 justify-content-center">
                    <Button 
                      size="sm" 
                      variant="primary" 
                      onClick={() => fetchGeminiInsight(analysisResult, true)}
                    >
                      🔄 Try Again
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline-secondary"
                      onClick={() => setGeminiError(null)}
                    >
                      Dismiss
                    </Button>
                  </div>
                  {geminiError.technical && (
                    <details className="mt-3">
                      <summary className="text-muted small" style={{cursor: 'pointer'}}>Technical Details</summary>
                      <pre className="text-muted small mt-2" style={{fontSize: '10px', maxHeight: '100px', overflow: 'auto'}}>
                        {geminiError.technical}
                      </pre>
                    </details>
                  )}
                </>
              ) : (
                <>
                  <div className="gemini-error-icon">⚠️</div>
                  <p>{typeof geminiError === 'string' ? geminiError : geminiError.message}</p>
                  {(typeof geminiError === 'object' && geminiError.canRetry) && (
                    <div className="d-flex gap-2 justify-content-center mt-3">
                      <Button 
                        size="sm" 
                        variant="outline-primary" 
                        onClick={() => fetchGeminiInsight(analysisResult, true)}
                      >
                        🔄 Retry
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline-secondary"
                        onClick={() => setGeminiError(null)}
                      >
                        Dismiss
                      </Button>
                    </div>
                  )}
                  {typeof geminiError === 'object' && geminiError.technical && (
                    <details className="mt-3">
                      <summary className="text-muted small" style={{cursor: 'pointer'}}>Technical Details</summary>
                      <pre className="text-muted small mt-2" style={{fontSize: '10px', maxHeight: '100px', overflow: 'auto'}}>
                        {geminiError.technical}
                      </pre>
                    </details>
                  )}
                </>
              )}
            </div>
          )}

          {/* AI Response */}
          {(geminiInsight || displayedText) && !geminiLoading && (() => {
            const rawText = isStreaming ? displayedText : geminiInsight;

            // ── Try to parse structured STEP format ──────────────────
            const isStructured = /STEP\s+\d+\s*:/i.test(rawText);

            if (isStructured) {
              // Parse GAP_SUMMARY
              const gapMatch  = rawText.match(/GAP_SUMMARY\s*:\s*(.+)/i);
              const gapSummary = gapMatch ? gapMatch[1].trim() : null;

              // Parse all STEP blocks
              const stepBlocks = [];
              const stepRegex  = /STEP\s+(\d+)\s*:\s*([^\n]+)\nCATEGORY\s*:\s*([^\n]+)\nSAVE\s*:\s*([^\n]+)\nHOW\s*:\s*([^\n]+)\nTIMEFRAME\s*:\s*([^\n]+)/gi;
              let m;
              while ((m = stepRegex.exec(rawText)) !== null) {
                stepBlocks.push({
                  num:       m[1],
                  title:     m[2].trim(),
                  category:  m[3].trim(),
                  save:      m[4].trim(),
                  how:       m[5].trim(),
                  timeframe: m[6].trim(),
                });
              }

              const quickWinMatch  = rawText.match(/QUICK_WIN\s*:\s*(.+)/i);
              const motivationMatch = rawText.match(/MOTIVATION\s*:\s*(.+)/i);
              const quickWin   = quickWinMatch  ? quickWinMatch[1].trim()  : null;
              const motivation = motivationMatch ? motivationMatch[1].trim() : null;

              const catIcon = (cat) => {
                const c = cat.toLowerCase();
                if (c.includes('food'))   return '🍱';
                if (c.includes('trans'))  return '🚌';
                if (c.includes('accom'))  return '🏠';
                if (c.includes('internet') || c.includes('phone')) return '📶';
                if (c.includes('util'))   return '💡';
                if (c.includes('study') || c.includes('material')) return '📚';
                if (c.includes('entertain')) return '🎮';
                if (c.includes('health'))    return '🏥';
                if (c.includes('income') || c.includes('earn')) return '�';
                return '⚡';
              };

              const timeColor = (tf) => {
                const t = tf.toLowerCase();
                if (t.includes('this week') || t.includes('today') || t.includes('week 1')) return 'ai-tl-node--now';
                if (t.includes('week 2') || t.includes('week 3')) return 'ai-tl-node--soon';
                return 'ai-tl-node--later';
              };

              return (
                <div className="ai-tl-wrap">
                  {/* Header meta */}
                  <div className="gemini-response-meta">
                    <span className="gemini-badge">
                      {aiProvider === 'OpenAI' ? '🚀' : '✨'} AI Step Plan
                    </span>
                    <span className="gemini-model-tag">
                      {aiProvider === 'OpenAI' ? 'gpt-4o-mini' : aiProvider === 'Gemini' ? 'gemini-2.0-flash' : 'AI'}
                    </span>
                    <span className="ai-tl-gap-badge">
                      {stepBlocks.length} steps to your target
                    </span>
                  </div>

                  {/* Gap summary bar */}
                  {gapSummary && (
                    <div className="ai-tl-gap-summary">
                      <span className="ai-tl-gap-icon">🎯</span>
                      <span>{gapSummary}</span>
                    </div>
                  )}

                  {/* Timeline steps */}
                  <div className="ai-tl-body">
                    <div className="ai-tl-spine" />
                    {stepBlocks.map((step, idx) => (
                      <div
                        key={idx}
                        className={`ai-tl-node ${timeColor(step.timeframe)}`}
                        style={{ animationDelay: `${idx * 0.12}s` }}
                      >
                        {/* Left: number dot on spine */}
                        <div className="ai-tl-dot">
                          <span>{step.num}</span>
                        </div>

                        {/* Card */}
                        <div className="ai-tl-card">
                          <div className="ai-tl-card-header">
                            <span className="ai-tl-cat-icon">{catIcon(step.category)}</span>
                            <div className="ai-tl-card-titles">
                              <div className="ai-tl-card-title">{step.title}</div>
                              <div className="ai-tl-card-cat">{step.category}</div>
                            </div>
                            <div className="ai-tl-save-pill">
                              <div className="ai-tl-save-amt">{step.save}</div>
                              <div className="ai-tl-save-label">monthly saving</div>
                            </div>
                          </div>
                          <div className="ai-tl-card-how">
                            <span className="ai-tl-how-label">How:</span> {step.how}
                          </div>
                          <div className="ai-tl-card-footer">
                            <span className="ai-tl-timeframe-tag">🗓 {step.timeframe}</span>
                          </div>
                        </div>
                      </div>
                    ))}

                    {/* Target reached node */}
                    {!isStreaming && stepBlocks.length > 0 && (
                      <div
                        className="ai-tl-node ai-tl-node--target"
                        style={{ animationDelay: `${stepBlocks.length * 0.12}s` }}
                      >
                        <div className="ai-tl-dot ai-tl-dot--target">✅</div>
                        <div className="ai-tl-card ai-tl-card--target">
                          <div className="ai-tl-target-title">🎯 Optimised Target Reached!</div>
                          {analysisResult?.optimal_strategy?.optimal_target && (
                            <div className="ai-tl-target-sub">
                              LKR {analysisResult.optimal_strategy.optimal_target.target_expenses.toLocaleString()}/month
                              · {analysisResult.optimal_strategy.optimal_target.target_savings_rate}% savings rate
                            </div>
                          )}
                          {motivation && <div className="ai-tl-motivation">"{motivation}"</div>}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Quick Win banner */}
                  {quickWin && !isStreaming && (
                    <div className="ai-tl-quickwin">
                      <span className="ai-tl-qw-icon">⚡</span>
                      <div>
                        <div className="ai-tl-qw-label">Do This TODAY — Quick Win</div>
                        <div className="ai-tl-qw-text">{quickWin}</div>
                      </div>
                    </div>
                  )}

                  {/* Footer */}
                  <div className="gemini-footer-note">
                    <span>💡 Generated by {aiProvider || 'AI'} · personalised to your profile</span>
                    {!isStreaming && (
                      <Button size="sm" variant="link" className="ms-3 p-0 gemini-retry-btn"
                        onClick={() => fetchGeminiInsight(analysisResult, true)}>
                        🔄 Regenerate
                      </Button>
                    )}
                  </div>

                  {isStreaming && <span className="streaming-cursor" style={{margin:'12px 32px',display:'block'}}>▊</span>}
                </div>
              );
            }

            // ── Fallback: plain text renderer ────────────────────────
            return (
              <div className="gemini-response">
                <div className="gemini-response-meta">
                  <span className="gemini-badge">
                    {aiProvider === 'Gemini' && '✨'}
                    {aiProvider === 'OpenAI' && '🚀'}
                    {!aiProvider && '🤖'}
                    {' '}AI Generated
                  </span>
                  <span className="gemini-model-tag">
                    {aiProvider === 'Gemini' && 'gemini-2.0-flash'}
                    {aiProvider === 'OpenAI' && 'gpt-4o-mini'}
                    {!aiProvider && 'AI Model'}
                  </span>
                </div>
                <div className="gemini-content">
                  {rawText.split('\n').map((line, i) => {
                    if (!line.trim()) return <div key={i} style={{height:'10px'}} />;
                    if (line.startsWith('**') && line.endsWith('**'))
                      return <h5 key={i} className="gemini-section-head">{line.replace(/\*\*/g, '')}</h5>;
                    if (line.includes('**')) {
                      const parts = line.split(/\*\*(.*?)\*\*/g);
                      return <p key={i} className="gemini-para">{parts.map((p, pi) => pi % 2 === 1 ? <strong key={pi}>{p}</strong> : p)}</p>;
                    }
                    if (line.trim().startsWith('- ') || line.trim().startsWith('• '))
                      return <div key={i} className="gemini-bullet"><span className="gemini-bullet-dot">•</span><span>{line.replace(/^[-•]\s*/, '')}</span></div>;
                    if (line.startsWith('#'))
                      return <h5 key={i} className="gemini-section-head">{line.replace(/^#+\s*/, '')}</h5>;
                    return <p key={i} className="gemini-para">{line}</p>;
                  })}
                  {isStreaming && <span className="streaming-cursor">▊</span>}
                </div>
                <div className="gemini-footer-note">
                  <span>💡 This analysis was generated by {aiProvider || 'AI'} based on your specific financial data</span>
                  {!isStreaming && (
                    <Button size="sm" variant="link" className="ms-3 p-0 gemini-retry-btn"
                      onClick={() => fetchGeminiInsight(analysisResult, true)}>🔄 Regenerate</Button>
                  )}
                </div>
              </div>
            );
          })()}
        </div>

        {/* Action Buttons */}
        <div className="text-center">
          <Button variant="outline-primary" onClick={() => setCurrentStep(1)} className="me-2">
            📝 Edit Profile
          </Button>
          <Button variant="primary" onClick={handlePrintReport}>
            🖨️ Print Full Report
          </Button>
        </div>
      </div>
    );
  };

  const handlePrintReport = () => {
    if (!analysisResult) return;
    const { financial_summary, expense_breakdown, calculated_budgets, risk_assessment, recommendation } = analysisResult;
    const strategy = analysisResult.optimal_strategy;
    const date = new Date().toLocaleDateString('en-LK', { year:'numeric', month:'long', day:'numeric' });

    const catIcons = { accommodation:'🏠', food:'🍽️', transport:'🚌', education:'📚',
      entertainment:'🎉', utilities:'💡', healthcare:'🏥', internet:'📱', study_materials:'✏️', other:'📦' };

    const expRows = Object.entries(expense_breakdown)
      .filter(([k,v]) => k !== 'total_expenses' && v > 0)
      .sort(([,a],[,b]) => b - a)
      .map(([k,v]) => {
        const pct = ((v / expense_breakdown.total_expenses) * 100).toFixed(1);
        const label = k.replace(/_/g,' ').replace(/\b\w/g, c => c.toUpperCase());
        return `<tr>
          <td>${catIcons[k] || '💰'} ${label}</td>
          <td style="text-align:right;font-weight:600">LKR ${v.toLocaleString()}</td>
          <td style="text-align:right;color:#666">${pct}%</td>
          <td style="width:140px;padding-left:8px">
            <div style="background:#edf2f7;border-radius:6px;height:10px">
              <div style="width:${Math.min(pct,100)}%;height:100%;background:#667eea;border-radius:6px"></div>
            </div>
          </td>
        </tr>`;
      }).join('');

    const riskRecs = (risk_assessment?.recommendations || [])
      .map(r => `<li><strong>${r.category}:</strong> ${r.message}${r.potential_savings>0 ? ` <span style="color:#28a745">(Save LKR ${r.potential_savings.toLocaleString()}/mo)</span>` : ''}</li>`)
      .join('');

    const altRows = (strategy?.optimal_alternatives || [])
      .map(a => `<tr>
        <td>${a.category||''}</td>
        <td>${a.current_method||''}</td>
        <td>${a.alternative||a.recommendation||''}</td>
        <td style="color:#e53e3e;text-align:right">LKR ${(a.current_cost||0).toLocaleString()}</td>
        <td style="color:#28a745;text-align:right">LKR ${(a.optimised_cost||a.target_cost||0).toLocaleString()}</td>
        <td style="color:#28a745;font-weight:700;text-align:right">${a.savings_percentage||a.potential_savings_pct||''}%</td>
      </tr>`).join('');

    const actionSteps = (recommendation?.action_steps || [])
      .map((s,i) => `<li style="margin-bottom:6px"><strong>Step ${i+1}:</strong> ${s}</li>`).join('');

    const foodInfo = calculated_budgets?.food;
    const transInfo = calculated_budgets?.transport;

    const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<title>Student Budget Report - ${formData.full_name || 'Student'}</title>
<style>
  * { box-sizing: border-box; margin:0; padding:0; }
  body { font-family: 'Segoe UI', Arial, sans-serif; color: #2d3748; background: #fff; font-size:13px; }
  .page { max-width:900px; margin:0 auto; padding:30px 30px; }
  /* Header */
  .report-header { background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); color:white;
    border-radius:12px; padding:28px 32px; margin-bottom:24px; }
  .report-header h1 { font-size:22px; font-weight:800; margin-bottom:4px; }
  .report-header .sub { opacity:0.88; font-size:13px; }
  .report-header .meta { margin-top:14px; display:flex; gap:30px; flex-wrap:wrap; }
  .report-header .meta span { font-size:12px; opacity:0.9; }
  .report-header .meta strong { display:block; font-size:14px; opacity:1; }
  /* Section */
  .section { margin-bottom:24px; border:1px solid #e2e8f0; border-radius:10px; overflow:hidden; }
  .section-header { padding:12px 18px; font-weight:700; font-size:14px; color:white; }
  .section-body { padding:18px; }
  .green { background: linear-gradient(135deg,#38b2ac,#2c7a7b); }
  .purple { background: linear-gradient(135deg,#667eea,#764ba2); }
  .orange { background: linear-gradient(135deg,#ed8936,#c05621); }
  .danger { background: linear-gradient(135deg,#fc8181,#c53030); }
  .success-bg { background: linear-gradient(135deg,#68d391,#276749); }
  /* Summary boxes */
  .summary-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; }
  .summary-box { border:1px solid #e2e8f0; border-radius:8px; padding:14px; text-align:center; }
  .summary-box .label { font-size:11px; color:#718096; text-transform:uppercase; letter-spacing:.5px; margin-bottom:4px; }
  .summary-box .value { font-size:18px; font-weight:800; }
  .blue { color:#667eea; } .red { color:#e53e3e; } .green-c { color:#28a745; }
  /* Table */
  table { width:100%; border-collapse:collapse; }
  th { background:#f7fafc; font-size:11px; text-transform:uppercase; letter-spacing:.5px; 
       color:#718096; padding:8px 10px; border-bottom:2px solid #e2e8f0; text-align:left; }
  td { padding:8px 10px; border-bottom:1px solid #f0f0f0; vertical-align:middle; }
  tr:last-child td { border-bottom:none; }
  /* 2-col */
  .two-col { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
  .detail-box { background:#f7fafc; border-radius:8px; padding:14px; }
  .detail-box h4 { font-size:13px; font-weight:700; margin-bottom:10px; }
  .detail-row { display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px dashed #e2e8f0; font-size:12px; }
  .detail-row:last-child { border-bottom:none; font-weight:700; font-size:13px; }
  /* Strategy */
  .strategy-grid { display:grid; grid-template-columns: repeat(3,1fr); gap:14px; margin-bottom:16px; }
  .strategy-box { border-radius:8px; padding:14px; text-align:center; }
  .s-current { background:#fff5f5; border:1px solid #fed7d7; }
  .s-target { background:#f0fff4; border:1px solid #9ae6b4; }
  .s-improve { background:#fffbf0; border:1px solid #fbd38d; }
  .strategy-box .s-label { font-size:11px; color:#718096; margin-bottom:4px; }
  .strategy-box .s-value { font-size:20px; font-weight:800; }
  /* Risk */
  .risk-high { background:#fff5f5; border:2px solid #fc8181; border-radius:8px; padding:14px; }
  .risk-low  { background:#f0fff4; border:2px solid #9ae6b4; border-radius:8px; padding:14px; }
  /* Gemini */
  .ai-box { background:#eff6ff; border:1px solid #bfdbfe; border-radius:8px; padding:16px; font-size:12px; line-height:1.7; }
  /* Tip */
  .alert-box { background:#fffbeb; border:1px solid #fcd34d; border-radius:8px; padding:12px 14px; margin-bottom:12px; font-size:12px; }
  /* Footer */
  .footer { text-align:center; margin-top:30px; font-size:11px; color:#a0aec0; border-top:1px solid #e2e8f0; padding-top:14px; }
  ul { padding-left:18px; }
  li { margin-bottom:4px; }
  @media print {
    body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .page { padding:10px 16px; }
    .no-print { display:none !important; }
  }
</style>
</head>
<body>
<div class="page">

  <!-- HEADER -->
  <div class="report-header">
    <h1>🎓 Student Budget Analysis Report</h1>
    <div class="sub">AI-Powered Financial Insights — UniFinder LK</div>
    <div class="meta">
      <div><span>Student</span><strong>${formData.full_name || '—'}</strong></div>
      <div><span>University</span><strong>${formData.university || '—'}</strong></div>
      <div><span>Year / Field</span><strong>${formData.year_of_study} · ${formData.field_of_study}</strong></div>
      <div><span>District</span><strong>${formData.district}</strong></div>
      <div><span>Report Date</span><strong>${date}</strong></div>
      <div><span>Accuracy</span><strong>86.89% ML Model</strong></div>
    </div>
  </div>

  <!-- FINANCIAL SUMMARY -->
  <div class="section">
    <div class="section-header green">💰 Financial Summary</div>
    <div class="section-body">
      <div class="summary-grid">
        <div class="summary-box">
          <div class="label">Monthly Income</div>
          <div class="value blue">LKR ${financial_summary.monthly_income.toLocaleString()}</div>
          ${financial_summary.home_money > 0 ? `<div style="font-size:11px;color:#888;margin-top:3px">Base: LKR ${(financial_summary.base_income||0).toLocaleString()} + Family: LKR ${financial_summary.home_money.toLocaleString()}</div>` : ''}
        </div>
        <div class="summary-box">
          <div class="label">Total Expenses</div>
          <div class="value red">LKR ${financial_summary.total_expenses.toLocaleString()}</div>
        </div>
        <div class="summary-box">
          <div class="label">Monthly Savings</div>
          <div class="value ${financial_summary.monthly_savings >= 0 ? 'green-c' : 'red'}">LKR ${financial_summary.monthly_savings.toLocaleString()}</div>
        </div>
        <div class="summary-box">
          <div class="label">Savings Rate</div>
          <div class="value ${financial_summary.savings_rate >= 0 ? 'green-c' : 'red'}">${financial_summary.savings_rate}%</div>
        </div>
      </div>
    </div>
  </div>

  <!-- EXPENSE BREAKDOWN -->
  <div class="section">
    <div class="section-header purple">📊 Expense Breakdown</div>
    <div class="section-body">
      <table>
        <thead><tr><th>Category</th><th style="text-align:right">Amount</th><th style="text-align:right">Share</th><th>Distribution</th></tr></thead>
        <tbody>${expRows}</tbody>
        <tfoot>
          <tr style="background:#f7fafc;font-weight:700;font-size:14px">
            <td>TOTAL EXPENSES</td>
            <td style="text-align:right;color:#667eea">LKR ${expense_breakdown.total_expenses.toLocaleString()}</td>
            <td style="text-align:right">100%</td><td></td>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>

  <!-- AI CALCULATED BUDGETS -->
  <div class="section">
    <div class="section-header orange">🤖 AI-Calculated Budgets</div>
    <div class="section-body">
      <div class="two-col">
        ${foodInfo ? `<div class="detail-box">
          <h4>🍽️ Food Budget — LKR ${foodInfo.monthly_total.toLocaleString()}/month</h4>
          <div class="detail-row"><span>Food Type</span><span>${foodInfo.food_type}</span></div>
          <div class="detail-row"><span>Daily Average</span><span>LKR ${foodInfo.daily_cost.toLocaleString()}</span></div>
          ${foodInfo.breakdown?.groceries !== undefined ? `<div class="detail-row"><span>🛒 Groceries (cooking)</span><span>LKR ${Math.round(foodInfo.breakdown.groceries).toLocaleString()}</span></div>` : ''}
          ${foodInfo.breakdown?.outside_meals !== undefined ? `<div class="detail-row"><span>🍜 Outside meals</span><span>LKR ${Math.round(foodInfo.breakdown.outside_meals).toLocaleString()}</span></div>` : ''}
          <div class="detail-row"><span>Monthly Total</span><span>LKR ${foodInfo.monthly_total.toLocaleString()}</span></div>
        </div>` : '<div class="detail-box"><h4>🍽️ Food Budget</h4><p style="color:#999">Not available</p></div>'}
        ${transInfo ? `<div class="detail-box">
          <h4>🚌 Transport Budget — LKR ${transInfo.monthly_total.toLocaleString()}/month</h4>
          <div class="detail-row"><span>Method</span><span>${transInfo.transport_method}</span></div>
          <div class="detail-row"><span>Commute Days/Month</span><span>${transInfo.commute_days_per_month || '~22'}</span></div>
          <div class="detail-row"><span>Round-trip Fare</span><span>LKR ${transInfo.daily_cost.toLocaleString()}</span></div>
          ${transInfo.one_way_trip_cost > 0 ? `<div class="detail-row"><span>One-way Fare</span><span>LKR ${transInfo.one_way_trip_cost.toLocaleString()}</span></div>` : ''}
          ${transInfo.breakdown?.daily_commute > 0 ? `<div class="detail-row"><span>🏫 Campus Commute</span><span>LKR ${transInfo.breakdown.daily_commute.toLocaleString()}</span></div>` : ''}
          ${transInfo.breakdown?.misc_trips > 0 ? `<div class="detail-row"><span>🌧️ Emergency Trips</span><span>LKR ${transInfo.breakdown.misc_trips.toLocaleString()}</span></div>` : ''}
          ${transInfo.breakdown?.home_visits > 0 ? `<div class="detail-row"><span>🏡 Home Visits</span><span>LKR ${transInfo.breakdown.home_visits.toLocaleString()}</span></div>` : ''}
          <div class="detail-row"><span>Monthly Total</span><span>LKR ${transInfo.monthly_total.toLocaleString()}</span></div>
        </div>` : '<div class="detail-box"><h4>🚌 Transport Budget</h4><p style="color:#999">Not available</p></div>'}
      </div>
    </div>
  </div>

  <!-- RISK ASSESSMENT -->
  ${risk_assessment ? `<div class="section">
    <div class="section-header ${risk_assessment.risk_level === 'High Risk' ? 'danger' : 'success-bg'}">${risk_assessment.risk_level === 'High Risk' ? '⚠️' : '✅'} Risk Assessment — ${risk_assessment.risk_level}</div>
    <div class="section-body">
      <div class="${risk_assessment.risk_level === 'High Risk' ? 'risk-high' : 'risk-low'}" style="margin-bottom:${riskRecs ? '14px' : '0'}">
        <strong>Risk Probability: ${risk_assessment.risk_probability}%</strong>
        <span style="margin-left:16px;font-size:12px;color:#555">${risk_assessment.risk_level === 'High Risk' ? 'Your current spending puts you at financial risk. Review the recommendations below.' : 'Your financial situation looks healthy. Keep maintaining good spending habits!'}</span>
      </div>
      ${riskRecs ? `<h5 style="font-size:13px;margin-bottom:8px;font-weight:700">📋 Risk Recommendations:</h5><ul>${riskRecs}</ul>` : ''}
    </div>
  </div>` : ''}

  <!-- OPTIMAL STRATEGY -->
  ${strategy ? `<div class="section">
    <div class="section-header success-bg">🎯 Personalised Optimal Budget Strategy</div>
    <div class="section-body">
      <div class="strategy-grid" style="margin-bottom:18px">
        <div class="strategy-box s-current">
          <div class="s-label">📊 Current Expenses</div>
          <div class="s-value red">LKR ${strategy.current_situation.total_expenses.toLocaleString()}</div>
          <div style="font-size:11px;color:#666;margin-top:4px">${strategy.current_situation.savings_rate}% savings now</div>
        </div>
        <div class="strategy-box s-target">
          <div class="s-label">🎯 Optimised Target</div>
          <div class="s-value green-c">LKR ${strategy.optimal_target.target_expenses.toLocaleString()}</div>
          <div style="font-size:11px;color:#666;margin-top:4px">${strategy.optimal_target.target_savings_rate}% savings rate</div>
        </div>
        <div class="strategy-box s-improve">
          <div class="s-label">💰 Potential Saving</div>
          <div class="s-value ${strategy.potential_improvement.extra_savings > 0 ? 'green-c' : 'blue'}">
            ${strategy.potential_improvement.extra_savings > 0 ? '+LKR ' + strategy.potential_improvement.extra_savings.toLocaleString() : 'Already Optimised ✅'}
          </div>
          <div style="font-size:11px;color:#666;margin-top:4px">${strategy.potential_improvement.extra_savings > 0 ? 'extra/month possible' : 'Well done!'}</div>
        </div>
      </div>
      ${altRows ? `<h5 style="font-size:13px;font-weight:700;margin-bottom:10px">🔄 Optimisation Alternatives:</h5>
      <table>
        <thead><tr><th>Category</th><th>Current</th><th>Alternative</th><th style="text-align:right">Current Cost</th><th style="text-align:right">Target Cost</th><th style="text-align:right">Savings</th></tr></thead>
        <tbody>${altRows}</tbody>
      </table>` : ''}
    </div>
  </div>` : ''}

  <!-- RECOMMENDATIONS -->
  ${recommendation ? `<div class="section">
    <div class="section-header purple">💡 Personalised Recommendations</div>
    <div class="section-body">
      ${recommendation.primary_advice ? `<div class="alert-box" style="margin-bottom:14px"><strong>📌 Primary Advice:</strong> ${recommendation.primary_advice}</div>` : ''}
      ${actionSteps ? `<h5 style="font-size:13px;font-weight:700;margin-bottom:8px">✅ Action Steps:</h5><ul>${actionSteps}</ul>` : ''}
    </div>
  </div>` : ''}

  <!-- STUDENT PROFILE SUMMARY -->
  <div class="section">
    <div class="section-header" style="background:linear-gradient(135deg,#a0aec0,#718096)">👤 Student Profile</div>
    <div class="section-body">
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;font-size:12px">
        <div><span style="color:#718096">University:</span> <strong>${formData.university}</strong></div>
        <div><span style="color:#718096">Year:</span> <strong>${formData.year_of_study}</strong></div>
        <div><span style="color:#718096">Field:</span> <strong>${formData.field_of_study}</strong></div>
        <div><span style="color:#718096">District:</span> <strong>${formData.district}</strong></div>
        <div><span style="color:#718096">Accommodation:</span> <strong>${formData.accommodation_type}</strong></div>
        <div><span style="color:#718096">Transport:</span> <strong>${formData.transport_method}</strong></div>
        <div><span style="color:#718096">Distance to Uni:</span> <strong>${formData.distance_uni_accommodation} km</strong></div>
        <div><span style="color:#718096">Distance Home:</span> <strong>${formData.distance_home_uni} km</strong></div>
        <div><span style="color:#718096">Home Visits:</span> <strong>${formData.home_visit_frequency}</strong></div>
        <div><span style="color:#718096">Food Type:</span> <strong>${formData.food_type}</strong></div>
        <div><span style="color:#718096">Diet:</span> <strong>${formData.diet_type}</strong></div>
        <div><span style="color:#718096">Meals/Day:</span> <strong>${formData.meals_per_day}</strong></div>
      </div>
    </div>
  </div>

  <div class="footer">
    <p>Generated by <strong>UniFinder LK — AI Student Budget Optimizer</strong> &nbsp;|&nbsp; ${date} &nbsp;|&nbsp; Model Accuracy: 86.89%</p>
    <p style="margin-top:4px">This report is for financial guidance purposes only. Actual costs may vary.</p>
  </div>

</div>
<script>window.onload = () => window.print();</script>
</body>
</html>`;

    const win = window.open('', '_blank', 'width=1000,height=800');
    win.document.write(html);
    win.document.close();
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

      {/* Distance Warning Modal */}
      <Modal show={distanceWarning.show} onHide={cancelDistanceWarning} centered>
        <Modal.Header closeButton className="border-0 pb-0">
          <Modal.Title className="d-flex align-items-center gap-2">
            <span style={{fontSize:'1.5rem'}}>⚠️</span>
            <span>Unusual Distance Detected</span>
          </Modal.Title>
        </Modal.Header>
        <Modal.Body className="pt-2">
          <div className="alert alert-warning mb-3" style={{borderRadius:'10px'}}>
            <strong>Are you sure?</strong>
          </div>
          <p className="mb-1">
            You entered <strong>{distanceWarning.pendingValue} km</strong> for <em>Home to University</em>.
          </p>
          <p className="text-muted" style={{fontSize:'0.9rem'}}>
            Sri Lanka's maximum end-to-end distance is about <strong>~430 km</strong>.
            A value over <strong>800 km</strong> is unusual for a student commute.
            Please double-check the distance.
          </p>
          <p className="mb-0" style={{fontSize:'0.9rem', color:'#555'}}>
            If you travel abroad or have a special case, you can confirm below.
          </p>
        </Modal.Body>
        <Modal.Footer className="border-0">
          <Button variant="outline-secondary" onClick={cancelDistanceWarning}>
            ✏️ Correct it
          </Button>
          <Button variant="warning" onClick={confirmDistanceWarning}>
            ✅ Yes, it's correct
          </Button>
        </Modal.Footer>
      </Modal>

    </div>
  );
};

export default BudgetOptimizerNew;
