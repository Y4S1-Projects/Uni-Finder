import express from "express";
import { matchScholarships } from "../controllers/scholarshipMatcherController.js";

const router = express.Router();

// POST /api/scholarships/match
router.post("/match", matchScholarships);

export default router;
