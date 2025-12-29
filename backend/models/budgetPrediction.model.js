import mongoose from "mongoose";

const budgetPredictionSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: false  // Optional - can track anonymous predictions too
    },
    username: {
        type: String,
        required: false
    },
    email: {
        type: String,
        required: false
    },
    
    // Personal Information
    monthly_income: {
        type: Number,
        required: true
    },
    year_of_study: {
        type: String,
        required: true
    },
    field_of_study: {
        type: String,
        required: true
    },
    university: {
        type: String,
        required: true
    },
    district: {
        type: String,
        required: true
    },
    accommodation_type: {
        type: String,
        required: true
    },
    
    // Budget Inputs
    rent: {
        type: Number,
        required: true
    },
    internet: {
        type: Number,
        default: 0
    },
    study_materials: {
        type: Number,
        default: 0
    },
    entertainment: {
        type: Number,
        default: 0
    },
    utilities: {
        type: Number,
        default: 0
    },
    healthcare: {
        type: Number,
        default: 0
    },
    other: {
        type: Number,
        default: 0
    },
    
    // Food Details
    food_type: {
        type: String,
        required: true
    },
    meals_per_day: {
        type: String,
        required: true
    },
    diet_type: {
        type: String,
        required: true
    },
    cooking_frequency: {
        type: String,
        required: true
    },
    cooking_percentage: {
        type: Number,
        default: 0
    },
    grocery_items: {
        type: Object,
        default: {}
    },
    delivery_items: {
        type: Object,
        default: {}
    },
    
    // Transport Details
    distance_uni_accommodation: {
        type: Number,
        required: true
    },
    distance_home_uni: {
        type: Number,
        required: true
    },
    transport_method: {
        type: String,
        required: true
    },
    transport_method_home: {
        type: String,
        required: true
    },
    days_per_week: {
        type: String,
        required: true
    },
    home_visit_frequency: {
        type: String,
        required: true
    },
    
    // Calculated Budgets
    food_budget: {
        monthly_total: Number,
        breakdown: Object,
        recommendations: [String]
    },
    transport_budget: {
        monthly_total: Number,
        breakdown: Object,
        recommendations: [String]
    },
    
    // ML Prediction Results
    predicted_budget: {
        type: Number,
        required: true
    },
    ml_confidence: {
        type: Number,
        default: 0
    },
    risk_level: {
        type: String,
        enum: ['Low Risk', 'Medium Risk', 'High Risk'],
        required: true
    },
    risk_probability: {
        type: Number,
        default: 0
    },
    
    // Financial Summary
    total_expenses: {
        type: Number,
        required: true
    },
    calculated_savings: {
        type: Number,
        required: true
    },
    savings_rate: {
        type: Number,
        default: 0
    },
    
    // Recommendations
    recommendations: {
        type: [String],
        default: []
    },
    actionable_steps: {
        type: [String],
        default: []
    },
    
    // Expense Breakdown
    expense_breakdown: {
        type: Object,
        default: {}
    },
    
    // Metadata
    analysis_date: {
        type: Date,
        default: Date.now
    },
    status: {
        type: String,
        enum: ['active', 'archived'],
        default: 'active'
    }
    
}, { timestamps: true });

// Index for faster queries
budgetPredictionSchema.index({ userId: 1, createdAt: -1 });
budgetPredictionSchema.index({ email: 1, createdAt: -1 });
budgetPredictionSchema.index({ analysis_date: -1 });

const BudgetPrediction = mongoose.model("BudgetPrediction", budgetPredictionSchema);

export default BudgetPrediction;
