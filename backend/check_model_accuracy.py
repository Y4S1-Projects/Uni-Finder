#!/usr/bin/env python3
"""
Check ML Model Accuracy and Performance Metrics
This script loads your trained models and displays their accuracy
"""

import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, classification_report
import os

print("\n" + "="*80)
print("🔍 CHECKING ML MODEL ACCURACY")
print("="*80 + "\n")

# Load the trained models
print("📥 Loading models...\n")

try:
    gbr_model = joblib.load('budget_optimizer_files/budget_optimizer_gbr_model_final_optimized.pkl')
    print(f"✅ Budget Prediction Model: {type(gbr_model).__name__}")
except Exception as e:
    print(f"❌ Error loading budget model: {e}")
    exit(1)

try:
    risk_classifier = joblib.load('budget_optimizer_files/risk_classifier_model_final.pkl')
    print(f"✅ Risk Classifier Model: {type(risk_classifier).__name__}")
except Exception as e:
    print(f"❌ Error loading risk classifier: {e}")
    exit(1)

try:
    scaler = joblib.load('budget_optimizer_files/feature_preprocessor_final.pkl')
    print(f"✅ Feature Preprocessor: {type(scaler).__name__}")
except Exception as e:
    print(f"❌ Error loading scaler: {e}")
    exit(1)

print("\n" + "="*80)

# Load and prepare test data from survey
print("\n📊 Loading survey data for accuracy testing...\n")

try:
    survey_df = pd.read_csv('budget_optimizer_files/Student Budget Survey.csv')
    print(f"✅ Loaded {len(survey_df)} survey records")
    
    # Rename columns
    survey_df.columns = [
        'Timestamp', 'Academic_Level', 'Funding_Source', 'Monthly_Income',
        'Transport_Cost', 'Financial_Comfort', 'Affordability_Accommodation',
        'Affordability_Food', 'Affordability_Materials', 'Affordability_Transport',
        'Affordability_Social', 'Financial_Assistance_Needed', 'Work_Hours_Per_Week',
        'Additional_Comments'
    ]
    
    # Create a working copy
    df = survey_df.copy()
    df = df.drop(['Timestamp', 'Additional_Comments'], axis=1)
    
    # Convert Monthly Income
    def convert_income(income_str):
        if pd.isna(income_str) or income_str == 'Prefer not to say':
            return 25000
        income_map = {
            'Less than LKR 15,000': 12500,
            'LKR 15,000 - 25,000': 20000,
            'LKR 25,001 - 35,000': 30000,
            'LKR 35,001 - 50,000': 42500,
            'LKR 50,001 - 75,000': 62500,
            'More than LKR 75,000': 90000
        }
        return income_map.get(income_str, 25000)
    
    df['Monthly_Income_Numeric'] = df['Monthly_Income'].apply(convert_income)
    
    # Convert Transport Cost
    df['Transport_Cost_Numeric'] = pd.to_numeric(df['Transport_Cost'], errors='coerce')
    df['Transport_Cost_Numeric'].fillna(df['Transport_Cost_Numeric'].median(), inplace=True)
    
    # Convert Work Hours
    def convert_work_hours(hours_str):
        if pd.isna(hours_str):
            return 0
        hours_map = {
            '0 hours': 0, '1-5 hours': 3, '6-10 hours': 8,
            '11-15 hours': 13, '16-20 hours': 18, 'More than 20 hours': 25
        }
        return hours_map.get(hours_str, 0)
    
    df['Work_Hours_Numeric'] = df['Work_Hours_Per_Week'].apply(convert_work_hours)
    
    # Convert Affordability
    affordability_map = {
        'Very Affordable': 5, 'Affordable': 4, 'Neutral': 3,
        'Unaffordable': 2, 'Very Unaffordable': 1
    }
    
    for col in ['Affordability_Accommodation', 'Affordability_Food', 'Affordability_Materials',
                'Affordability_Transport', 'Affordability_Social']:
        df[col + '_Score'] = df[col].map(affordability_map).fillna(3)
    
    # Financial Comfort
    df['Financial_Comfort_Score'] = pd.to_numeric(df['Financial_Comfort'], errors='coerce').fillna(3)
    
    # Funding sources
    df['Has_Parental_Support'] = df['Funding_Source'].str.contains('Parental/Family', na=False).astype(int)
    df['Has_PartTime_Job'] = df['Funding_Source'].str.contains('Part-time Job', na=False).astype(int)
    df['Has_Scholarship'] = df['Funding_Source'].str.contains('Scholarship', na=False).astype(int)
    df['Has_Loan'] = df['Funding_Source'].str.contains('Loan', na=False).astype(int)
    df['Has_Savings'] = df['Funding_Source'].str.contains('Savings', na=False).astype(int)
    
    # Cost of Living Index
    df['Cost_of_Living_Index'] = (
        (6 - df['Affordability_Accommodation_Score']) * 0.4 +
        (6 - df['Affordability_Food_Score']) * 0.3 +
        (6 - df['Affordability_Transport_Score']) * 0.2 +
        (6 - df['Affordability_Materials_Score']) * 0.1
    )
    
    # Create target variables
    df['Estimated_Food_Cost'] = df['Monthly_Income_Numeric'] * 0.35 * (df['Cost_of_Living_Index'] / 3)
    df['Estimated_Accommodation_Cost'] = df['Monthly_Income_Numeric'] * 0.30 * (6 - df['Affordability_Accommodation_Score']) / 3
    df['Estimated_Transport_Cost'] = df['Transport_Cost_Numeric']
    df['Estimated_Other_Expenses'] = df['Monthly_Income_Numeric'] * 0.15
    
    df['Total_Monthly_Expenses'] = (
        df['Estimated_Food_Cost'] + df['Estimated_Accommodation_Cost'] +
        df['Estimated_Transport_Cost'] + df['Estimated_Other_Expenses']
    )
    
    df['Savings'] = df['Monthly_Income_Numeric'] - df['Total_Monthly_Expenses']
    df['Savings_Rate'] = (df['Savings'] / df['Monthly_Income_Numeric']) * 100
    df['Financial_Risk'] = (
        (df['Savings_Rate'] < 10) | (df['Financial_Comfort_Score'] <= 2)
    ).astype(int)
    
    # Prepare features
    feature_columns = [
        'Monthly_Income_Numeric', 'Transport_Cost_Numeric', 'Work_Hours_Numeric',
        'Financial_Comfort_Score', 'Affordability_Accommodation_Score',
        'Affordability_Food_Score', 'Affordability_Materials_Score',
        'Affordability_Transport_Score', 'Affordability_Social_Score',
        'Has_Parental_Support', 'Has_PartTime_Job', 'Has_Scholarship',
        'Has_Loan', 'Has_Savings', 'Cost_of_Living_Index'
    ]
    
    X = df[feature_columns].copy()
    y_expenses = df['Total_Monthly_Expenses'].copy()
    y_risk = df['Financial_Risk'].copy()
    
    # Handle missing values
    X.fillna(X.median(), inplace=True)
    
    # Split data
    X_train, X_test, y_train_exp, y_test_exp, y_train_risk, y_test_risk = train_test_split(
        X, y_expenses, y_risk, test_size=0.2, random_state=42
    )
    
    # Scale features
    X_test_scaled = scaler.transform(X_test)
    
    print(f"✅ Prepared test data: {len(X_test)} samples")
    print(f"   Features: {len(feature_columns)}")
    
except Exception as e:
    print(f"❌ Error preparing data: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test Budget Prediction Model
print("\n" + "="*80)
print("💰 BUDGET PREDICTION MODEL ACCURACY")
print("="*80 + "\n")

try:
    # Make predictions
    y_pred_exp = gbr_model.predict(X_test_scaled)
    
    # Calculate metrics
    mae = mean_absolute_error(y_test_exp, y_pred_exp)
    rmse = np.sqrt(mean_squared_error(y_test_exp, y_pred_exp))
    r2 = r2_score(y_test_exp, y_pred_exp)
    mape = np.mean(np.abs((y_test_exp - y_pred_exp) / y_test_exp)) * 100
    
    accuracy_percentage = r2 * 100
    
    print(f"📊 Model Type: {type(gbr_model).__name__}")
    print(f"\n🎯 Accuracy Metrics:")
    print(f"   ✅ R² Score: {r2:.4f} ({accuracy_percentage:.2f}%)")
    print(f"   📉 MAE (Mean Absolute Error): LKR {mae:,.2f}")
    print(f"   📉 RMSE (Root Mean Squared Error): LKR {rmse:,.2f}")
    print(f"   📉 MAPE (Mean Absolute Percentage Error): {mape:.2f}%")
    
    print(f"\n💡 What this means:")
    if accuracy_percentage >= 85:
        print(f"   🎉 EXCELLENT! Your model achieves {accuracy_percentage:.1f}% accuracy")
        print(f"   ✅ This is significantly better than your previous 67.4%")
    elif accuracy_percentage >= 75:
        print(f"   ✅ GOOD! Your model achieves {accuracy_percentage:.1f}% accuracy")
        print(f"   ✅ This is an improvement over your previous 67.4%")
    else:
        print(f"   ⚠️ Your model achieves {accuracy_percentage:.1f}% accuracy")
        print(f"   💡 Consider retraining with more features or different hyperparameters")
    
    print(f"\n📈 Average Prediction Error: LKR {mae:,.0f}")
    print(f"   For a student with LKR 30,000 budget, error is ±{mae:,.0f}")
    
except Exception as e:
    print(f"❌ Error testing budget model: {e}")
    import traceback
    traceback.print_exc()

# Test Risk Classification Model
print("\n" + "="*80)
print("⚠️ RISK CLASSIFICATION MODEL ACCURACY")
print("="*80 + "\n")

try:
    # Make predictions
    y_pred_risk = risk_classifier.predict(X_test_scaled)
    
    # Calculate accuracy
    clf_accuracy = accuracy_score(y_test_risk, y_pred_risk)
    
    print(f"📊 Model Type: {type(risk_classifier).__name__}")
    print(f"\n🎯 Classification Accuracy: {clf_accuracy*100:.2f}%")
    
    print(f"\n📋 Detailed Classification Report:")
    print(classification_report(y_test_risk, y_pred_risk, 
                                target_names=['Low Risk', 'High Risk'],
                                digits=4))
    
    print(f"\n💡 What this means:")
    if clf_accuracy >= 0.85:
        print(f"   🎉 EXCELLENT! Your risk classifier is {clf_accuracy*100:.1f}% accurate")
    elif clf_accuracy >= 0.75:
        print(f"   ✅ GOOD! Your risk classifier is {clf_accuracy*100:.1f}% accurate")
    else:
        print(f"   ⚠️ Your risk classifier is {clf_accuracy*100:.1f}% accurate")
    
except Exception as e:
    print(f"❌ Error testing risk classifier: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*80)
print("📊 OVERALL SUMMARY")
print("="*80 + "\n")

print(f"✅ Budget Prediction Accuracy: {accuracy_percentage:.2f}%")
print(f"✅ Risk Classification Accuracy: {clf_accuracy*100:.2f}%")
print(f"\n🎯 Average Error in Budget Predictions: ±LKR {mae:,.0f}")
print(f"📈 Your Previous Model: 67.4%")
print(f"📈 Your New Model: {accuracy_percentage:.2f}%")
print(f"🚀 Improvement: +{accuracy_percentage - 67.4:.2f}%")

print("\n" + "="*80)
print("✅ Model accuracy check complete!")
print("="*80 + "\n")
