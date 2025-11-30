#!/usr/bin/env python3
"""
ML Budget Predictor - Integration with trained models
Component of UniFinder LK Budget Optimizer
Uses pre-trained .pkl models for predictions
"""

import joblib
import pandas as pd
import numpy as np
import os
from datetime import datetime

class MLBudgetPredictor:
    """
    Load and use pre-trained ML models for budget prediction
    """
    
    def __init__(self, model_dir='budget_optimizer_files'):
        self.model_dir = model_dir
        self.gbr_model = None
        self.risk_classifier = None
        self.feature_preprocessor = None
        self.academic_calendar = None
        self.load_models()
        self.load_reference_data()
    
    def load_models(self):
        """Load pre-trained models from .pkl files"""
        try:
            # Load GBR model for budget optimization
            gbr_path = os.path.join(self.model_dir, 'budget_optimizer_gbr_model_final_optimized.pkl')
            if os.path.exists(gbr_path):
                self.gbr_model = joblib.load(gbr_path)
                print("✅ Loaded GBR Budget Optimizer Model")
            
            # Load Risk Classifier
            risk_path = os.path.join(self.model_dir, 'risk_classifier_model_final.pkl')
            if os.path.exists(risk_path):
                self.risk_classifier = joblib.load(risk_path)
                print("✅ Loaded Risk Classifier Model")
            
            # Load Feature Preprocessor
            preprocessor_path = os.path.join(self.model_dir, 'feature_preprocessor_final.pkl')
            if os.path.exists(preprocessor_path):
                self.feature_preprocessor = joblib.load(preprocessor_path)
                print("✅ Loaded Feature Preprocessor")
                
        except Exception as e:
            print(f"⚠️ Error loading models: {e}")
    
    def load_reference_data(self):
        """Load reference CSV files"""
        try:
            # Load academic calendar for dynamic adjustments
            calendar_path = os.path.join(self.model_dir, 'academic_calendar.csv')
            if os.path.exists(calendar_path):
                self.academic_calendar = pd.read_csv(calendar_path)
                print("✅ Loaded Academic Calendar")
                
        except Exception as e:
            print(f"⚠️ Error loading reference data: {e}")
    
    def preprocess_input(self, student_data):
        """
        Preprocess student data to match model's expected format
        
        Args:
            student_data: Dictionary with student information
        
        Returns:
            Processed features ready for model prediction
        """
        
        # Extract required features (adjust based on your model's training features)
        features = {
            'Estimated_Income_LKR': student_data.get('monthly_income', 25000),
            'Financial_Comfort_Level': student_data.get('financial_comfort_level', 3),
            'Academic_Level': student_data.get('year_of_study', 'Second Year'),
            'Student_District': student_data.get('district', 'Colombo'),
            'Accommodation_Type': student_data.get('accommodation_type', 'Rented Room'),
            'Monthly_Rent_LKR': student_data.get('rent', 8000),
            'Transport_Type': student_data.get('transport_method', 'Bus'),
            'Food_Type': student_data.get('food_type', 'Mixed'),
            'Degree_Program': student_data.get('field_of_study', 'IT'),
            'University': student_data.get('university', 'SLIIT'),
            'Year_in_Program': self._extract_year_number(student_data.get('year_of_study', 'Second Year')),
            'Meals_Per_Day': self._extract_meals_count(student_data.get('meals_per_day', '3 meals')),
            'Home_Visit_Frequency': student_data.get('home_visit_frequency', 'Monthly')
        }
        
        # Create DataFrame
        df = pd.DataFrame([features])
        
        # Use preprocessor if available
        if self.feature_preprocessor is not None:
            try:
                processed_features = self.feature_preprocessor.transform(df)
                return processed_features
            except Exception as e:
                print(f"⚠️ Preprocessing error: {e}")
                return df
        
        return df
    
    def _extract_year_number(self, year_string):
        """Extract year number from string like 'Second Year'"""
        year_map = {
            'First Year': 1,
            'Second Year': 2,
            'Third Year': 3,
            'Fourth Year': 4
        }
        return year_map.get(year_string, 2)
    
    def _extract_meals_count(self, meals_string):
        """Extract number of meals from string"""
        if '2 meals' in meals_string:
            return 2
        elif '3 meals + snacks' in meals_string:
            return 3.5
        else:
            return 3
    
    def predict_budget(self, student_data):
        """
        Predict optimal budget using GBR model
        
        Args:
            student_data: Student information dictionary
        
        Returns:
            Dictionary with budget predictions
        """
        
        if self.gbr_model is None:
            return self._fallback_prediction(student_data)
        
        try:
            # Preprocess input
            features = self.preprocess_input(student_data)
            
            # Make prediction
            predicted_budget = self.gbr_model.predict(features)[0]
            
            # Apply dynamic adjustments based on academic calendar
            adjusted_budget = self._apply_dynamic_adjustments(predicted_budget, student_data)
            
            # Calculate component breakdown
            breakdown = self._calculate_budget_breakdown(adjusted_budget, student_data)
            
            return {
                'predicted_optimal_budget': round(adjusted_budget, 2),
                'breakdown': breakdown,
                'confidence': self._calculate_confidence(),
                'model_used': 'GBR_Optimized',
                'prediction_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return self._fallback_prediction(student_data)
    
    def predict_risk(self, student_data):
        """
        Predict financial risk level
        
        Args:
            student_data: Student information dictionary
        
        Returns:
            Dictionary with risk prediction
        """
        
        if self.risk_classifier is None:
            return {'risk_level': 'Unknown', 'risk_score': 0.5}
        
        try:
            # Preprocess input
            features = self.preprocess_input(student_data)
            
            # Make prediction
            risk_prediction = self.risk_classifier.predict(features)[0]
            risk_probability = self.risk_classifier.predict_proba(features)[0]
            
            risk_level = 'High Risk' if risk_prediction == 1 else 'Low Risk'
            risk_score = risk_probability[1] if len(risk_probability) > 1 else 0.5
            
            # Generate recommendations based on risk
            recommendations = self._generate_risk_recommendations(risk_level, student_data)
            
            return {
                'risk_level': risk_level,
                'risk_score': round(float(risk_score), 3),
                'risk_probability': round(float(risk_score) * 100, 1),
                'recommendations': recommendations
            }
            
        except Exception as e:
            print(f"❌ Risk prediction error: {e}")
            return {
                'risk_level': 'Unknown',
                'risk_score': 0.5,
                'recommendations': []
            }
    
    def _apply_dynamic_adjustments(self, base_budget, student_data):
        """
        Apply dynamic adjustments based on academic calendar
        """
        
        if self.academic_calendar is None:
            return base_budget
        
        try:
            current_month = datetime.now().month
            
            # Check if current month is exam period or study leave
            calendar_data = self.academic_calendar[
                self.academic_calendar['Month'] == current_month
            ]
            
            if not calendar_data.empty:
                period_type = calendar_data.iloc[0].get('Period_Type', 'Regular')
                
                # Increase budget during exam/study periods
                if 'Exam' in period_type or 'Study' in period_type:
                    adjustment_factor = 1.15  # 15% increase
                    adjusted_budget = base_budget * adjustment_factor
                    print(f"📚 Applied dynamic adjustment: {period_type} (+15%)")
                    return adjusted_budget
            
        except Exception as e:
            print(f"⚠️ Dynamic adjustment error: {e}")
        
        return base_budget
    
    def _calculate_budget_breakdown(self, total_budget, student_data):
        """
        Break down total budget into categories
        """
        
        # Standard percentage allocations
        breakdown_percentages = {
            'food': 0.35,
            'accommodation': 0.30,
            'transport': 0.15,
            'study_materials': 0.10,
            'entertainment': 0.05,
            'other': 0.05
        }
        
        breakdown = {}
        for category, percentage in breakdown_percentages.items():
            breakdown[category] = round(total_budget * percentage, 2)
        
        return breakdown
    
    def _calculate_confidence(self):
        """
        Calculate model confidence score
        (Placeholder - should use actual model metrics)
        """
        return 86.89  # Your stated model accuracy
    
    def _generate_risk_recommendations(self, risk_level, student_data):
        """
        Generate personalized recommendations based on risk level
        """
        
        recommendations = []
        
        if risk_level == 'High Risk':
            income = student_data.get('monthly_income', 25000)
            rent = student_data.get('rent', 8000)
            food = student_data.get('food_budget', 10000)
            
            # Check if rent is too high
            if rent / income > 0.35:
                recommendations.append({
                    'category': 'Accommodation',
                    'message': f'Your rent (LKR {rent}) is {round((rent/income)*100, 1)}% of income. Consider finding cheaper accommodation.',
                    'priority': 'High',
                    'potential_savings': round(rent * 0.2, 2)
                })
            
            # Check if food budget is high
            if food / income > 0.40:
                recommendations.append({
                    'category': 'Food',
                    'message': f'Food expenses are {round((food/income)*100, 1)}% of income. Try cooking more at home.',
                    'priority': 'Medium',
                    'potential_savings': round(food * 0.15, 2)
                })
            
            # General savings advice
            recommendations.append({
                'category': 'Savings',
                'message': 'Create an emergency fund of at least LKR 5,000 per month.',
                'priority': 'High',
                'potential_savings': 5000
            })
        else:
            recommendations.append({
                'category': 'General',
                'message': 'Your budget is well-balanced. Consider increasing your savings goal.',
                'priority': 'Low',
                'potential_savings': 0
            })
        
        return recommendations
    
    def _fallback_prediction(self, student_data):
        """
        Fallback prediction when model is not available
        """
        
        income = student_data.get('monthly_income', 25000)
        
        # Rule-based estimation
        estimated_budget = {
            'food': income * 0.35,
            'accommodation': student_data.get('rent', income * 0.30),
            'transport': income * 0.15,
            'study_materials': income * 0.10,
            'entertainment': income * 0.05,
            'other': income * 0.05
        }
        
        total = sum(estimated_budget.values())
        
        return {
            'predicted_optimal_budget': round(total, 2),
            'breakdown': {k: round(v, 2) for k, v in estimated_budget.items()},
            'confidence': 75.0,
            'model_used': 'Rule_Based_Fallback',
            'prediction_date': datetime.now().isoformat()
        }
    
    def generate_complete_analysis(self, student_data):
        """
        Generate complete budget analysis with predictions and risk assessment
        
        Args:
            student_data: Complete student information
        
        Returns:
            Comprehensive analysis dictionary
        """
        
        # Get budget prediction
        budget_prediction = self.predict_budget(student_data)
        
        # Get risk assessment
        risk_assessment = self.predict_risk(student_data)
        
        # Calculate savings potential
        monthly_income = student_data.get('monthly_income', 25000)
        predicted_expenses = budget_prediction['predicted_optimal_budget']
        savings_potential = monthly_income - predicted_expenses
        
        # Generate optimization recommendation
        if savings_potential < 0:
            optimization_status = 'Over Budget'
            recommendation = 'Your expenses exceed income. Immediate budget adjustments needed.'
        elif savings_potential < monthly_income * 0.10:
            optimization_status = 'Tight Budget'
            recommendation = 'You have minimal savings. Consider reducing discretionary spending.'
        else:
            optimization_status = 'Healthy Budget'
            recommendation = 'Your budget is balanced. Continue monitoring and save consistently.'
        
        return {
            'status': 'success',
            'budget_prediction': budget_prediction,
            'risk_assessment': risk_assessment,
            'financial_summary': {
                'monthly_income': monthly_income,
                'predicted_expenses': round(predicted_expenses, 2),
                'savings_potential': round(savings_potential, 2),
                'savings_rate': round((savings_potential / monthly_income) * 100, 1) if monthly_income > 0 else 0,
                'optimization_status': optimization_status
            },
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        }


# Example usage
if __name__ == '__main__':
    predictor = MLBudgetPredictor()
    
    # Test prediction
    test_student = {
        'monthly_income': 30000,
        'year_of_study': 'Second Year',
        'field_of_study': 'Engineering',
        'district': 'Colombo',
        'accommodation_type': 'Rented Room',
        'rent': 10000,
        'transport_method': 'Bus',
        'food_type': 'Mixed',
        'university': 'SLIIT',
        'meals_per_day': '3 meals',
        'home_visit_frequency': 'Monthly'
    }
    
    analysis = predictor.generate_complete_analysis(test_student)
    print("\n" + "="*60)
    print("📊 BUDGET ANALYSIS RESULTS")
    print("="*60)
    print(f"\n💰 Monthly Income: LKR {analysis['financial_summary']['monthly_income']}")
    print(f"📉 Predicted Expenses: LKR {analysis['financial_summary']['predicted_expenses']}")
    print(f"💵 Savings Potential: LKR {analysis['financial_summary']['savings_potential']}")
    print(f"📊 Savings Rate: {analysis['financial_summary']['savings_rate']}%")
    print(f"\n⚠️ Risk Level: {analysis['risk_assessment']['risk_level']}")
    print(f"🎯 Recommendation: {analysis['recommendation']}")
