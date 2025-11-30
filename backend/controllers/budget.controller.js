import BudgetPrediction from '../models/budgetPrediction.model.js';
import User from '../models/user.model.js';

// Save budget prediction
export const saveBudgetPrediction = async (req, res, next) => {
    try {
        const budgetData = req.body;
        
        // Optional: If userId or email is provided, verify user exists
        if (budgetData.userId) {
            const user = await User.findById(budgetData.userId);
            if (user) {
                budgetData.username = user.username;
                budgetData.email = user.email;
            }
        }
        
        // Create new budget prediction record
        const newPrediction = new BudgetPrediction(budgetData);
        await newPrediction.save();
        
        res.status(201).json({
            success: true,
            message: 'Budget prediction saved successfully',
            predictionId: newPrediction._id,
            data: newPrediction
        });
        
    } catch (error) {
        console.error('Error saving budget prediction:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to save budget prediction',
            error: error.message
        });
    }
};

// Get all budget predictions for a user
export const getUserBudgetPredictions = async (req, res, next) => {
    try {
        const { userId } = req.params;
        
        const predictions = await BudgetPrediction.find({ userId })
            .sort({ createdAt: -1 })
            .limit(50);
        
        res.status(200).json({
            success: true,
            count: predictions.length,
            data: predictions
        });
        
    } catch (error) {
        console.error('Error fetching user predictions:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch predictions',
            error: error.message
        });
    }
};

// Get budget predictions by email
export const getBudgetPredictionsByEmail = async (req, res, next) => {
    try {
        const { email } = req.params;
        
        const predictions = await BudgetPrediction.find({ email })
            .sort({ createdAt: -1 })
            .limit(50);
        
        res.status(200).json({
            success: true,
            count: predictions.length,
            data: predictions
        });
        
    } catch (error) {
        console.error('Error fetching predictions by email:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch predictions',
            error: error.message
        });
    }
};

// Get single budget prediction by ID
export const getBudgetPredictionById = async (req, res, next) => {
    try {
        const { id } = req.params;
        
        const prediction = await BudgetPrediction.findById(id);
        
        if (!prediction) {
            return res.status(404).json({
                success: false,
                message: 'Budget prediction not found'
            });
        }
        
        res.status(200).json({
            success: true,
            data: prediction
        });
        
    } catch (error) {
        console.error('Error fetching prediction:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch prediction',
            error: error.message
        });
    }
};

// Get all budget predictions (admin)
export const getAllBudgetPredictions = async (req, res, next) => {
    try {
        const { page = 1, limit = 20, status } = req.query;
        
        const query = status ? { status } : {};
        
        const predictions = await BudgetPrediction.find(query)
            .sort({ createdAt: -1 })
            .limit(limit * 1)
            .skip((page - 1) * limit);
        
        const count = await BudgetPrediction.countDocuments(query);
        
        res.status(200).json({
            success: true,
            count: predictions.length,
            totalPages: Math.ceil(count / limit),
            currentPage: page,
            data: predictions
        });
        
    } catch (error) {
        console.error('Error fetching all predictions:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to fetch predictions',
            error: error.message
        });
    }
};

// Update budget prediction status
export const updateBudgetPredictionStatus = async (req, res, next) => {
    try {
        const { id } = req.params;
        const { status } = req.body;
        
        const prediction = await BudgetPrediction.findByIdAndUpdate(
            id,
            { status },
            { new: true }
        );
        
        if (!prediction) {
            return res.status(404).json({
                success: false,
                message: 'Budget prediction not found'
            });
        }
        
        res.status(200).json({
            success: true,
            message: 'Budget prediction updated successfully',
            data: prediction
        });
        
    } catch (error) {
        console.error('Error updating prediction:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to update prediction',
            error: error.message
        });
    }
};

// Delete budget prediction
export const deleteBudgetPrediction = async (req, res, next) => {
    try {
        const { id } = req.params;
        
        const prediction = await BudgetPrediction.findByIdAndDelete(id);
        
        if (!prediction) {
            return res.status(404).json({
                success: false,
                message: 'Budget prediction not found'
            });
        }
        
        res.status(200).json({
            success: true,
            message: 'Budget prediction deleted successfully'
        });
        
    } catch (error) {
        console.error('Error deleting prediction:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to delete prediction',
            error: error.message
        });
    }
};

// Get budget statistics for a user
export const getUserBudgetStats = async (req, res, next) => {
    try {
        const { userId } = req.params;
        
        const predictions = await BudgetPrediction.find({ userId });
        
        if (predictions.length === 0) {
            return res.status(200).json({
                success: true,
                message: 'No predictions found',
                stats: null
            });
        }
        
        // Calculate statistics
        const totalPredictions = predictions.length;
        const avgMonthlyIncome = predictions.reduce((sum, p) => sum + p.monthly_income, 0) / totalPredictions;
        const avgExpenses = predictions.reduce((sum, p) => sum + p.total_expenses, 0) / totalPredictions;
        const avgSavings = predictions.reduce((sum, p) => sum + p.calculated_savings, 0) / totalPredictions;
        
        const riskDistribution = {
            'Low Risk': predictions.filter(p => p.risk_level === 'Low Risk').length,
            'Medium Risk': predictions.filter(p => p.risk_level === 'Medium Risk').length,
            'High Risk': predictions.filter(p => p.risk_level === 'High Risk').length
        };
        
        const latestPrediction = predictions.sort((a, b) => b.createdAt - a.createdAt)[0];
        
        res.status(200).json({
            success: true,
            stats: {
                totalPredictions,
                avgMonthlyIncome: Math.round(avgMonthlyIncome),
                avgExpenses: Math.round(avgExpenses),
                avgSavings: Math.round(avgSavings),
                riskDistribution,
                latestPrediction: latestPrediction.createdAt,
                currentRiskLevel: latestPrediction.risk_level
            }
        });
        
    } catch (error) {
        console.error('Error calculating stats:', error);
        res.status(500).json({
            success: false,
            message: 'Failed to calculate statistics',
            error: error.message
        });
    }
};
