#!/usr/bin/env python3
"""
AI-Powered Student Budget Optimizer - Model Training System
Component 2 of UniFinder LK Platform

This module implements machine learning models for expense forecasting
and budget optimization specifically for Sri Lankan students.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
import joblib
import json
import os
from datetime import datetime, timedelta
import requests
import warnings
warnings.filterwarnings('ignore')

class StudentBudgetOptimizer:
    """
    AI-powered budget optimizer for Sri Lankan students
    Integrates with UniFinder platform for personalized recommendations
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.accuracy_metrics = {}
        self.training_history = []
        
    def load_training_data(self, csv_file_path):
        """
        Load and preprocess training data from CSV files
        Expected columns: student_id, month, income, accommodation, food, transport, 
                         education, entertainment, utilities, degree_type, location, year
        """
        try:
            df = pd.read_csv(csv_file_path)
            print(f"✅ Loaded training data: {len(df)} records from {csv_file_path}")
            return self.preprocess_data(df)
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None
    
    def preprocess_data(self, df):
        """
        Preprocess data for model training
        """
        # Feature engineering
        df['total_expenses'] = df[['accommodation', 'food', 'transport', 
                                 'education', 'entertainment', 'utilities']].sum(axis=1)
        
        # Create expense ratios
        df['accommodation_ratio'] = df['accommodation'] / df['income']
        df['food_ratio'] = df['food'] / df['income']
        df['transport_ratio'] = df['transport'] / df['income']
        
        # Encode categorical variables
        categorical_cols = ['degree_type', 'location']
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                self.encoders[col] = le
        
        # Handle missing values
        df = df.fillna(df.mean(numeric_only=True))
        
        return df
    
    def create_sample_data(self):
        """
        Create sample training data for Sri Lankan students
        This integrates with your existing UniFinder data structure
        """
        np.random.seed(42)
        n_samples = 1000
        
        # Sri Lankan context data
        locations = ['Colombo', 'Kandy', 'Galle', 'Jaffna', 'Matara', 'Ratnapura']
        degree_types = ['Engineering', 'Medicine', 'Arts', 'Science', 'Commerce', 'Law']
        
        data = {
            'student_id': range(1, n_samples + 1),
            'month': np.random.randint(1, 13, n_samples),
            'year': np.random.choice([2023, 2024, 2025], n_samples),
            'income': np.random.normal(25000, 8000, n_samples),  # LKR
            'accommodation': np.random.normal(12000, 4000, n_samples),
            'food': np.random.normal(8000, 2500, n_samples),
            'transport': np.random.normal(3000, 1000, n_samples),
            'education': np.random.normal(5000, 2000, n_samples),
            'entertainment': np.random.normal(2000, 800, n_samples),
            'utilities': np.random.normal(1500, 600, n_samples),
            'degree_type': np.random.choice(degree_types, n_samples),
            'location': np.random.choice(locations, n_samples),
            'semester': np.random.randint(1, 9, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Ensure positive values
        expense_cols = ['income', 'accommodation', 'food', 'transport', 'education', 'entertainment', 'utilities']
        for col in expense_cols:
            df[col] = np.abs(df[col])
        
        # Save sample data
        df.to_csv('/Users/shehansalitha/Desktop/Uni-Finder/backend/student_budget_training_data.csv', index=False)
        print("✅ Created sample training data: student_budget_training_data.csv")
        
        return df
    
    def train_expense_prediction_model(self, df):
        """
        Train linear regression model for expense prediction
        Target: 85% accuracy for monthly forecasts
        """
        # Prepare features
        feature_cols = ['income', 'month', 'year', 'semester']
        
        # Add encoded categorical features
        for col in ['degree_type', 'location']:
            if f'{col}_encoded' in df.columns:
                feature_cols.append(f'{col}_encoded')
        
        X = df[feature_cols]
        y = df['total_expenses']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Create pipeline with polynomial features and regularization
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('poly', PolynomialFeatures(degree=2, include_bias=False)),
            ('ridge', Ridge(alpha=1.0))
        ])
        
        # Train model
        pipeline.fit(X_train, y_train)
        
        # Predictions
        y_pred = pipeline.predict(X_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        accuracy = max(0, (1 - mae / y_test.mean()) * 100)
        
        # Store model and metrics
        self.models['expense_prediction'] = pipeline
        self.accuracy_metrics['expense_prediction'] = {
            'accuracy': round(accuracy, 2),
            'mae': round(mae, 2),
            'mse': round(mse, 2),
            'r2_score': round(r2, 3),
            'target_accuracy': 85.0,
            'achieved': bool(accuracy >= 85.0)
        }
        
        print(f"🎯 Expense Prediction Model Trained:")
        print(f"   Accuracy: {accuracy:.2f}% (Target: 85%)")
        print(f"   MAE: {mae:.2f} LKR")
        print(f"   R² Score: {r2:.3f}")
        
        return pipeline
    
    def train_budget_optimization_model(self, df):
        """
        Train model for budget category optimization
        """
        # Features for budget optimization
        feature_cols = ['income', 'total_expenses', 'month', 'semester']
        
        # Add encoded features
        for col in ['degree_type', 'location']:
            if f'{col}_encoded' in df.columns:
                feature_cols.append(f'{col}_encoded')
        
        # Train separate models for each expense category
        expense_categories = ['accommodation', 'food', 'transport', 'education', 'entertainment', 'utilities']
        category_models = {}
        
        for category in expense_categories:
            X = df[feature_cols]
            y = df[category]
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Simple linear regression for category prediction
            model = Pipeline([
                ('scaler', StandardScaler()),
                ('regressor', LinearRegression())
            ])
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            accuracy = max(0, (1 - mean_absolute_error(y_test, y_pred) / y_test.mean()) * 100)
            
            category_models[category] = {
                'model': model,
                'accuracy': round(accuracy, 2)
            }
        
        self.models['budget_optimization'] = category_models
        print("✅ Budget optimization models trained for all expense categories")
        
        return category_models
    
    def integrate_with_unifinder(self, student_data):
        """
        Integration with UniFinder platform data
        Uses degree recommendations, scholarship data, and career guidance
        """
        try:
            # Simulate API call to UniFinder components
            integrated_data = {
                'degree_recommendation': student_data.get('recommended_degree', 'General'),
                'scholarship_amount': student_data.get('scholarship', 0),
                'career_field': student_data.get('career_field', 'General'),
                'location_preference': student_data.get('location', 'Colombo')
            }
            
            # Adjust predictions based on UniFinder insights
            if integrated_data['scholarship_amount'] > 0:
                # Reduce education expenses if scholarship available
                reduction_factor = min(0.3, integrated_data['scholarship_amount'] / 50000)
                return {'education_discount': reduction_factor}
            
            return integrated_data
            
        except Exception as e:
            print(f"⚠️ UniFinder integration warning: {e}")
            return {}
    
    def predict_monthly_expenses(self, student_profile):
        """
        Predict monthly expenses for a student
        """
        if 'expense_prediction' not in self.models:
            print("❌ Expense prediction model not trained!")
            return None
        
        try:
            # Prepare input features
            features = {
                'income': student_profile.get('income', 25000),
                'month': student_profile.get('month', datetime.now().month),
                'year': student_profile.get('year', datetime.now().year),
                'semester': student_profile.get('semester', 1)
            }
            
            # Add encoded categorical features
            for col in ['degree_type', 'location']:
                if col in student_profile and col in self.encoders:
                    encoded_val = self.encoders[col].transform([student_profile[col]])[0]
                    features[f'{col}_encoded'] = encoded_val
                else:
                    features[f'{col}_encoded'] = 0  # Default value
            
            # Create input array
            input_data = pd.DataFrame([features])
            
            # Make prediction
            prediction = self.models['expense_prediction'].predict(input_data)[0]
            
            # Integrate with UniFinder data
            unifinder_adjustments = self.integrate_with_unifinder(student_profile)
            
            return {
                'predicted_total_expenses': round(prediction, 2),
                'confidence': self.accuracy_metrics['expense_prediction']['accuracy'],
                'unifinder_integration': unifinder_adjustments,
                'prediction_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            return None
    
    def optimize_budget(self, student_profile, target_savings=0.15):
        """
        Optimize budget allocation across categories
        """
        if 'budget_optimization' not in self.models:
            print("❌ Budget optimization models not trained!")
            return None
        
        try:
            income = student_profile.get('income', 25000)
            target_expenses = income * (1 - target_savings)
            
            optimized_budget = {}
            category_models = self.models['budget_optimization']
            
            # Prepare features
            features = {
                'income': income,
                'total_expenses': target_expenses,
                'month': student_profile.get('month', datetime.now().month),
                'semester': student_profile.get('semester', 1)
            }
            
            # Add encoded features
            for col in ['degree_type', 'location']:
                if col in student_profile and col in self.encoders:
                    encoded_val = self.encoders[col].transform([student_profile[col]])[0]
                    features[f'{col}_encoded'] = encoded_val
                else:
                    features[f'{col}_encoded'] = 0
            
            input_data = pd.DataFrame([features])
            
            # Predict optimal allocation for each category
            total_predicted = 0
            for category, model_info in category_models.items():
                predicted_amount = model_info['model'].predict(input_data)[0]
                optimized_budget[category] = max(0, round(predicted_amount, 2))
                total_predicted += optimized_budget[category]
            
            # Normalize to fit target expenses
            if total_predicted > 0:
                scale_factor = target_expenses / total_predicted
                for category in optimized_budget:
                    optimized_budget[category] = round(optimized_budget[category] * scale_factor, 2)
            
            return {
                'optimized_budget': optimized_budget,
                'target_savings_rate': target_savings,
                'projected_savings': round(income - sum(optimized_budget.values()), 2),
                'total_expenses': round(sum(optimized_budget.values()), 2)
            }
            
        except Exception as e:
            print(f"❌ Budget optimization error: {e}")
            return None
    
    def save_models(self, model_dir='/Users/shehansalitha/Desktop/Uni-Finder/backend/models'):
        """
        Save trained models and metadata
        """
        os.makedirs(model_dir, exist_ok=True)
        
        # Save models
        for model_name, model in self.models.items():
            model_path = os.path.join(model_dir, f'{model_name}.joblib')
            joblib.dump(model, model_path)
            print(f"✅ Saved {model_name} model to {model_path}")
        
        # Save encoders
        encoders_path = os.path.join(model_dir, 'encoders.joblib')
        joblib.dump(self.encoders, encoders_path)
        
        # Save metadata
        metadata = {
            'accuracy_metrics': self.accuracy_metrics,
            'training_date': datetime.now().isoformat(),
            'model_version': '1.0',
            'target_accuracy': 85.0
        }
        
        metadata_path = os.path.join(model_dir, 'model_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Model training completed. Files saved in {model_dir}")
    
    def load_models(self, model_dir='/Users/shehansalitha/Desktop/Uni-Finder/backend/models'):
        """
        Load pre-trained models
        """
        try:
            # Load models
            for model_file in os.listdir(model_dir):
                if model_file.endswith('.joblib') and model_file != 'encoders.joblib':
                    model_name = model_file.replace('.joblib', '')
                    model_path = os.path.join(model_dir, model_file)
                    self.models[model_name] = joblib.load(model_path)
            
            # Load encoders
            encoders_path = os.path.join(model_dir, 'encoders.joblib')
            if os.path.exists(encoders_path):
                self.encoders = joblib.load(encoders_path)
            
            # Load metadata
            metadata_path = os.path.join(model_dir, 'model_metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.accuracy_metrics = metadata.get('accuracy_metrics', {})
            
            print("✅ Models loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            return False
    
    def get_model_performance(self):
        """
        Get current model performance metrics
        """
        return {
            'models_trained': list(self.models.keys()),
            'accuracy_metrics': self.accuracy_metrics,
            'status': 'ready' if self.models else 'not_trained',
            'last_updated': datetime.now().isoformat()
        }

def main():
    """
    Main training pipeline
    """
    print("🚀 AI-Powered Student Budget Optimizer - Model Training")
    print("=" * 60)
    
    # Initialize optimizer
    optimizer = StudentBudgetOptimizer()
    
    # Create or load training data
    print("📊 Preparing training data...")
    df = optimizer.create_sample_data()
    
    if df is not None:
        # Preprocess data
        df = optimizer.preprocess_data(df)
        
        # Train models
        print("\n🤖 Training expense prediction model...")
        optimizer.train_expense_prediction_model(df)
        
        print("\n🎯 Training budget optimization models...")
        optimizer.train_budget_optimization_model(df)
        
        # Save models
        print("\n💾 Saving trained models...")
        optimizer.save_models()
        
        # Test prediction
        print("\n🧪 Testing prediction...")
        test_profile = {
            'income': 30000,
            'month': 10,
            'year': 2025,
            'semester': 5,
            'degree_type': 'Engineering',
            'location': 'Colombo'
        }
        
        prediction = optimizer.predict_monthly_expenses(test_profile)
        budget_optimization = optimizer.optimize_budget(test_profile)
        
        print("\n📈 Sample Prediction Results:")
        print(f"   Predicted Expenses: {prediction['predicted_total_expenses']} LKR")
        print(f"   Model Confidence: {prediction['confidence']}%")
        
        print("\n💰 Sample Budget Optimization:")
        if budget_optimization:
            for category, amount in budget_optimization['optimized_budget'].items():
                print(f"   {category.title()}: {amount} LKR")
            print(f"   Projected Savings: {budget_optimization['projected_savings']} LKR")
        
        # Display performance metrics
        print("\n🎯 Model Performance Summary:")
        performance = optimizer.get_model_performance()
        for model, metrics in performance['accuracy_metrics'].items():
            print(f"   {model.title()}: {metrics['accuracy']}% accuracy")
        
        print("\n✅ Training completed successfully!")
        print("🔗 Models ready for integration with UniFinder platform")
    
    else:
        print("❌ Failed to load training data")

if __name__ == "__main__":
    main()