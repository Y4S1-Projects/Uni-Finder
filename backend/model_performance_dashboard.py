#!/usr/bin/env python3
"""
ML Model Performance Dashboard
Real-time testing and accuracy verification for Budget Optimizer models
"""

import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_section(title):
    print("\n" + "-"*80)
    print(f"  {title}")
    print("-"*80)

# Main execution
if __name__ == "__main__":
    print_header("🎯 ML MODEL PERFORMANCE DASHBOARD")
    
    # Step 1: Load Models
    print("📥 Loading trained models...")
    
    try:
        gbr_model = joblib.load('budget_optimizer_files/budget_optimizer_gbr_model_final_optimized.pkl')
        print(f"✅ Budget Predictor: {type(gbr_model).__name__}")
    except Exception as e:
        print(f"❌ Error loading budget model: {e}")
        exit(1)
    
    try:
        risk_clf = joblib.load('budget_optimizer_files/risk_classifier_model_final.pkl')
        print(f"✅ Risk Classifier: {type(risk_clf).__name__}")
    except Exception as e:
        print(f"❌ Error loading risk classifier: {e}")
        exit(1)
    
    try:
        scaler = joblib.load('budget_optimizer_files/feature_preprocessor_final.pkl')
        print(f"✅ Feature Scaler: {type(scaler).__name__}")
    except Exception as e:
        print(f"❌ Error loading scaler: {e}")
        exit(1)
    
    # Step 2: Load and Prepare Data
    print_section("📊 Loading Survey Data")
    
    survey_df = pd.read_csv('budget_optimizer_files/Student Budget Survey.csv')
    print(f"✅ Loaded {len(survey_df)} student records")
    
    # Rename columns
    survey_df.columns = [
        'Timestamp', 'Academic_Level', 'Funding_Source', 'Monthly_Income',
        'Transport_Cost', 'Financial_Comfort', 'Affordability_Accommodation',
        'Affordability_Food', 'Affordability_Materials', 'Affordability_Transport',
        'Affordability_Social', 'Financial_Assistance_Needed', 'Work_Hours_Per_Week',
        'Additional_Comments'
    ]
    
    df = survey_df.copy()
    df = df.drop(['Timestamp', 'Additional_Comments'], axis=1)
    
    # Feature Engineering (matching ADVANCED training notebook - 16 features)
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
    
    df['Income'] = df['Monthly_Income'].apply(convert_income)
    df['Transport'] = pd.to_numeric(df['Transport_Cost'], errors='coerce')
    df['Transport'].fillna(df['Transport'].median(), inplace=True)
    
    def convert_work_hours(hours_str):
        if pd.isna(hours_str):
            return 0
        hours_map = {
            '0 hours': 0, '1-5 hours': 3, '6-10 hours': 8,
            '11-15 hours': 13, '16-20 hours': 18, 'More than 20 hours': 25
        }
        return hours_map.get(hours_str, 0)
    
    df['Work_Hours'] = df['Work_Hours_Per_Week'].apply(convert_work_hours)
    
    affordability_map = {
        'Very Affordable': 5, 'Affordable': 4, 'Neutral': 3,
        'Unaffordable': 2, 'Very Unaffordable': 1
    }
    
    # Use SHORT names matching the new model
    df['Aff_Accommodation'] = df['Affordability_Accommodation'].map(affordability_map).fillna(3)
    df['Aff_Food'] = df['Affordability_Food'].map(affordability_map).fillna(3)
    df['Aff_Materials'] = df['Affordability_Materials'].map(affordability_map).fillna(3)
    df['Aff_Transport'] = df['Affordability_Transport'].map(affordability_map).fillna(3)
    df['Aff_Social'] = df['Affordability_Social'].map(affordability_map).fillna(3)
    
    df['Comfort'] = pd.to_numeric(df['Financial_Comfort'], errors='coerce').fillna(3)
    
    df['Has_Parental'] = df['Funding_Source'].str.contains('Parental/Family', na=False).astype(int)
    df['Has_Job'] = df['Funding_Source'].str.contains('Part-time Job', na=False).astype(int)
    df['Has_Scholarship'] = df['Funding_Source'].str.contains('Scholarship', na=False).astype(int)
    df['Has_Loan'] = df['Funding_Source'].str.contains('Loan', na=False).astype(int)
    
    # NEW: Add the 3 advanced features from real pricing data
    # These should match what's calculated in training
    df['Food_Cost_Multiplier'] = 1.5  # Approximate from food_prices.csv
    df['Avg_District_Rent'] = 15000  # Approximate median from rentals
    df['Avg_Transport_Cost'] = 150  # Approximate from transport costs
    
    print(f"✅ Added 3 advanced pricing features")
    
    # Create targets (matching fixed training notebook logic)
    # Base percentages
    accommodation_pct = 0.50 - (df['Aff_Accommodation'] - 1) * 0.10  # 50% down to 10%
    food_pct = 0.35 - (df['Aff_Food'] - 1) * 0.05  # 35% down to 15%
    materials_pct = 0.10 - (df['Aff_Materials'] - 1) * 0.02  # 10% down to 2%
    social_pct = 0.10 - (df['Aff_Social'] - 1) * 0.02  # 10% down to 2%
    
    df['Estimated_Accommodation_Cost'] = df['Income'] * accommodation_pct
    df['Estimated_Food_Cost'] = df['Income'] * food_pct
    df['Estimated_Materials_Cost'] = df['Income'] * materials_pct
    df['Estimated_Social_Cost'] = df['Income'] * social_pct
    df['Estimated_Transport_Cost'] = df['Transport']
    
    df['Total_Monthly_Expenses'] = (
        df['Estimated_Accommodation_Cost'] + df['Estimated_Food_Cost'] +
        df['Estimated_Materials_Cost'] + df['Estimated_Social_Cost'] +
        df['Estimated_Transport_Cost']
    )
    
    df['Savings'] = df['Income'] - df['Total_Monthly_Expenses']
    df['Savings_Rate'] = (df['Savings'] / df['Income']) * 100
    df['Financial_Risk'] = ((df['Savings_Rate'] < 10) | (df['Comfort'] <= 2)).astype(int)
    
    # Prepare features - EXACT 16 features matching ADVANCED model
    feature_columns = [
        'Income', 'Transport', 'Work_Hours', 'Comfort',
        'Aff_Accommodation', 'Aff_Food', 'Aff_Materials', 'Aff_Transport', 'Aff_Social',
        'Has_Parental', 'Has_Job', 'Has_Scholarship', 'Has_Loan',
        'Food_Cost_Multiplier', 'Avg_District_Rent', 'Avg_Transport_Cost'
    ]
    
    X = df[feature_columns].copy()
    y_expenses = df['Total_Monthly_Expenses'].copy()
    y_risk = df['Financial_Risk'].copy()
    X.fillna(X.median(), inplace=True)
    
    # Split data (same random_state as training)
    X_train, X_test, y_train_exp, y_test_exp, y_train_risk, y_test_risk = train_test_split(
        X, y_expenses, y_risk, test_size=0.2, random_state=42
    )
    
    # Scale features
    X_test_scaled = scaler.transform(X_test)
    
    print(f"✅ Test set prepared: {len(X_test)} samples")
    print(f"✅ Features used: {len(feature_columns)}")
    
    # Step 3: Budget Prediction Model Evaluation
    print_header("💰 BUDGET PREDICTION MODEL - PERFORMANCE METRICS")
    
    y_pred_exp = gbr_model.predict(X_test_scaled)
    
    mae = mean_absolute_error(y_test_exp, y_pred_exp)
    rmse = np.sqrt(mean_squared_error(y_test_exp, y_pred_exp))
    r2 = r2_score(y_test_exp, y_pred_exp)
    mape = np.mean(np.abs((y_test_exp - y_pred_exp) / y_test_exp)) * 100
    
    accuracy_percentage = r2 * 100
    
    print(f"📊 Model: {type(gbr_model).__name__}")
    print(f"   • Estimators: {gbr_model.get_params()['n_estimators']}")
    if 'learning_rate' in gbr_model.get_params():
        print(f"   • Learning Rate: {gbr_model.get_params()['learning_rate']}")
    print(f"   • Max Depth: {gbr_model.get_params()['max_depth']}")
    
    print(f"\n🎯 ACCURACY: {accuracy_percentage:.2f}%")
    print(f"   ├─ R² Score: {r2:.4f}")
    print(f"   ├─ MAE: LKR {mae:,.2f}")
    print(f"   ├─ RMSE: LKR {rmse:,.2f}")
    print(f"   └─ MAPE: {mape:.2f}%")
    
    print(f"\n📈 Performance Rating:")
    if accuracy_percentage >= 90:
        print(f"   🏆 EXCELLENT - Your model is production-ready!")
    elif accuracy_percentage >= 85:
        print(f"   ⭐ VERY GOOD - High accuracy achieved!")
    elif accuracy_percentage >= 80:
        print(f"   ✅ GOOD - Solid performance")
    elif accuracy_percentage >= 75:
        print(f"   ⚠️  FAIR - Consider improvements")
    else:
        print(f"   ❌ NEEDS IMPROVEMENT")
    
    print(f"\n💡 What this means:")
    print(f"   • For a student with LKR 30,000 monthly expenses")
    print(f"   • Model predicts within ±LKR {mae:,.0f} on average")
    print(f"   • Error margin: {(mae/30000)*100:.1f}%")
    
    # Sample predictions
    print_section("🔍 Sample Predictions")
    
    sample_indices = np.random.choice(len(X_test), 5, replace=False)
    print(f"\n{'Actual':>12} | {'Predicted':>12} | {'Error':>12} | {'Error %':>10}")
    print("-" * 55)
    for idx in sample_indices:
        actual = y_test_exp.iloc[idx]
        predicted = y_pred_exp[idx]
        error = abs(actual - predicted)
        error_pct = (error / actual) * 100
        print(f"LKR {actual:>8,.0f} | LKR {predicted:>8,.0f} | LKR {error:>7,.0f} | {error_pct:>8.1f}%")
    
    # Step 4: Risk Classification Model Evaluation
    print_header("⚠️ RISK CLASSIFICATION MODEL - PERFORMANCE METRICS")
    
    y_pred_risk = risk_clf.predict(X_test_scaled)
    y_pred_risk_proba = risk_clf.predict_proba(X_test_scaled)
    
    clf_accuracy = accuracy_score(y_test_risk, y_pred_risk)
    
    print(f"📊 Model: {type(risk_clf).__name__}")
    print(f"   • Estimators: {risk_clf.get_params()['n_estimators']}")
    print(f"   • Max Depth: {risk_clf.get_params()['max_depth']}")
    
    print(f"\n🎯 ACCURACY: {clf_accuracy*100:.2f}%")
    
    print(f"\n📊 Classification Report:")
    print(classification_report(y_test_risk, y_pred_risk, 
                                target_names=['Low Risk', 'High Risk'],
                                digits=4))
    
    print(f"🔢 Confusion Matrix:")
    cm = confusion_matrix(y_test_risk, y_pred_risk)
    print(f"\n                 Predicted")
    print(f"              Low    High")
    print(f"Actual Low  | {cm[0][0]:>4} | {cm[0][1]:>4}")
    print(f"       High | {cm[1][0]:>4} | {cm[1][1]:>4}")
    
    # Calculate additional metrics
    true_negatives = cm[0][0]
    false_positives = cm[0][1]
    false_negatives = cm[1][0]
    true_positives = cm[1][1]
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\n📈 Additional Metrics:")
    print(f"   • Precision: {precision:.4f} ({precision*100:.2f}%)")
    print(f"   • Recall: {recall:.4f} ({recall*100:.2f}%)")
    print(f"   • F1-Score: {f1:.4f} ({f1*100:.2f}%)")
    
    # Step 5: Feature Importance
    print_header("🔬 FEATURE IMPORTANCE ANALYSIS")
    
    if hasattr(gbr_model, 'feature_importances_'):
        importance_df = pd.DataFrame({
            'Feature': feature_columns,
            'Importance': gbr_model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        print("💰 Budget Prediction - Top Features:")
        print(f"\n{'Rank':<6} {'Feature':<35} {'Importance':>12} {'%':>8}")
        print("-" * 65)
        for idx, row in importance_df.head(10).iterrows():
            pct = (row['Importance'] / importance_df['Importance'].sum()) * 100
            print(f"{importance_df.index.get_loc(idx)+1:<6} {row['Feature']:<35} {row['Importance']:>12.6f} {pct:>7.2f}%")
    
    if hasattr(risk_clf, 'feature_importances_'):
        importance_df_clf = pd.DataFrame({
            'Feature': feature_columns,
            'Importance': risk_clf.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        print("\n⚠️  Risk Classification - Top Features:")
        print(f"\n{'Rank':<6} {'Feature':<35} {'Importance':>12} {'%':>8}")
        print("-" * 65)
        for idx, row in importance_df_clf.head(10).iterrows():
            pct = (row['Importance'] / importance_df_clf['Importance'].sum()) * 100
            print(f"{importance_df_clf.index.get_loc(idx)+1:<6} {row['Feature']:<35} {row['Importance']:>12.6f} {pct:>7.2f}%")
    
    # Step 6: Overall Summary
    print_header("📊 OVERALL PERFORMANCE SUMMARY")
    
    print(f"✅ Budget Prediction Accuracy: {accuracy_percentage:.2f}%")
    print(f"✅ Risk Classification Accuracy: {clf_accuracy*100:.2f}%")
    print(f"\n📈 Improvement from Previous Model:")
    print(f"   • Previous: 67.4%")
    print(f"   • Current:  {accuracy_percentage:.2f}%")
    print(f"   • Gain:     +{accuracy_percentage - 67.4:.2f}%")
    
    print(f"\n🎯 Model Status:")
    if accuracy_percentage >= 85 and clf_accuracy >= 0.85:
        print(f"   🏆 PRODUCTION READY - Both models meet target accuracy!")
    elif accuracy_percentage >= 80 or clf_accuracy >= 0.80:
        print(f"   ⭐ GOOD PERFORMANCE - Models are usable in production")
    else:
        print(f"   ⚠️  NEEDS IMPROVEMENT - Consider retraining")
    
    print(f"\n💾 Model Files:")
    print(f"   • budget_optimizer_gbr_model_final_optimized.pkl")
    print(f"   • risk_classifier_model_final.pkl")
    print(f"   • feature_preprocessor_final.pkl")
    
    print("\n" + "="*80)
    print("✅ Performance analysis complete!")
    print("="*80 + "\n")
