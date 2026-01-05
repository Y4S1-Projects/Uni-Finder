#!/usr/bin/env python3
"""
Budget Calculator - Food and Transport Auto-Calculation
Component of UniFinder LK Budget Optimizer
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

class BudgetCalculator:
    """
    Auto-calculate food and transport budgets based on user preferences
    """
    
    def __init__(self, data_dir='budget_optimizer_files'):
        self.data_dir = data_dir
        self.food_prices = None
        self.vegetable_prices = None
        self.transport_costs = None
        self.load_reference_data()
    
    def load_reference_data(self):
        """Load reference data from CSV files"""
        try:
            # Load food prices
            food_prices_path = os.path.join(self.data_dir, 'food_prices.csv')
            if os.path.exists(food_prices_path):
                self.food_prices = pd.read_csv(food_prices_path)
                print(f"✅ Loaded food prices: {len(self.food_prices)} items")
            
            # Load vegetable prices
            veg_prices_path = os.path.join(self.data_dir, 'Vegetables_fruit_prices.csv')
            if os.path.exists(veg_prices_path):
                self.vegetable_prices = pd.read_csv(veg_prices_path)
                print(f"✅ Loaded vegetable prices: {len(self.vegetable_prices)} items")
            
            # Load transport costs
            transport_path = os.path.join(self.data_dir, 'srilanka_transport_costs.csv')
            if os.path.exists(transport_path):
                self.transport_costs = pd.read_csv(transport_path)
                print(f"✅ Loaded transport costs")
                
        except Exception as e:
            print(f"⚠️ Error loading reference data: {e}")
    
    def calculate_food_budget(self, food_data):
        """
        Calculate monthly food budget based on user preferences
        
        Args:
            food_data: Dictionary containing:
                - food_type: 'Home Cooked', 'Mixed', 'Food Delivery', etc.
                - meals_per_day: '2 meals', '3 meals', '3 meals + snacks'
                - diet_type: 'Vegetarian', 'Non-Vegetarian', 'Vegan'
                - cooking_frequency: 'Every day', 'Most days', etc.
                - district: Location for pricing
                - grocery_items: Dict of selected groceries (if home cooked)
                - delivery_items: Dict of delivery preferences (if food delivery)
        
        Returns:
            Dictionary with budget breakdown
        """
        
        food_type = food_data.get('food_type', 'Mixed')
        district = food_data.get('district', 'Colombo')
        
        if food_type == 'Home Cooked':
            return self._calculate_grocery_budget(food_data)
        elif food_type == 'Food Delivery':
            return self._calculate_delivery_budget(food_data)
        elif food_type == 'Mixed':
            return self._calculate_mixed_budget(food_data)
        elif food_type == 'Mostly Canteen/Restaurants':
            return self._calculate_restaurant_budget(food_data)
        elif food_type == 'Full Meal Plan':
            return self._calculate_meal_plan_budget(food_data)
        else:
            # Default calculation
            return self._calculate_default_budget(food_data)
    
    def _calculate_grocery_budget(self, food_data):
        """Calculate budget for home cooking based on grocery items"""
        
        grocery_items = food_data.get('grocery_items', {})
        district = food_data.get('district', 'Colombo')
        
        # Base costs for common items (LKR per month)
        base_grocery_costs = {
            # Rice & Grains
            'white_rice_5kg': 1200,
            'white_rice_10kg': 2200,
            'white_rice_25kg': 5000,
            'red_rice_5kg': 1400,
            'dhal_1kg': 450,
            'flour_1kg': 180,
            
            # Proteins (weekly costs × 4)
            'chicken_1kg_weekly': 850 * 4,
            'fish_1kg_weekly': 1200 * 4,
            'eggs_12_weekly': 600 * 4,
            'milk_1kg': 800,
            
            # Vegetables (weekly costs × 4)
            'vegetables_weekly': 500 * 4,
            'leafy_greens_weekly': 200 * 4,
            'root_vegetables_weekly': 300 * 4,
            
            # Spices & Condiments
            'curry_powder_250g': 250,
            'chili_powder_250g': 300,
            'salt_1kg': 80,
            'sugar_1kg': 200,
            'cooking_oil_1l': 600,
            
            # Other
            'bread_weekly': 150 * 4,
            'tea_coffee_500g': 400,
            'instant_noodles_5pk_weekly': 250 * 4,
        }
        
        # District multiplier (Colombo = 1.0 baseline)
        district_multipliers = {
            'Colombo': 1.2,
            'Gampaha': 1.1,
            'Kandy': 1.0,
            'Galle': 0.95,
            'Jaffna': 1.05,
            'Other': 1.0
        }
        
        multiplier = district_multipliers.get(district, 1.0)
        
        # Calculate total based on selected items
        total_groceries = 0
        breakdown = {}
        
        for item, cost in base_grocery_costs.items():
            if grocery_items.get(item, False):
                adjusted_cost = cost * multiplier
                total_groceries += adjusted_cost
                breakdown[item] = round(adjusted_cost, 2)
        
        # If no items selected, use default estimation
        if total_groceries == 0:
            diet_type = food_data.get('diet_type', 'Vegetarian')
            meals_per_day = food_data.get('meals_per_day', '3 meals')
            
            # Base monthly grocery budget estimates
            base_budget = {
                'Vegetarian': 8000,
                'Non-Vegetarian': 12000,
                'Vegan': 7000
            }
            
            meal_multiplier = {
                '2 meals': 0.7,
                '3 meals': 1.0,
                '3 meals + snacks': 1.3
            }
            
            total_groceries = base_budget.get(diet_type, 8000) * meal_multiplier.get(meals_per_day, 1.0) * multiplier
        
        return {
            'monthly_total': round(total_groceries, 2),
            'food_type': 'Home Cooked',
            'breakdown': breakdown,
            'daily_cost': round(total_groceries / 30, 2)
        }
    
    def _calculate_delivery_budget(self, food_data):
        """Calculate budget for food delivery based on ordering habits"""
        
        delivery_items = food_data.get('delivery_items', {})
        
        # Base costs for common delivery items
        meal_costs = {
            'breakfast': {
                'egg_roti': 250,
                'string_hoppers': 200,
                'sandwich': 350,
                'paratha': 150,
                'rice_packet': 300
            },
            'lunch': {
                'rice_curry': 400,
                'fried_rice': 450,
                'biriyani': 650,
                'noodles': 500,
                'kottu': 550,
                'submarine': 600
            },
            'dinner': {
                'rice_curry': 450,
                'pizza': 1200,
                'fried_rice': 500,
                'kottu': 550,
                'biriyani': 700,
                'fast_food': 800
            },
            'snacks': {
                'tea_coffee': 150,
                'desserts': 300,
                'soft_drinks': 200
            }
        }
        
        # Calculate weekly costs
        weekly_cost = 0
        breakdown = {}
        
        # Breakfast
        breakfast_times = delivery_items.get('breakfast_times_per_week', 0)
        breakfast_items = delivery_items.get('breakfast_items', [])
        if breakfast_times > 0 and breakfast_items:
            avg_breakfast = np.mean([meal_costs['breakfast'].get(item, 250) for item in breakfast_items])
            breakfast_weekly = avg_breakfast * breakfast_times
            weekly_cost += breakfast_weekly
            breakdown['breakfast'] = round(breakfast_weekly * 4, 2)
        
        # Lunch
        lunch_times = delivery_items.get('lunch_times_per_week', 0)
        lunch_items = delivery_items.get('lunch_items', [])
        if lunch_times > 0 and lunch_items:
            avg_lunch = np.mean([meal_costs['lunch'].get(item, 400) for item in lunch_items])
            lunch_weekly = avg_lunch * lunch_times
            weekly_cost += lunch_weekly
            breakdown['lunch'] = round(lunch_weekly * 4, 2)
        
        # Dinner
        dinner_times = delivery_items.get('dinner_times_per_week', 0)
        dinner_items = delivery_items.get('dinner_items', [])
        if dinner_times > 0 and dinner_items:
            avg_dinner = np.mean([meal_costs['dinner'].get(item, 450) for item in dinner_items])
            dinner_weekly = avg_dinner * dinner_times
            weekly_cost += dinner_weekly
            breakdown['dinner'] = round(dinner_weekly * 4, 2)
        
        # Snacks
        snacks_times = delivery_items.get('snacks_times_per_week', 0)
        if snacks_times > 0:
            snacks_weekly = 200 * snacks_times
            weekly_cost += snacks_weekly
            breakdown['snacks'] = round(snacks_weekly * 4, 2)
        
        # Monthly total
        monthly_total = weekly_cost * 4
        
        # Add delivery fees (avg LKR 100 per order)
        total_orders_per_week = breakfast_times + lunch_times + dinner_times + (snacks_times // 2)
        delivery_fees = total_orders_per_week * 100 * 4
        monthly_total += delivery_fees
        breakdown['delivery_fees'] = round(delivery_fees, 2)
        
        return {
            'monthly_total': round(monthly_total, 2),
            'food_type': 'Food Delivery',
            'breakdown': breakdown,
            'daily_cost': round(monthly_total / 30, 2)
        }
    
    def _calculate_mixed_budget(self, food_data):
        """Calculate budget for mixed cooking and ordering"""
        
        cooking_percentage = food_data.get('cooking_percentage', 60)
        ordering_percentage = 100 - cooking_percentage
        
        # Calculate grocery portion
        grocery_budget = self._calculate_grocery_budget(food_data)
        grocery_total = grocery_budget['monthly_total'] * (cooking_percentage / 100)
        
        # Calculate delivery portion
        delivery_budget = self._calculate_delivery_budget(food_data)
        delivery_total = delivery_budget['monthly_total'] * (ordering_percentage / 100)
        
        total = grocery_total + delivery_total
        
        return {
            'monthly_total': round(total, 2),
            'food_type': 'Mixed',
            'breakdown': {
                'groceries': round(grocery_total, 2),
                'delivery': round(delivery_total, 2)
            },
            'daily_cost': round(total / 30, 2)
        }
    
    def _calculate_restaurant_budget(self, food_data):
        """Calculate budget for mostly eating at canteens/restaurants"""
        
        meals_per_day = food_data.get('meals_per_day', '3 meals')
        diet_type = food_data.get('diet_type', 'Vegetarian')
        district = food_data.get('district', 'Colombo')
        
        # Base costs per meal in restaurants
        meal_costs = {
            'Colombo': {'breakfast': 200, 'lunch': 300, 'dinner': 350},
            'Kandy': {'breakfast': 150, 'lunch': 250, 'dinner': 300},
            'Galle': {'breakfast': 130, 'lunch': 220, 'dinner': 280},
            'Other': {'breakfast': 120, 'lunch': 200, 'dinner': 250}
        }
        
        costs = meal_costs.get(district, meal_costs['Other'])
        
        # Calculate daily cost
        daily_cost = 0
        if meals_per_day == '2 meals':
            daily_cost = costs['lunch'] + costs['dinner']
        elif meals_per_day == '3 meals':
            daily_cost = costs['breakfast'] + costs['lunch'] + costs['dinner']
        elif meals_per_day == '3 meals + snacks':
            daily_cost = costs['breakfast'] + costs['lunch'] + costs['dinner'] + 150
        
        # Apply diet multiplier
        if diet_type == 'Non-Vegetarian':
            daily_cost *= 1.3
        elif diet_type == 'Vegan':
            daily_cost *= 0.95
        
        monthly_total = daily_cost * 30
        
        return {
            'monthly_total': round(monthly_total, 2),
            'food_type': 'Mostly Canteen/Restaurants',
            'breakdown': {
                'daily_average': round(daily_cost, 2),
                'monthly_estimate': round(monthly_total, 2)
            },
            'daily_cost': round(daily_cost, 2)
        }
    
    def _calculate_meal_plan_budget(self, food_data):
        """Calculate budget for hostel/boarding meal plan"""
        
        meal_plan_cost = food_data.get('meal_plan_cost', 15000)
        
        return {
            'monthly_total': meal_plan_cost,
            'food_type': 'Full Meal Plan',
            'breakdown': {
                'meal_plan': meal_plan_cost
            },
            'daily_cost': round(meal_plan_cost / 30, 2)
        }
    
    def _calculate_default_budget(self, food_data):
        """Default budget calculation when type is not specified"""
        
        monthly_income = food_data.get('monthly_income', 25000)
        district = food_data.get('district', 'Colombo')
        
        # Rule of thumb: 30-40% of income on food
        base_estimate = monthly_income * 0.35
        
        # District adjustment
        district_multipliers = {
            'Colombo': 1.2,
            'Gampaha': 1.1,
            'Kandy': 1.0,
            'Galle': 0.95,
            'Other': 1.0
        }
        
        estimate = base_estimate * district_multipliers.get(district, 1.0)
        
        return {
            'monthly_total': round(estimate, 2),
            'food_type': 'Estimated',
            'breakdown': {
                'estimate_based_on_income': round(estimate, 2)
            },
            'daily_cost': round(estimate / 30, 2)
        }
    
    def calculate_transport_budget(self, transport_data):
        """
        Calculate monthly transport budget
        
        Args:
            transport_data: Dictionary containing:
                - distance_uni_accommodation: Distance in km
                - distance_home_uni: Distance in km
                - transport_method: Primary transport method
                - days_per_week: University days
                - home_visit_frequency: How often going home
                - transport_method_home: Transport for home visits
        
        Returns:
            Dictionary with transport budget breakdown
        """
        
        # Get distances
        distance_uni = transport_data.get('distance_uni_accommodation', 5)
        distance_home = transport_data.get('distance_home_uni', 50)
        
        # Get transport methods
        daily_transport = transport_data.get('transport_method', 'Bus')
        home_transport = transport_data.get('transport_method_home', daily_transport)
        
        # Get frequencies
        days_per_week = int(transport_data.get('days_per_week', '5').split()[0])
        home_visit_freq = transport_data.get('home_visit_frequency', 'Monthly')
        
        # Transport rates (LKR per km or per trip)
        transport_rates = {
            'Walking': 0,
            'Bicycle': 0,
            'Bus': 3.5,  # Per km round trip
            'Train': 2.5,
            'Tuk-Tuk': 80,  # Fixed per trip
            'Ride-share': 100,
            'Personal Vehicle': 15,  # Petrol per km
            'University Transport': 50,  # Per day
            'Mixed': 4.5
        }
        
        # Calculate daily commute
        daily_rate = transport_rates.get(daily_transport, 3.5)
        
        if daily_transport in ['Tuk-Tuk', 'Ride-share']:
            daily_cost = daily_rate * 2  # Round trip
        elif daily_transport == 'University Transport':
            daily_cost = daily_rate
        else:
            daily_cost = distance_uni * daily_rate * 2  # Round trip
        
        # Monthly commute (4 weeks)
        monthly_commute = daily_cost * days_per_week * 4
        
        # Home visit costs
        home_visit_costs = {
            'Weekly': 4,
            'Bi-weekly': 2,
            'Monthly': 1,
            'Once per semester': 0.25,
            'Rarely/Never': 0
        }
        
        visits_per_month = home_visit_costs.get(home_visit_freq, 0)
        
        # Home visit rate
        home_rate = transport_rates.get(home_transport, 2.5)
        if distance_home > 20:
            home_rate = 2.5  # Assume bus/train for long distance
        
        monthly_home = distance_home * home_rate * 2 * visits_per_month
        
        # Total with 10% buffer
        total_transport = monthly_commute + monthly_home
        total_with_buffer = total_transport * 1.1
        
        return {
            'monthly_total': round(total_with_buffer, 2),
            'breakdown': {
                'daily_commute': round(monthly_commute, 2),
                'home_visits': round(monthly_home, 2),
                'buffer': round(total_with_buffer - total_transport, 2)
            },
            'daily_cost': round(daily_cost, 2),
            'transport_method': daily_transport
        }
    
    def calculate_distance(self, origin, destination):
        """
        Calculate distance between two locations
        (Placeholder - integrate Google Maps API for production)
        
        Args:
            origin: Origin address
            destination: Destination address
        
        Returns:
            Dictionary with distance and duration
        """
        
        # For now, return estimated distance
        # In production, use Google Maps Distance Matrix API
        
        # Simple estimation based on city names
        major_cities = {
            'Colombo': (6.9271, 79.8612),
            'Kandy': (7.2906, 80.6337),
            'Galle': (6.0535, 80.2210),
            'Jaffna': (9.6615, 80.0255),
            'Kurunegala': (7.4863, 80.3623),
            'Matara': (5.9549, 80.5550),
            'Anuradhapura': (8.3114, 80.4037)
        }
        
        # Placeholder: return default distance
        return {
            'distance_km': 50,
            'duration_minutes': 90,
            'status': 'estimated',
            'message': 'Distance estimation - integrate Google Maps API for accurate results'
        }


# Example usage
if __name__ == '__main__':
    calculator = BudgetCalculator()
    
    # Test food calculation
    food_data = {
        'food_type': 'Home Cooked',
        'meals_per_day': '3 meals',
        'diet_type': 'Non-Vegetarian',
        'district': 'Colombo',
        'grocery_items': {
            'white_rice_10kg': True,
            'chicken_1kg_weekly': True,
            'eggs_12_weekly': True,
            'vegetables_weekly': True
        }
    }
    
    food_budget = calculator.calculate_food_budget(food_data)
    print(f"\n📊 Food Budget: LKR {food_budget['monthly_total']}")
    print(f"Breakdown: {food_budget['breakdown']}")
    
    # Test transport calculation
    transport_data = {
        'distance_uni_accommodation': 5,
        'distance_home_uni': 80,
        'transport_method': 'Bus',
        'days_per_week': '5 days',
        'home_visit_frequency': 'Monthly',
        'transport_method_home': 'Bus'
    }
    
    transport_budget = calculator.calculate_transport_budget(transport_data)
    print(f"\n🚌 Transport Budget: LKR {transport_budget['monthly_total']}")
    print(f"Breakdown: {transport_budget['breakdown']}")
