const express = require('express');
const router = express.Router();

const { triggerUpdate } = require('../controllers/updateDatasetController');

// POST /api/update-datasets
router.post('/update-datasets', triggerUpdate);

module.exports = router;




