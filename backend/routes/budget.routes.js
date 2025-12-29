import express from 'express';
import {
    saveBudgetPrediction,
    getUserBudgetPredictions,
    getBudgetPredictionsByEmail,
    getBudgetPredictionById,
    getAllBudgetPredictions,
    updateBudgetPredictionStatus,
    deleteBudgetPrediction,
    getUserBudgetStats
} from '../controllers/budget.controller.js';

const router = express.Router();

// Save new budget prediction
router.post('/save', saveBudgetPrediction);

// Get budget predictions for a specific user
router.get('/user/:userId', getUserBudgetPredictions);

// Get budget predictions by email
router.get('/email/:email', getBudgetPredictionsByEmail);

// Get single budget prediction by ID
router.get('/:id', getBudgetPredictionById);

// Get all budget predictions (admin)
router.get('/', getAllBudgetPredictions);

// Update budget prediction status
router.patch('/:id/status', updateBudgetPredictionStatus);

// Delete budget prediction
router.delete('/:id', deleteBudgetPrediction);

// Get user budget statistics
router.get('/stats/:userId', getUserBudgetStats);

export default router;
