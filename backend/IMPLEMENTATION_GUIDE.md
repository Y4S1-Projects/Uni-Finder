# Budget Optimizer - Complete Implementation Guide

## ✅ What Has Been Built

### Backend Components (Python/Flask)

#### 1. **budget_calculator.py**
Auto-calculates food and transport budgets based on user preferences.

**Features:**
- ✅ Food budget calculation (5 types)
  - Home Cooked (with grocery items)
  - Food Delivery (with meal preferences)
  - Mixed (cooking + delivery split)
  - Mostly Canteen/Restaurants
  - Full Meal Plan
- ✅ Transport budget calculation
  - Daily commute costs
  - Home visit costs
  - Distance-based pricing
- ✅ District-based price adjustments
- ✅ Diet type multipliers (Veg/Non-Veg/Vegan)

#### 2. **ml_budget_predictor.py**
Integrates with your pre-trained ML models (.pkl files).

**Features:**
- ✅ Loads 3 ML models:
  - `budget_optimizer_gbr_model_final_optimized.pkl`
  - `risk_classifier_model_final.pkl`
  - `feature_preprocessor_final.pkl`
- ✅ Budget prediction using GBR model
- ✅ Financial risk assessment (High/Low)
- ✅ Dynamic adjustments based on academic calendar
- ✅ Personalized recommendations
- ✅ Complete financial analysis

#### 3. **app_budget_enhanced.py**
Complete Flask API with all endpoints.

**API Endpoints:**

```
GET  /health                          - Health check
GET  /api/data/districts              - Get all districts
GET  /api/data/universities           - Get universities list
GET  /api/data/food-prices?district=  - Get food prices
GET  /api/data/transport-costs        - Get transport costs
GET  /api/data/rental-prices?district=- Get rental averages
GET  /api/model/performance           - Get ML model metrics

POST /api/budget/calculate-food       - Calculate food budget
POST /api/budget/calculate-transport  - Calculate transport budget
POST /api/budget/predict              - ML budget prediction
POST /api/budget/complete-analysis    - MAIN ENDPOINT (all-in-one)
```

---

## 📊 CSV Data Integration

### Loaded CSV Files:

1. **Student Budget Survey.csv** (1,020 records)
   - Actual student survey data
   - Income ranges, expenses, comfort levels

2. **food_prices.csv** (402 items)
   - District-wise food prices
   - Rice & Curry, Kottu, Biriyani, etc.

3. **Vegetables_fruit_prices.csv** (130,002 records!)
   - Historical vegetable/fruit prices by district
   - Date-wise price tracking

4. **srilanka_transport_costs.csv** (100 routes)
   - District-to-district transport costs
   - Bus, Petrol Car, Diesel Car prices

5. **room_annex_rentals.csv** (669 listings)
   - Room/annex rental prices
   - District-wise accommodation costs

6. **academic_calendar.csv**
   - University academic calendars
   - Used for dynamic budget adjustments (exam periods)

---

## 🚀 How to Run the Backend

### Step 1: Install Dependencies

```bash
cd /Users/shehansalitha/Desktop/Uni-Finder/backend
pip3 install flask flask-cors pandas numpy scikit-learn joblib
```

### Step 2: Start the Server

```bash
python3 app_budget_enhanced.py
```

Server will start at: **http://127.0.0.1:5002**

### Step 3: Test the API

```bash
# Health check
curl http://127.0.0.1:5002/health

# Get districts
curl http://127.0.0.1:5002/api/data/districts

# Get model performance
curl http://127.0.0.1:5002/api/model/performance
```

---

## 📝 Frontend Implementation (Next Steps)

### What You Need to Build in React:

#### 1. **Multi-Step Registration Form**

```
Step 1: Account Information (5 fields)
├─ Email
├─ Password
├─ Full Name
├─ Phone Number
└─ University

Step 2: Academic Profile (3 fields)
├─ Year of Study
├─ Field of Study
└─ Current District

Step 3: Financial Basics (3 fields)
├─ Monthly Income
├─ Accommodation Type
└─ Monthly Rent

Step 4: Food Preferences (Dynamic)
├─ Food Type [Dropdown]
│  └─ If "Home Cooked" → Show grocery items
│  └─ If "Food Delivery" → Show delivery preferences
│  └─ If "Mixed" → Show percentage slider
├─ Meals Per Day
└─ Diet Type

Step 5: Transport Details (Dynamic)
├─ Home Address
├─ University Address
├─ Boarding Address (if applicable)
├─ Transport Method
├─ Days Per Week
└─ Home Visit Frequency

Step 6: Additional Expenses (Optional)
├─ Internet & Mobile
├─ Study Materials
├─ Entertainment
├─ Healthcare
└─ Other

Step 7: Results Dashboard
```

#### 2. **API Integration Examples**

```javascript
// Complete Budget Analysis
const analyzeBudget = async (formData) => {
  const response = await fetch('http://127.0.0.1:5002/api/budget/complete-analysis', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      // Account & Academic
      monthly_income: 30000,
      year_of_study: 'Second Year',
      field_of_study: 'Engineering',
      district: 'Colombo',
      university: 'SLIIT',
      
      // Accommodation
      accommodation_type: 'Rented Room',
      rent: 10000,
      
      // Food
      food_type: 'Mixed',
      meals_per_day: '3 meals',
      diet_type: 'Non-Vegetarian',
      cooking_frequency: 'Most days',
      cooking_percentage: 60,
      
      // Transport
      distance_uni_accommodation: 5,
      distance_home_uni: 85,
      transport_method: 'Bus',
      days_per_week: '5 days',
      home_visit_frequency: 'Monthly',
      
      // Additional
      internet: 1500,
      study_materials: 2000,
      entertainment: 2000,
      utilities: 1000,
      healthcare: 1000,
      other: 500
    })
  });
  
  const result = await response.json();
  return result;
};
```

#### 3. **Results Display Components**

```javascript
// Financial Summary Card
<Card>
  <h3>💰 Financial Summary</h3>
  <div>
    <p>Monthly Income: LKR {result.financial_summary.monthly_income}</p>
    <p>Total Expenses: LKR {result.financial_summary.total_expenses}</p>
    <p>Monthly Savings: LKR {result.financial_summary.monthly_savings}</p>
    <p>Savings Rate: {result.financial_summary.savings_rate}%</p>
  </div>
</Card>

// Expense Breakdown Chart
<PieChart data={[
  { name: 'Rent', value: result.expense_breakdown.rent },
  { name: 'Food', value: result.expense_breakdown.food },
  { name: 'Transport', value: result.expense_breakdown.transport },
  // ... other expenses
]} />

// Risk Assessment Alert
{result.risk_assessment.risk_level === 'High Risk' && (
  <Alert variant="danger">
    ⚠️ High Financial Risk Detected
    <ul>
      {result.risk_assessment.recommendations.map(rec => (
        <li key={rec.category}>{rec.message}</li>
      ))}
    </ul>
  </Alert>
)}

// AI Recommendations
<Card>
  <h3>🎯 AI Recommendations</h3>
  <p>{result.recommendation}</p>
  <p>Status: {result.optimization_status}</p>
</Card>
```

---

## 🔄 Data Flow

```
User Input (Frontend Form)
    ↓
POST /api/budget/complete-analysis
    ↓
budget_calculator.py
    ├─ calculate_food_budget()
    └─ calculate_transport_budget()
    ↓
ml_budget_predictor.py
    ├─ predict_budget() → Uses GBR Model
    ├─ predict_risk() → Uses Risk Classifier
    └─ generate_complete_analysis()
    ↓
Response with:
    ├─ Calculated budgets (food, transport)
    ├─ Expense breakdown (all categories)
    ├─ Financial summary (income, expenses, savings)
    ├─ ML predictions (optimal budget)
    ├─ Risk assessment (High/Low risk)
    └─ Personalized recommendations
    ↓
Display Results (Frontend Dashboard)
```

---

## 📋 Required Input Fields Summary

### Minimum Required (13 fields):
1. Email
2. Password
3. Full Name
4. Phone Number
5. University
6. Year of Study
7. Field of Study
8. District
9. Monthly Income
10. Accommodation Type
11. Monthly Rent
12. Food Type
13. Transport Method

### Optional for Better Predictions (12 more fields):
14. Meals Per Day
15. Diet Type
16. Cooking Frequency
17. Distance Uni to Accommodation
18. Distance Home to University
19. Days Per Week at University
20. Home Visit Frequency
21. Internet & Mobile
22. Study Materials
23. Entertainment
24. Healthcare
25. Other Expenses

---

## 🎨 Frontend Components to Create

### Files to Create:

```
frontend/src/pages/
├─ BudgetOptimizerNew.js        (Main multi-step form)
├─ BudgetResults.js             (Results dashboard)
└─ components/
   ├─ StepIndicator.js          (Progress bar)
   ├─ FoodPreferences.js        (Food type selector)
   ├─ TransportCalculator.js    (Transport inputs)
   ├─ ExpenseBreakdown.js       (Pie chart)
   ├─ RiskAlert.js              (Risk warning)
   └─ RecommendationCard.js     (AI suggestions)
```

### Styling Files:

```
frontend/src/pages/
├─ BudgetOptimizerNew.css
└─ BudgetResults.css
```

---

## 🧪 Testing Checklist

### Backend Tests:

- [ ] Health endpoint works
- [ ] Districts list loads
- [ ] Food prices API returns data
- [ ] Transport costs API works
- [ ] Complete analysis endpoint works
- [ ] ML models load successfully

### Frontend Tests:

- [ ] Multi-step form navigation works
- [ ] Food type selection shows correct inputs
- [ ] Transport calculator displays
- [ ] API calls succeed
- [ ] Results display correctly
- [ ] Charts render properly

---

## 🚨 Common Issues & Solutions

### Issue 1: Models not loading
**Solution:** Ensure `.pkl` files are in `budget_optimizer_files/` folder

### Issue 2: CORS errors
**Solution:** Backend has `CORS(app)` enabled for all origins

### Issue 3: Port already in use
**Solution:** Backend uses port 5002 (different from your main app on 5001)

### Issue 4: CSV files not found
**Solution:** Check paths in `budget_calculator.py` and `ml_budget_predictor.py`

---

## 📞 Next Actions

### For You:

1. **Start Backend:**
   ```bash
   python3 app_budget_enhanced.py
   ```

2. **Test API:**
   - Visit http://127.0.0.1:5002/health
   - Test http://127.0.0.1:5002/api/model/performance

3. **Tell me:**
   - Does the backend start successfully?
   - Any errors in console?
   - Which frontend component should I build first?

### For Me (When You're Ready):

1. Create multi-step React form component
2. Integrate with backend API
3. Build results dashboard
4. Add charts and visualizations
5. Style the complete flow

---

## 📊 Expected Results Example

```json
{
  "success": true,
  "calculated_budgets": {
    "food": {
      "monthly_total": 12350,
      "food_type": "Mixed",
      "daily_cost": 411.67
    },
    "transport": {
      "monthly_total": 4850,
      "daily_cost": 140,
      "transport_method": "Bus"
    }
  },
  "expense_breakdown": {
    "rent": 10000,
    "food": 12350,
    "transport": 4850,
    "internet": 1500,
    "study_materials": 2000,
    "entertainment": 2000,
    "utilities": 1000,
    "healthcare": 1000,
    "other": 500,
    "total_expenses": 35200
  },
  "financial_summary": {
    "monthly_income": 30000,
    "total_expenses": 35200,
    "monthly_savings": -5200,
    "savings_rate": -17.3
  },
  "ml_prediction": {
    "predicted_optimal_budget": 28500,
    "confidence": 86.89,
    "model_used": "GBR_Optimized"
  },
  "risk_assessment": {
    "risk_level": "High Risk",
    "risk_score": 0.783,
    "recommendations": [...]
  },
  "recommendation": "Your expenses exceed income. Immediate budget adjustments needed.",
  "optimization_status": "Over Budget"
}
```

---

**Ready to proceed! Let me know when you've started the backend and I'll build the frontend components! 🚀**
