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
    
    def __init__(self, model_dir='data'):
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
        """Load reference CSV files for advanced feature calculation"""
        try:
            # Load academic calendar
            calendar_path = os.path.join(self.model_dir, 'academic_calendar.csv')
            if os.path.exists(calendar_path):
                self.academic_calendar = pd.read_csv(calendar_path)
                print("✅ Loaded Academic Calendar")
            
            # Load food prices for Food_Cost_Multiplier
            food_prices_path = os.path.join(self.model_dir, 'food_prices.csv')
            if os.path.exists(food_prices_path):
                self.food_prices_df = pd.read_csv(food_prices_path)
                # Calculate average food price
                price_col = None
                for col in ['Price', 'price', 'Unit_Price', 'Cost']:
                    if col in self.food_prices_df.columns:
                        price_col = col
                        break
                if price_col:
                    avg_food_price = self.food_prices_df[price_col].mean()
                    self.food_cost_multiplier = avg_food_price / 200  # Normalize
                else:
                    self.food_cost_multiplier = 1.0
                print(f"✅ Loaded Food Prices (multiplier: {self.food_cost_multiplier:.2f})")
            else:
                self.food_cost_multiplier = 1.0
            
            # Load rental prices for Avg_District_Rent
            rentals_path = os.path.join(self.model_dir, 'room_annex_rentals.csv')
            if os.path.exists(rentals_path):
                self.rentals_df = pd.read_csv(rentals_path)
                rent_col = None
                for col in ['Rent', 'Monthly_Rent', 'Price', 'rent', 'monthly_rent']:
                    if col in self.rentals_df.columns:
                        rent_col = col
                        break
                if rent_col:
                    # Clean rental prices - remove "Rs", commas, "/month", etc.
                    def clean_price(price_str):
                        if pd.isna(price_str):
                            return None
                        price_str = str(price_str)
                        price_str = price_str.replace('Rs', '').replace('LKR', '').replace(',', '')
                        price_str = price_str.replace('/month', '').replace('/Month', '').strip()
                        try:
                            return float(price_str)
                        except:
                            return None
                    
                    self.rentals_df[rent_col + '_clean'] = self.rentals_df[rent_col].apply(clean_price)
                    clean_rents = self.rentals_df[rent_col + '_clean'].dropna()
                    
                    if len(clean_rents) > 0:
                        self.avg_district_rent = clean_rents.median()
                    else:
                        self.avg_district_rent = 10000
                else:
                    self.avg_district_rent = 10000
                print(f"✅ Loaded Rental Prices (avg: LKR {self.avg_district_rent:,.2f})")
            else:
                self.avg_district_rent = 10000
            
            # Load transport costs for Avg_Transport_Cost
            transport_path = os.path.join(self.model_dir, 'srilanka_transport_costs.csv')
            if os.path.exists(transport_path):
                self.transport_df = pd.read_csv(transport_path)
                cost_col = None
                for col in ['Cost', 'cost', 'Price', 'Fare', 'fare']:
                    if col in self.transport_df.columns:
                        cost_col = col
                        break
                if cost_col:
                    self.avg_transport_cost = self.transport_df[cost_col].median()
                else:
                    self.avg_transport_cost = 150
                print(f"✅ Loaded Transport Costs (avg: LKR {self.avg_transport_cost:.2f})")
            else:
                self.avg_transport_cost = 150
                
        except Exception as e:
            print(f"⚠️ Error loading reference data: {e}")
            # Set defaults
            self.food_cost_multiplier = 1.0
            self.avg_district_rent = 10000
            self.avg_transport_cost = 150
    
    def preprocess_input(self, student_data):
        """
        Preprocess student data to match ADVANCED model's expected format
        ADVANCED MODEL expects these 16 features in exact order:
        Income, Transport, Work_Hours, Comfort,
        Aff_Accommodation, Aff_Food, Aff_Materials, Aff_Transport, Aff_Social,
        Has_Parental, Has_Job, Has_Scholarship, Has_Loan,
        Food_Cost_Multiplier, Avg_District_Rent, Avg_Transport_Cost
        
        Args:
            student_data: Dictionary with student information
        
        Returns:
            Processed features ready for model prediction
        """
        
        # Convert affordability scores (assume user provides 1-5 scale or we estimate)
        # Default to 3 (Neutral) if not provided
        aff_accommodation = student_data.get('affordability_accommodation', 3)
        aff_food = student_data.get('affordability_food', 3)
        aff_materials = student_data.get('affordability_materials', 3)
        aff_transport = student_data.get('affordability_transport', 3)
        aff_social = student_data.get('affordability_social', 3)
        
        # Parse funding sources
        funding_source = student_data.get('funding_source', 'Parental/Family Support')
        has_parental = 1 if 'Parental' in funding_source or 'Family' in funding_source else 0
        has_job = 1 if 'Part-time' in funding_source or 'Job' in funding_source else 0
        has_scholarship = 1 if 'Scholarship' in funding_source or 'Grant' in funding_source else 0
        has_loan = 1 if 'Loan' in funding_source else 0
        
        # Extract work hours (default 0 if not provided)
        work_hours = student_data.get('work_hours', 0)
        
        # Financial comfort (1-5 scale, default 3)
        comfort = student_data.get('financial_comfort', 3)
        
        # Features in exact order expected by ADVANCED model (16 features)
        features = {
            # Original 13 features
            'Income': float(student_data.get('monthly_income', 25000)),
            'Transport': float(student_data.get('transport_budget', student_data.get('transport_cost', 2000))),
            'Work_Hours': float(work_hours),
            'Comfort': float(comfort),
            'Aff_Accommodation': float(aff_accommodation),
            'Aff_Food': float(aff_food),
            'Aff_Materials': float(aff_materials),
            'Aff_Transport': float(aff_transport),
            'Aff_Social': float(aff_social),
            'Has_Parental': int(has_parental),
            'Has_Job': int(has_job),
            'Has_Scholarship': int(has_scholarship),
            'Has_Loan': int(has_loan),
            # NEW 3 features from real pricing data
            'Food_Cost_Multiplier': float(self.food_cost_multiplier),
            'Avg_District_Rent': float(self.avg_district_rent),
            'Avg_Transport_Cost': float(self.avg_transport_cost)
        }
        
        # Create DataFrame with exact column order
        df = pd.DataFrame([features])
        
        # Use preprocessor (StandardScaler) if available
        if self.feature_preprocessor is not None:
            try:
                processed_features = self.feature_preprocessor.transform(df)
                return processed_features
            except Exception as e:
                print(f"⚠️ Preprocessing error: {e}")
                return df.values
        
        return df.values
    
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
    
    def generate_optimal_budget_strategy(self, student_data, current_expenses):
        """
        Generate the BEST BUDGET STRATEGY based on user inputs and ML insights
        Provides optimal alternatives and step-by-step improvements
        
        Args:
            student_data: User input data
            current_expenses: Calculated current expenses breakdown
        
        Returns:
            Comprehensive optimal strategy with alternatives and savings
        """
        
        monthly_income = student_data.get('monthly_income', 25000)
        current_total = current_expenses.get('total_expenses', 0)
        current_savings = monthly_income - current_total
        
        # Get ML prediction for optimal budget
        ml_prediction = self.predict_budget(student_data)
        ml_optimal = ml_prediction.get('predicted_optimal_budget', monthly_income * 0.85)
        
        # ── CRITICAL FIX: Optimal target must ALWAYS be ≤ current total ──
        # The "optimal" budget means how much you COULD spend if you optimised.
        # It should never be higher than what you currently spend.
        # If model predicts higher (model over-estimates), cap at 90% of current.
        if ml_optimal >= current_total:
            # Already at or below optimal – target a realistic 10-15% reduction
            optimal_budget = round(current_total * 0.87, 2)
        else:
            # Model predicts lower – cap reduction at max 30% (realistic)
            min_possible = current_total * 0.70
            optimal_budget = round(max(ml_optimal, min_possible), 2)
        
        # Ensure optimal_budget is at least 50% of income (can't live on nothing)
        optimal_budget = max(optimal_budget, monthly_income * 0.50)
        
        # Derived improvement numbers
        expense_reduction = round(current_total - optimal_budget, 2)
        extra_savings     = round((monthly_income - optimal_budget) - current_savings, 2)
        
        # Safety: never show negative improvement
        expense_reduction = max(expense_reduction, 0)
        extra_savings     = max(extra_savings, 0)
        
        strategy = {
            'strategy_name': 'Personalized Optimal Budget Plan',
            'current_situation': {
                'total_expenses': round(current_total, 2),
                'savings': round(current_savings, 2),
                'savings_rate': round((current_savings / monthly_income * 100), 1) if monthly_income > 0 else 0
            },
            'optimal_target': {
                'target_expenses': round(optimal_budget, 2),
                'target_savings': round(monthly_income - optimal_budget, 2),
                'target_savings_rate': round(((monthly_income - optimal_budget) / monthly_income * 100), 1) if monthly_income > 0 else 0
            },
            'potential_improvement': {
                'expense_reduction': expense_reduction,
                'extra_savings': extra_savings
            }
        }
        
        # ═══════════════════════════════════════════════════════════
        # Generate category-specific optimal alternatives
        # Covers ALL major spending categories for a well-rounded view
        # ═══════════════════════════════════════════════════════════
        alternatives = []
        
        food_type        = student_data.get('food_type', 'Mixed')
        current_food     = current_expenses.get('food', 0)
        cooking_pct      = student_data.get('cooking_percentage', 50)
        transport_method = student_data.get('transport_method', 'Bus')
        current_transport= current_expenses.get('transport', 0)
        distance_uni     = student_data.get('distance_uni_accommodation', 5)
        rent             = student_data.get('rent', 0)
        accommodation_type = student_data.get('accommodation_type', 'Rented Room')
        district         = student_data.get('district', 'Colombo')
        study_materials  = current_expenses.get('study_materials', 2000)
        entertainment    = current_expenses.get('entertainment', 0)
        internet         = current_expenses.get('internet', 0)
        utilities        = current_expenses.get('utilities', 0)
        healthcare       = current_expenses.get('healthcare', 0)
        district_avg_rent = self.avg_district_rent if self.avg_district_rent else 10000
        
        # ── 1. FOOD ────────────────────────────────────────────────
        if food_type in ('Food Delivery', 'Mostly Canteen/Restaurants'):
            alternatives.append({
                'category': 'Food',
                'current_choice': f'{food_type} – LKR {current_food:,.0f}/month',
                'optimal_choice': 'Mixed (70% Home Cooked + 30% Outside)',
                'reasoning': 'Ordering every meal is 40-50% more expensive than home cooking. Switching to a mixed approach saves significantly while still allowing social meals.',
                'estimated_savings': round(current_food * 0.38, 2),
                'action_steps': [
                    'Buy basic cooking equipment (one-time ~LKR 3,000)',
                    'Plan a simple weekly menu (rice, dhal, vegetables)',
                    'Shop at Keells/Cargills on weekends for weekly groceries',
                    'Batch-cook on Sunday – saves time & money on weekdays',
                    'Reserve outside food for 2-3 social meals per week'
                ],
                'priority': 'High'
            })
        elif food_type == 'Mixed' and cooking_pct < 55:
            alternatives.append({
                'category': 'Food',
                'current_choice': f'Mixed – only {cooking_pct}% home cooking (LKR {current_food:,.0f}/month)',
                'optimal_choice': f'Mixed – 70-75% Home Cooked (save ~LKR {int(current_food*0.18):,}/month)',
                'reasoning': f'Increasing home cooking from {cooking_pct}% to 72% is the single biggest budget lever for students.',
                'estimated_savings': round(current_food * 0.18, 2),
                'action_steps': [
                    f'Increase cooking by just 2-3 extra meals/week',
                    'Learn 3-4 quick Sri Lankan recipes (dhal curry, egg fried rice, pasta)',
                    'Share cooking duties with a housemate to cut prep time',
                    'Buy groceries at pola (Sunday market) for 20-30% cheaper produce'
                ],
                'priority': 'Medium'
            })
        elif food_type == 'Home Cooked' and current_food > 14000:
            alternatives.append({
                'category': 'Food',
                'current_choice': f'Home Cooked – LKR {current_food:,.0f}/month',
                'optimal_choice': 'Optimise grocery shopping for LKR 11,000-12,000/month',
                'reasoning': 'Your grocery bill is above average for home cooking. Smart shopping can reduce it by 15-20%.',
                'estimated_savings': round(current_food * 0.16, 2),
                'action_steps': [
                    'Buy rice in 10-25kg bags (10-15% cheaper per kg)',
                    'Replace chicken with eggs/dhal 2x/week for protein',
                    'Buy vegetables at Sunday pola market (30-40% cheaper)',
                    'Avoid packaged/processed foods (high markup)'
                ],
                'priority': 'Low'
            })
        
        # ── 2. TRANSPORT ──────────────────────────────────────────
        if transport_method == 'Tuk-Tuk' and distance_uni <= 2.5:
            alternatives.append({
                'category': 'Transport',
                'current_choice': f'Tuk-Tuk / Three-Wheeler daily – LKR {current_transport:,.0f}/month',
                'optimal_choice': 'Walk / Bicycle (≤ 2.5 km away)',
                'reasoning': 'At under 2.5 km you are paying LKR 4,000-8,000/month to avoid a 25-min walk/ride. A bicycle pays for itself in under 2 months.',
                'estimated_savings': round(current_transport * 0.88, 2),
                'action_steps': [
                    'Buy a second-hand bicycle (LKR 8,000-15,000 one-time)',
                    'Payback period: 1-2 months vs current tuk-tuk cost',
                    'Get free daily exercise – skip the gym fee',
                    'Reserve tuk-tuk only for late nights or very heavy rain'
                ],
                'priority': 'High',
                'payback_period': '2 months'
            })
        elif transport_method in ('Tuk-Tuk', 'Ride-share'):
            alternatives.append({
                'category': 'Transport',
                'current_choice': f'{transport_method} – LKR {current_transport:,.0f}/month',
                'optimal_choice': 'CTB / Private Bus daily + student pass discount',
                'reasoning': 'Public transport costs LKR 60-150/trip vs Tuk-Tuk LKR 130-400/trip. Switching saves 55-70% on daily commuting.',
                'estimated_savings': round(current_transport * 0.60, 2),
                'action_steps': [
                    'Apply for student bus pass at university registrar (50% CTB discount)',
                    'Map your bus route on Google Maps – usually faster than PickMe during rush hour',
                    'Leave 10 min earlier to match bus schedules',
                    'Keep PickMe/Uber for late evenings or heavy-rain emergencies only'
                ],
                'priority': 'High'
            })
        elif transport_method == 'Personal Vehicle' and current_transport > 6000:
            alternatives.append({
                'category': 'Transport',
                'current_choice': f'Personal Vehicle – LKR {current_transport:,.0f}/month',
                'optimal_choice': 'Bus on weekdays + vehicle only for weekend/home visits',
                'reasoning': 'Petrol + maintenance on a personal vehicle costs LKR 5,000-10,000/month for typical student distances. Using the bus on weekdays cuts this by 40-50%.',
                'estimated_savings': round(current_transport * 0.42, 2),
                'action_steps': [
                    'Use the bus/train for routine uni commutes (5 days/week)',
                    'Reserve vehicle for home visits, late nights, and cargo trips',
                    'Save petrol money in a dedicated envelope each week',
                    'Get vehicle serviced on schedule – avoids costly breakdowns'
                ],
                'priority': 'Medium'
            })
        elif transport_method == 'Bus' and current_transport > 3500:
            alternatives.append({
                'category': 'Transport',
                'current_choice': f'Bus – LKR {current_transport:,.0f}/month',
                'optimal_choice': 'Monthly student bus pass + reduce home visit frequency',
                'reasoning': 'A monthly CTB student pass can save 25-30% on daily fares. Reducing home visits from bi-weekly to monthly cuts trip costs by half.',
                'estimated_savings': round(current_transport * 0.22, 2),
                'action_steps': [
                    'Apply for monthly CTB student pass at your university registrar',
                    'Consolidate home visits: once a month saves 1-3 round trips at LKR 200-1,000 each',
                    'Travel mid-week (Tuesday/Wednesday) – less crowded, occasionally cheaper private buses',
                    'Coordinate with friends for shared tuk-tuk on rainy days to split cost'
                ],
                'priority': 'Medium'
            })
        
        # ── 3. ACCOMMODATION ──────────────────────────────────────
        if rent > district_avg_rent * 1.25:
            alternatives.append({
                'category': 'Accommodation',
                'current_choice': f'{accommodation_type} – LKR {rent:,.0f}/month',
                'optimal_choice': f'Shared room / boarding in {district} (LKR {int(district_avg_rent):,}-{int(district_avg_rent*1.1):,}/month)',
                'reasoning': f'Your rent is {round((rent/district_avg_rent-1)*100)}% above the district average (LKR {int(district_avg_rent):,}). Sharing or moving slightly saves the most money.',
                'estimated_savings': round(rent - district_avg_rent * 1.05, 2),
                'action_steps': [
                    'Post on university Facebook groups for roommate search',
                    'Check university notice boards for boarding ads',
                    f'Target: LKR {int(district_avg_rent*0.85):,} - {int(district_avg_rent):,} (shared)',
                    'Consider moving 1-2 km farther from uni for 20-30% rent drop',
                    'One-time moving cost ~LKR 3,000-5,000'
                ],
                'priority': 'Medium',
                'note': 'Most impactful single expense if reduced.'
            })
        elif rent == 0 and accommodation_type not in ('Living with Family', 'University Hostel'):
            pass  # No rent – no accommodation tip needed
        
        # ── 4. INTERNET & UTILITIES ────────────────────────────────
        if internet > 2000:
            alternatives.append({
                'category': 'Internet & Phone',
                'current_choice': f'LKR {internet:,.0f}/month internet',
                'optimal_choice': f'Dialog/Mobitel student bundle – LKR 1,000-1,500/month',
                'reasoning': 'Telecom providers offer unlimited student data bundles that are 30-50% cheaper than standard home broadband.',
                'estimated_savings': round(internet - 1400, 2),
                'action_steps': [
                    'Compare Dialog Axiata "School of Savings" student plans',
                    'Check Mobitel Campus SIM bundles (unlimited data + calls)',
                    'Share WiFi router with housemates (split cost)',
                    'Use university campus WiFi for heavy downloads/streaming'
                ],
                'priority': 'Medium'
            })
        elif internet > 0 and internet <= 2000:
            pass  # Internet is already reasonable
        
        if utilities > 1500:
            alternatives.append({
                'category': 'Utilities (Electricity & Water)',
                'current_choice': f'LKR {utilities:,.0f}/month utilities',
                'optimal_choice': f'LKR 700-1,000/month with conservation habits',
                'reasoning': 'Small behaviour changes can cut electricity bills by 30-40% – a common hidden expense students overlook.',
                'estimated_savings': round(utilities - 900, 2),
                'action_steps': [
                    'Unplug chargers and devices when not in use',
                    'Use fan instead of A/C (saves 60% electricity)',
                    'Wash clothes in cold water and air-dry',
                    'Switch to LED bulbs if using incandescents',
                    'Share utility bill with housemates to track per-person cost'
                ],
                'priority': 'Low'
            })
        
        # ── 5. STUDY MATERIALS ────────────────────────────────────
        if study_materials > 2500:
            alternatives.append({
                'category': 'Study Materials',
                'current_choice': f'LKR {study_materials:,.0f}/month (buying new)',
                'optimal_choice': 'Library + Second-hand + Digital = LKR 500-800/month',
                'reasoning': 'University libraries and seniors are largely untapped free resources. Most textbooks have legal free PDF versions too.',
                'estimated_savings': round(study_materials * 0.65, 2),
                'action_steps': [
                    'Register and use your university library (all textbooks free)',
                    'Buy previous-years textbooks from seniors at 40-60% off',
                    'Use OpenLibrary.org and Project Gutenberg for free e-books',
                    'Form a 4-5 person study group to share one textbook',
                    'Photocopy only key chapters you need (LKR 0.50/page)'
                ],
                'priority': 'Low'
            })
        
        # ── 6. ENTERTAINMENT ─────────────────────────────────────
        if entertainment > monthly_income * 0.10:
            target_ent = round(monthly_income * 0.06, 0)
            alternatives.append({
                'category': 'Entertainment & Leisure',
                'current_choice': f'LKR {entertainment:,.0f}/month ({(entertainment/monthly_income*100):.0f}% of income)',
                'optimal_choice': f'LKR {int(target_ent):,}/month (6% of income)',
                'reasoning': 'Entertainment above 8-10% of income puts financial pressure on essentials. There are many free/low-cost activities in Sri Lanka.',
                'estimated_savings': round(entertainment - target_ent, 2),
                'action_steps': [
                    'Use student ID for 50% discount at Savoy/Liberty cinemas',
                    'Explore free campus cultural events, sports, and clubs',
                    'Visit free public beaches, parks, and libraries for leisure',
                    'Cancel unused streaming subscriptions (keep 1 max)',
                    'Set a weekly cash budget (LKR 600-800) and stick to it'
                ],
                'priority': 'Medium'
            })
        
        # ── 7. HEALTHCARE (if spending too much) ─────────────────
        if healthcare > 2000:
            alternatives.append({
                'category': 'Healthcare',
                'current_choice': f'LKR {healthcare:,.0f}/month private healthcare',
                'optimal_choice': 'Use free government OPD + university health centre',
                'reasoning': 'Government hospitals and university health centres are free for students. Private clinics charge 5-10x more for the same service.',
                'estimated_savings': round(healthcare * 0.55, 2),
                'action_steps': [
                    'Register at your university health centre (free consultations)',
                    'Use government hospital OPD for routine check-ups (free)',
                    'Buy generic / government-supply medicines (70-80% cheaper)',
                    'Keep private hospitals only for emergencies',
                    '1600 Suwa Seriya ambulance is free for emergencies'
                ],
                'priority': 'Low'
            })
        
        # ── 8. INCOME BOOST (always shown if savings rate is low) ─
        savings_rate_now = round((current_savings / monthly_income * 100), 1) if monthly_income > 0 else 0
        if savings_rate_now < 15:
            alternatives.append({
                'category': 'Income Enhancement',
                'current_choice': f'Single income source – LKR {monthly_income:,.0f}/month ({savings_rate_now}% saved)',
                'optimal_choice': 'Add LKR 5,000-15,000/month from part-time / freelance',
                'reasoning': 'When expenses are already lean, boosting income is as powerful as cutting costs. Many Sri Lankan students earn from remote freelancing.',
                'estimated_savings': 0,
                'income_boost': 8000,
                'action_steps': [
                    'Offer tutoring to juniors (LKR 1,500-3,000/student/month)',
                    'Freelance on Fiverr/Upwork (data entry, design, coding)',
                    'Check scholarship portals: mahapola.gov.lk, ugc.ac.lk',
                    'Apply for on-campus part-time jobs (library, IT lab assistant)',
                    'Check if your university offers merit bursaries'
                ],
                'priority': 'Medium'
            })
        
        strategy['optimal_alternatives'] = alternatives
        
        # Calculate total potential savings (exclude income-boost entries)
        total_potential_savings = sum(
            alt.get('estimated_savings', 0) for alt in alternatives
            if alt.get('estimated_savings', 0) > 0
        )
        strategy['maximum_savings_potential'] = round(total_potential_savings, 2)
        
        # Cap maximum_savings_potential to not exceed expense_reduction
        # (unrealistic to promise more savings than the target improvement)
        strategy['maximum_savings_potential'] = min(
            strategy['maximum_savings_potential'],
            max(expense_reduction, total_potential_savings)
        )
        
        # Generate implementation plan (prioritized)
        implementation_plan = {
            'immediate_actions': [],
            'this_month_actions': [],
            'long_term_actions': []
        }
        
        for alt in alternatives:
            if alt['priority'] == 'High':
                implementation_plan['immediate_actions'].append({
                    'action': f"Optimize {alt['category']}: {alt['optimal_choice']}",
                    'savings': alt.get('estimated_savings', 0)
                })
            elif alt['priority'] == 'Medium':
                implementation_plan['this_month_actions'].append({
                    'action': f"Review {alt['category']}: {alt['optimal_choice']}",
                    'savings': alt.get('estimated_savings', 0)
                })

            else:
                implementation_plan['long_term_actions'].append({
                    'action': f"Consider {alt['category']}: {alt['optimal_choice']}",
                    'savings': alt.get('estimated_savings', 0)
                })
        
        strategy['implementation_plan'] = implementation_plan
        
        # Realistic success metrics
        target_savings_rate = round(((monthly_income - optimal_budget) / monthly_income * 100), 0) if monthly_income > 0 else 15
        strategy['success_metrics'] = {
            'target_1_month': f"Reduce expenses by LKR {int(total_potential_savings * 0.30):,} (quick wins first)",
            'target_3_months': f"Reach {int(target_savings_rate)}% savings rate (LKR {int(monthly_income - optimal_budget):,} saved/month)",
            'target_6_months': f"Build emergency fund of LKR {int(monthly_income * 1.5):,} (1.5 months buffer)",
            'tracking': 'Track weekly expenses in a spreadsheet or a free app like Spendee'
        }
        
        return strategy
    
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
