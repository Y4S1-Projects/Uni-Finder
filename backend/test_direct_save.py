"""
Quick test to verify budget prediction can be saved directly to MongoDB
This mimics what the frontend does after getting Flask results
"""

import requests
import json

# Test saving directly to Node.js MongoDB API (like SignUp does)
def test_direct_budget_save():
    print("\n" + "="*70)
    print("🧪 TESTING DIRECT MONGODB SAVE (Like SignUp Page)")
    print("="*70)
    
    test_data = {
        "email": "direct.test@student.com",
        "username": "Direct Test Student",
        "monthly_income": 35000,
        "year_of_study": "Second Year",
        "field_of_study": "IT",
        "university": "SLIIT",
        "district": "Colombo",
        "accommodation_type": "Rented Room",
        "rent": 10000,
        "internet": 1500,
        "study_materials": 2000,
        "entertainment": 2000,
        "utilities": 1000,
        "healthcare": 1000,
        "other": 500,
        "food_type": "Mixed",
        "meals_per_day": "3 meals",
        "diet_type": "Non-Vegetarian",
        "cooking_frequency": "Most days",
        "cooking_percentage": 60,
        "distance_uni_accommodation": 5,
        "distance_home_uni": 80,
        "transport_method": "Bus",
        "transport_method_home": "Bus",
        "days_per_week": "5 days",
        "home_visit_frequency": "Monthly",
        "food_budget": {
            "monthly_total": 15000,
            "breakdown": {},
            "recommendations": []
        },
        "transport_budget": {
            "monthly_total": 3500,
            "breakdown": {},
            "recommendations": []
        },
        "predicted_budget": 28500,
        "ml_confidence": 85.5,
        "risk_level": "Low Risk",
        "risk_probability": 12.3,
        "total_expenses": 27500,
        "calculated_savings": 7500,
        "savings_rate": 21.4,
        "recommendations": ["Great budget!", "Keep it up!"],
        "actionable_steps": ["Track expenses", "Save regularly"],
        "expense_breakdown": {
            "rent": 10000,
            "food": 15000,
            "transport": 3500,
            "internet": 1500,
            "study_materials": 2000,
            "entertainment": 2000,
            "utilities": 1000,
            "healthcare": 1000,
            "other": 500
        },
        "analysis_date": "2025-11-30T10:00:00.000Z",
        "status": "active"
    }
    
    try:
        print("\n📤 Sending POST request to http://localhost:3000/api/budget/save...")
        
        response = requests.post(
            'http://localhost:3000/api/budget/save',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("\n✅ SUCCESS! Budget prediction saved to MongoDB")
            print(f"   Prediction ID: {result.get('predictionId')}")
            print(f"   Message: {result.get('message')}")
            print(f"\n   Saved Data:")
            print(f"   - Email: {test_data['email']}")
            print(f"   - Income: LKR {test_data['monthly_income']}")
            print(f"   - Expenses: LKR {test_data['total_expenses']}")
            print(f"   - Savings: LKR {test_data['calculated_savings']}")
            print(f"   - Risk: {test_data['risk_level']}")
            
            print("\n" + "="*70)
            print("✅ DIRECT SAVE WORKING - Same approach as SignUp page!")
            print("="*70)
            
            return result.get('predictionId')
        else:
            print(f"\n❌ FAILED: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR!")
        print("   Node.js server is not running on port 3000")
        print("\n   To fix:")
        print("   1. Open terminal")
        print("   2. cd backend")
        print("   3. npm run dev")
        return None
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None

def verify_saved_data(prediction_id):
    """Verify the saved data can be retrieved"""
    if not prediction_id:
        print("\n⚠️  No prediction ID to verify")
        return
    
    print("\n" + "="*70)
    print("🔍 VERIFYING SAVED DATA")
    print("="*70)
    
    try:
        response = requests.get(
            f'http://localhost:3000/api/budget/{prediction_id}',
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            data = result['data']
            
            print(f"\n✅ Data retrieved successfully!")
            print(f"\n   Student Info:")
            print(f"   - Email: {data.get('email')}")
            print(f"   - University: {data.get('university')}")
            print(f"   - Year: {data.get('year_of_study')}")
            
            print(f"\n   Financial Summary:")
            print(f"   - Income: LKR {data.get('monthly_income')}")
            print(f"   - Expenses: LKR {data.get('total_expenses')}")
            print(f"   - Savings: LKR {data.get('calculated_savings')}")
            
            print(f"\n   ML Predictions:")
            print(f"   - Risk Level: {data.get('risk_level')}")
            print(f"   - ML Confidence: {data.get('ml_confidence')}%")
            
            print("\n" + "="*70)
            print("✅ DATA VERIFIED IN MONGODB!")
            print("="*70)
            
        else:
            print(f"❌ Failed to retrieve: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("\n" + "🚀 DIRECT MONGODB SAVE TEST (Frontend Approach)")
    print("="*70)
    print("This test mimics what BudgetOptimizerNew.js does:")
    print("  1. Get results from Flask")
    print("  2. Save DIRECTLY to MongoDB via Node.js API")
    print("  3. Same as SignUp page approach")
    print("="*70)
    
    # Test direct save
    prediction_id = test_direct_budget_save()
    
    # Verify it was saved
    if prediction_id:
        verify_saved_data(prediction_id)
    
    print("\n" + "="*70)
    print("📋 NEXT STEPS:")
    print("="*70)
    print("1. Make sure Node.js server is running: npm run dev")
    print("2. Test the frontend form at: http://localhost:3000/budget-optimizer-new")
    print("3. Check MongoDB collection: budgetpredictions")
    print("4. View saved predictions: http://localhost:3000/api/budget")
    print("\n")
