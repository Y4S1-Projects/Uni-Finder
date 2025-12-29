const express = require('express');
const router = express.Router();

const { triggerUpdate, getStats } = require('../controllers/updateDatasetController');

// GET /api/update-datasets/stats - Get current dataset statistics
router.get('/update-datasets/stats', getStats);

// POST /api/update-datasets - Trigger dataset update
router.post('/update-datasets', triggerUpdate);

module.exports = router;





