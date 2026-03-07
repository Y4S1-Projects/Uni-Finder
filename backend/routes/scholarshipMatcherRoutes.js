import express from "express";
import { matchScholarships } from "../../scholarship_and_loan_recommendation_service/controllers/scholarshipMatcherController.js";

const router = express.Router();

// POST /api/scholarships/match
router.post("/match", matchScholarships);

export default router;
