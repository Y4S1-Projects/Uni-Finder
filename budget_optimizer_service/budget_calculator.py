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
    
    def __init__(self, data_dir='data'):
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
        
        # If no items selected, use realistic default estimation
        if total_groceries == 0:
            diet_type = food_data.get('diet_type', 'Vegetarian')
            meals_per_day = food_data.get('meals_per_day', '3 meals')
            
            # Realistic monthly grocery budget estimates for Sri Lanka (2024-2025)
            # Based on: rice 10kg/month, vegetables, protein, condiments, etc.
            base_budget = {
                'Vegetarian': 11000,    # Rice, dhal, vegetables, eggs, oil, spices
                'Non-Vegetarian': 15000, # + chicken/fish twice a week
                'Vegan': 10000          # Plant-based, no dairy/meat
            }
            
            meal_multiplier = {
                '2 meals': 0.75,
                '3 meals': 1.0,
                '3 meals + snacks': 1.25
            }
            
            total_groceries = base_budget.get(diet_type, 11000) * meal_multiplier.get(meals_per_day, 1.0) * multiplier
        
        # Minimum floor: at least LKR 280/day for home cooking
        minimum_monthly = 280 * 30
        total_groceries = max(total_groceries, minimum_monthly)
        
        return {
            'monthly_total': round(total_groceries, 2),
            'food_type': 'Home Cooked',
            'breakdown': breakdown,
            'daily_cost': round(total_groceries / 30, 2),
            'grocery_monthly': round(total_groceries, 2),
            'notes': f'Estimated grocery cost for {food_data.get("meals_per_day", "3 meals")} home-cooked per day'
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
        
        # Add delivery fees (avg LKR 120 per order)
        total_orders_per_week = breakfast_times + lunch_times + dinner_times + (snacks_times // 2)
        delivery_fees = total_orders_per_week * 120 * 4
        monthly_total += delivery_fees
        breakdown['delivery_fees'] = round(delivery_fees, 2)
        
        # If no items selected, use realistic fallback based on meals_per_day
        if monthly_total <= delivery_fees:
            meals_per_day = food_data.get('meals_per_day', '3 meals')
            diet_type = food_data.get('diet_type', 'Non-Vegetarian')
            district = food_data.get('district', 'Colombo')
            
            # Realistic outside meal costs per day
            daily_outside_cost = {
                '2 meals': {'Vegetarian': 700, 'Non-Vegetarian': 900, 'Vegan': 650},
                '3 meals': {'Vegetarian': 1000, 'Non-Vegetarian': 1300, 'Vegan': 900},
                '3 meals + snacks': {'Vegetarian': 1300, 'Non-Vegetarian': 1700, 'Vegan': 1150}
            }
            dist_multiplier = {'Colombo': 1.2, 'Gampaha': 1.1, 'Kandy': 1.0}.get(district, 1.0)
            per_day = daily_outside_cost.get(meals_per_day, daily_outside_cost['3 meals'])
            fallback_daily = per_day.get(diet_type, per_day['Vegetarian']) * dist_multiplier
            monthly_total = round(fallback_daily * 30, 2)
            breakdown['estimated_daily_outside'] = round(fallback_daily, 2)
        
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
        diet_type = food_data.get('diet_type', 'Non-Vegetarian')
        meals_per_day = food_data.get('meals_per_day', '3 meals')
        district = food_data.get('district', 'Colombo')
        
        # ── Grocery portion ──────────────────────────────────────────
        # Full-month grocery baseline (as if cooking 100% of the time)
        full_grocery_base = {
            'Vegetarian':     {'2 meals': 9000,  '3 meals': 11000, '3 meals + snacks': 13500},
            'Non-Vegetarian': {'2 meals': 11500, '3 meals': 15000, '3 meals + snacks': 18500},
            'Vegan':          {'2 meals': 8500,  '3 meals': 10000, '3 meals + snacks': 12500},
        }
        dist_multiplier = {'Colombo': 1.2, 'Gampaha': 1.1, 'Kandy': 1.0,
                           'Galle': 0.95, 'Jaffna': 1.05}.get(district, 1.0)
        full_grocery = full_grocery_base.get(diet_type, full_grocery_base['Vegetarian'])
        full_grocery_monthly = full_grocery.get(meals_per_day, full_grocery['3 meals']) * dist_multiplier
        
        # Scale by actual cooking percentage
        grocery_total = full_grocery_monthly * (cooking_percentage / 100)
        
        # ── Outside food portion ─────────────────────────────────────
        # Cost when eating outside - weighted average of canteen + delivery
        # (Not all-restaurant; most students mix canteen rice packets with occasional delivery)
        outside_daily_cost = {
            'Vegetarian':     {'2 meals': 450,  '3 meals': 650,  '3 meals + snacks': 870},
            'Non-Vegetarian': {'2 meals': 560,  '3 meals': 800,  '3 meals + snacks': 1050},
            'Vegan':          {'2 meals': 420,  '3 meals': 600,  '3 meals + snacks': 800},
        }
        outside_cost_map = outside_daily_cost.get(diet_type, outside_daily_cost['Vegetarian'])
        outside_per_day = outside_cost_map.get(meals_per_day, outside_cost_map['3 meals']) * dist_multiplier
        outside_monthly = outside_per_day * 30 * (ordering_percentage / 100)
        
        total = grocery_total + outside_monthly
        
        # Minimum floor: LKR 300/day total
        minimum_monthly = 300 * 30
        total = max(total, minimum_monthly)
        
        return {
            'monthly_total': round(total, 2),
            'food_type': 'Mixed',
            'breakdown': {
                'groceries': round(grocery_total, 2),
                'outside_meals': round(outside_monthly, 2),
            },
            'grocery_monthly': round(grocery_total, 2),
            'grocery_note': f'Grocery for {cooking_percentage}% home cooking ({meals_per_day})',
            'outside_note': f'Outside meals for {ordering_percentage}% ordering ({meals_per_day})',
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
        Calculate realistic monthly transport budget for Sri Lankan university students.

        Real-world cost modelling (Sri Lanka 2024-2025):
          Bus  : min LKR 60 + LKR 10/km  (CTB / private mix; regulated minimum fare)
          Train: min LKR 30 + LKR  6/km  (2nd class; cheapest but slow)
          Tuk-Tuk    : min LKR 130 + LKR 65/km  (metered / negotiated)
          Ride-share : min LKR 200 + LKR 55/km  (PickMe / Uber)
          Motorbike  : LKR 23/km (petrol) + LKR 2,500/month (fuel+maint base)
          Car        : LKR 28/km (petrol) + LKR 5,000/month (fuel+maint base)
          Uni Transport: fixed monthly pass  LKR 2,500–5,000
          Bicycle    : LKR 500/month maintenance, essentially zero per trip
          Walking    : free (practical only ≤ 2 km)
          Mixed      : weighted 65% bus + 35% tuk-tuk
        """

        # ── Inputs ──────────────────────────────────────────────────────
        distance_uni  = float(transport_data.get('distance_uni_accommodation', 5))
        distance_home = float(transport_data.get('distance_home_uni', 50))
        daily_transport = transport_data.get('transport_method', 'Bus')   # Accommodation → University

        # Home → Accommodation route: prefer new field, fall back to legacy transport_method_home
        home_transport = transport_data.get(
            'transport_method_home_accommodation',
            transport_data.get('transport_method_home', 'Bus')
        )

        days_str = str(transport_data.get('days_per_week', '5'))
        days_per_week = int(days_str.split()[0]) if days_str[0].isdigit() else 5

        home_visit_freq = transport_data.get('home_visit_frequency', 'Monthly')

        # Work commute (optional)
        has_work_commute   = bool(transport_data.get('has_work_commute', False))
        distance_work      = float(transport_data.get('distance_work', 10))
        work_transport     = transport_data.get('work_transport_method', 'Bus')
        work_days_str      = str(transport_data.get('work_days_per_week', '5'))
        work_days_per_week = int(work_days_str.split()[0]) if work_days_str[0].isdigit() else 5

        # Effective commuting days per month (4.33 = avg weeks per month)
        commute_days_per_month = round(days_per_week * 4.33)

        # Visits per month (if 'Daily' the person commutes every day → already in commute cost)
        visits_per_month_map = {
            'Daily':              0,     # commuter — no separate home-visit cost
            'Weekly':             4.33,
            'Bi-weekly':          2.17,
            'Monthly':            1,
            'Once per semester':  0.25,
            'Rarely/Never':       0,
        }
        visits_per_month = visits_per_month_map.get(home_visit_freq, 1)

        # ── One-way trip cost calculator ─────────────────────────────────
        def one_way_cost(method, km):
            km = max(0.5, float(km))          # avoid zero distances
            if method == 'Walking':
                return 0 if km <= 2 else max(60, 10 * km)   # walk if close, else bus
            elif method == 'Bicycle':
                return 0                                     # handled as monthly maintenance
            elif method == 'Bus':
                return max(60, 10 * km)                      # min LKR 60
            elif method == 'Train':
                return max(30, 6 * km)                       # min LKR 30
            elif method == 'Tuk-Tuk':
                return max(130, 65 * km)                     # min LKR 130
            elif method == 'Ride-share':
                return max(200, 55 * km)                     # min LKR 200
            elif method == 'Personal Vehicle':
                return 23 * km                               # petrol only; base handled below
            elif method == 'University Transport':
                return 0                                     # handled as monthly pass
            elif method == 'Mixed':
                return 0.65 * max(60, 10 * km) + 0.35 * max(130, 65 * km)
            else:
                return max(60, 10 * km)

        # ── Daily commute cost ───────────────────────────────────────────
        round_trip_cost = one_way_cost(daily_transport, distance_uni) * 2   # round trip
        vehicle_monthly_base = 0    # fixed cost for personal vehicles / bicycle

        if daily_transport == 'Bicycle':
            round_trip_cost = 0
            vehicle_monthly_base = 500          # monthly maintenance

        elif daily_transport == 'University Transport':
            # Monthly pass: LKR 2,500 base + LKR 100/km distance
            round_trip_cost = 0
            vehicle_monthly_base = max(2500, min(5000, 2500 + distance_uni * 100))

        elif daily_transport == 'Personal Vehicle':
            # Motorbike assumed (most students); LKR 2,500/month base for fuel+maintenance
            vehicle_monthly_base = 2500

        elif daily_transport == 'Walking' and distance_uni <= 2:
            round_trip_cost = 0     # truly walking — no cost

        monthly_commute = round_trip_cost * commute_days_per_month + vehicle_monthly_base

        # ── Miscellaneous / incidental trips ────────────────────────────
        # Public-transport users: occasional tuk-tuk (rain, late night, heavy bag)
        # ~4 emergency trips per month; short ride ≤ 3 km
        misc_monthly = 0
        if daily_transport in ('Bus', 'Train', 'Mixed', 'Walking'):
            emergency_ride = max(130, 65 * min(distance_uni, 3))   # short tuk-tuk
            misc_monthly += 4 * emergency_ride                     # ~4/month
            misc_monthly += 600                                    # weekend city trips
        elif daily_transport in ('Bicycle',):
            misc_monthly += 600     # occasional bus/tuk when it rains

        # ── Home visit costs ─────────────────────────────────────────────
        home_trip_cost = self._get_home_visit_cost(distance_home, home_transport, transport_data)
        monthly_home = home_trip_cost * visits_per_month

        # ── Work commute cost (optional) ────────────────────────────────
        monthly_work = 0
        work_commute_days_per_month = 0
        work_round_trip_cost = 0
        if has_work_commute and distance_work > 0:
            work_round_trip_cost = one_way_cost(work_transport, distance_work) * 2
            work_vehicle_base = 0
            if work_transport == 'Bicycle':
                work_round_trip_cost = 0
                work_vehicle_base = 250   # shared maintenance
            elif work_transport == 'Personal Vehicle':
                work_vehicle_base = 1500  # shared fuel base (already partly counted in uni)
            elif work_transport == 'University Transport':
                work_round_trip_cost = 0
                work_vehicle_base = max(1500, min(3000, 1500 + distance_work * 50))
            work_commute_days_per_month = round(work_days_per_week * 4.33)
            monthly_work = work_round_trip_cost * work_commute_days_per_month + work_vehicle_base

        # ── Total ────────────────────────────────────────────────────────
        total = monthly_commute + misc_monthly + monthly_home + monthly_work
        total = max(total, 1500)   # realistic floor: LKR 1,500/month minimum

        # Human-readable method label
        method_labels = {
            'Bus':                  'CTB / Private Bus',
            'Train':                'Train',
            'Tuk-Tuk':              'Tuk-Tuk / Three-Wheeler',
            'Ride-share':           'PickMe / Uber',
            'Personal Vehicle':     'Personal Vehicle (Motorbike)',
            'University Transport': 'University Transport Pass',
            'Walking':              'Walking',
            'Bicycle':              'Bicycle',
            'Mixed':                'Mixed (Bus + Tuk-Tuk)',
        }

        return {
            'monthly_total': round(total, 2),
            'breakdown': {
                'daily_commute':   round(monthly_commute, 2),
                'misc_trips':      round(misc_monthly, 2),
                'home_visits':     round(monthly_home, 2),
                'work_commute':    round(monthly_work, 2),
            },
            'daily_cost':                round(round_trip_cost, 2),
            # Route method labels — both routes exposed
            'transport_method':          method_labels.get(daily_transport, daily_transport),
            'accommodation_uni_method':  method_labels.get(daily_transport, daily_transport),
            'home_accommodation_method': method_labels.get(home_transport, home_transport),
            'commute_days_per_month':    commute_days_per_month,
            'one_way_trip_cost':         round(one_way_cost(daily_transport, distance_uni), 2),
            'home_visit_frequency':      home_visit_freq,
            'distance_uni_km':           distance_uni,
            'distance_home_km':          distance_home,
            # Work commute
            'has_work_commute':          has_work_commute,
            'work_commute_method':       method_labels.get(work_transport, work_transport) if has_work_commute else None,
            'work_distance_km':          distance_work if has_work_commute else 0,
            'work_commute_days_per_month': work_commute_days_per_month,
            'work_round_trip_cost':      round(work_round_trip_cost, 2) if has_work_commute else 0,
        }

    def _get_home_visit_cost(self, distance_home, home_transport, transport_data):
        """
        Calculate round-trip cost for one home visit.
        Prefers inter-district prices from the CSV where district info is available;
        falls back to per-km estimation otherwise.
        """
        home_district = transport_data.get('home_district', '').strip()
        uni_district  = transport_data.get('district', transport_data.get('uni_district', '')).strip()

        # Try CSV lookup first
        if (self.transport_costs is not None
                and home_district and uni_district
                and home_district.lower() != uni_district.lower()):
            mask = (
                (self.transport_costs['Source_District'].str.lower() == uni_district.lower()) &
                (self.transport_costs['Destination_District'].str.lower() == home_district.lower())
            )
            row = self.transport_costs[mask]
            if not row.empty:
                if home_transport == 'Train':
                    return float(row.iloc[0]['Bus_Price (LKR)']) * 0.65
                elif home_transport == 'Personal Vehicle':
                    return float(row.iloc[0]['Diesel_Car_Price (LKR)']) * 0.5   # motorbike ≈ half diesel-car cost
                else:
                    return float(row.iloc[0]['Bus_Price (LKR)'])   # bus round-trip price from CSV

        # Fallback: per-km estimate for the round trip
        per_km_one_way = {
            'Bus':             10,
            'Train':            6,
            'Personal Vehicle': 23,
            'Ride-share':       55,
        }
        rate = per_km_one_way.get(home_transport, 10)
        one_way = max(60, rate * distance_home)
        return one_way * 2   # round trip
    
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

