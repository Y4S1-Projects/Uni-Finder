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

  // Gemini AI Enhanced Strategy state
  const [geminiInsight, setGeminiInsight] = useState(null);
  const [displayedText, setDisplayedText] = useState(''); // For streaming effect
  const [isStreaming, setIsStreaming] = useState(false);
  const [geminiLoading, setGeminiLoading] = useState(false);
  const [geminiError, setGeminiError] = useState(null);
  const [aiProvider, setAiProvider] = useState(null); // Track which AI was used

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

  const nextStep = () => {
    setCurrentStep(prev => Math.min(prev + 1, 7));
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
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
                    <h6 className="text-muted">Current Situation</h6>
                    <h4 className="text-danger mb-0">
                      LKR {analysisResult.optimal_strategy.current_situation.total_expenses.toLocaleString()}
                    </h4>
                    <small className="text-muted">
                      {analysisResult.optimal_strategy.current_situation.savings_rate}% savings rate
                    </small>
                  </div>
                </Col>
                <Col md={4}>
                  <div className="text-center p-3 bg-success text-white rounded">
                    <h6>Optimal Target</h6>
                    <h4 className="mb-0">
                      LKR {analysisResult.optimal_strategy.optimal_target.target_expenses.toLocaleString()}
                    </h4>
                    <small>
                      {analysisResult.optimal_strategy.optimal_target.target_savings_rate}% savings rate
                    </small>
                  </div>
                </Col>
                <Col md={4}>
                  <div className="text-center p-3 bg-warning rounded">
                    <h6 className="text-dark">Potential Improvement</h6>
                    <h4 className="text-success mb-0">
                      +LKR {analysisResult.optimal_strategy.potential_improvement.extra_savings.toLocaleString()}
                    </h4>
                    <small className="text-dark">Extra savings/month</small>
                  </div>
                </Col>
              </Row>

              {/* Maximum Savings Potential */}
              {analysisResult.optimal_strategy.maximum_savings_potential > 0 && (
                <Alert variant="success" className="mb-4">
                  <h5>💰 Total Savings Potential: LKR {analysisResult.optimal_strategy.maximum_savings_potential.toLocaleString()}/month</h5>
                  <p className="mb-0">By implementing all recommendations below, you could save this amount monthly!</p>
                </Alert>
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
                          <Col md={8}>
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
                          <Col md={4} className="text-center border-start">
                            <div className="p-3">
                              <h6 className="text-muted mb-2">Potential Savings</h6>
                              <h3 className="text-success mb-0">
                                LKR {alt.estimated_savings.toLocaleString()}
                              </h3>
                              <small className="text-muted d-block mt-1">/month</small>
                              {alt.payback_period && (
                                <small className="d-block mt-2 text-info">
                                  <strong>Payback:</strong> {alt.payback_period}
                                </small>
                              )}
                            </div>
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

              {/* Success Metrics */}
              {analysisResult.optimal_strategy.success_metrics && (
                <Card className="bg-light border-0">
                  <Card.Body>
                    <h5 className="mb-3">📈 Track Your Progress</h5>
                    <Row>
                      <Col md={4} className="mb-2">
                        <strong>1 Month Goal:</strong>
                        <p className="mb-0">{analysisResult.optimal_strategy.success_metrics.target_1_month}</p>
                      </Col>
                      <Col md={4} className="mb-2">
                        <strong>3 Month Goal:</strong>
                        <p className="mb-0">{analysisResult.optimal_strategy.success_metrics.target_3_months}</p>
                      </Col>
                      <Col md={4} className="mb-2">
                        <strong>6 Month Goal:</strong>
                        <p className="mb-0">{analysisResult.optimal_strategy.success_metrics.target_6_months}</p>
                      </Col>
                    </Row>
                    <hr />
                    <p className="text-muted mb-0">
                      <strong>💡 Tip:</strong> {analysisResult.optimal_strategy.success_metrics.tracking}
                    </p>
                  </Card.Body>
                </Card>
              )}
            </Card.Body>
          </Card>
        )}

        {/* ════════════════════════════════════════════════════════ */}
        {/*   ✨ GEMINI AI ENHANCED STRATEGY                        */}
        {/* ════════════════════════════════════════════════════════ */}
        <div className="gemini-section mb-4">
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

          {/* Initial state - show button to get AI insights */}
          {!geminiInsight && !geminiLoading && !geminiError && (
            <div className="text-center py-5">
              <div className="mb-3">
                <svg width="48" height="48" viewBox="0 0 28 28" fill="none">
                  <defs>
                    <linearGradient id="aiGrad" x1="0" y1="0" x2="1" y2="1">
                      <stop offset="0%" stopColor="#4285F4"/>
                      <stop offset="33%" stopColor="#EA4335"/>
                      <stop offset="66%" stopColor="#FBBC05"/>
                      <stop offset="100%" stopColor="#34A853"/>
                    </linearGradient>
                  </defs>
                  <path d="M14 3 L14 25 M3 14 L25 14 M6.5 6.5 L21.5 21.5 M21.5 6.5 L6.5 21.5"
                    stroke="url(#aiGrad)" strokeWidth="2.5" strokeLinecap="round"/>
                </svg>
              </div>
              <h5 className="mb-3">Get Personalized AI Strategy</h5>
              <p className="text-muted mb-4">
                Click below to generate AI-powered financial advice tailored to your specific situation
              </p>
              <Button 
                variant="primary" 
                size="lg"
                onClick={() => fetchGeminiInsight(analysisResult)}
                className="px-5"
              >
                🤖 Generate AI Insights
              </Button>
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

          {/* Gemini Response */}
          {(geminiInsight || displayedText) && !geminiLoading && (
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
                {(isStreaming ? displayedText : geminiInsight).split('\n').map((line, i) => {
                  if (!line.trim()) return <div key={i} style={{height:'10px'}} />;
                  // Bold headers (lines starting with ** or #)
                  if (line.startsWith('**') && line.endsWith('**')) {
                    return (
                      <h5 key={i} className="gemini-section-head">
                        {line.replace(/\*\*/g, '')}
                      </h5>
                    );
                  }
                  // Inline bold (e.g. **text**)
                  if (line.includes('**')) {
                    const parts = line.split(/\*\*(.*?)\*\*/g);
                    return (
                      <p key={i} className="gemini-para">
                        {parts.map((part, pi) => pi % 2 === 1 ? <strong key={pi}>{part}</strong> : part)}
                      </p>
                    );
                  }
                  // Bullet points
                  if (line.trim().startsWith('- ') || line.trim().startsWith('• ')) {
                    return (
                      <div key={i} className="gemini-bullet">
                        <span className="gemini-bullet-dot">•</span>
                        <span>{line.replace(/^[-•]\s*/, '')}</span>
                      </div>
                    );
                  }
                  // Numbered list
                  if (/^\d+\./.test(line.trim())) {
                    return (
                      <div key={i} className="gemini-num-item">
                        <span className="gemini-num">{line.match(/^\d+/)[0]}</span>
                        <span>{line.replace(/^\d+\.\s*/, '')}</span>
                      </div>
                    );
                  }
                  // Heading with #
                  if (line.startsWith('#')) {
                    return <h5 key={i} className="gemini-section-head">{line.replace(/^#+\s*/, '')}</h5>;
                  }
                  return <p key={i} className="gemini-para">{line}</p>;
                })}
                {/* Blinking cursor during streaming */}
                {isStreaming && <span className="streaming-cursor">▊</span>}
              </div>
              <div className="gemini-footer-note">
                <span>💡 This analysis was generated by {aiProvider || 'AI'} based on your specific financial data</span>
                {!isStreaming && (
                  <Button
                    size="sm" variant="link" className="ms-3 p-0 gemini-retry-btn"
                    onClick={() => fetchGeminiInsight(analysisResult, true)}
                  >
                    🔄 Regenerate
                  </Button>
                )}
              </div>
            </div>
          )}
        </div>

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
