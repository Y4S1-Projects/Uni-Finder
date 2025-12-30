const express = require('express');
const router = express.Router();

const { matchScholarships } = require('../controllers/scholarshipMatcherController');

// POST /api/scholarships/match
router.post('/match', matchScholarships);

module.exports = router;


