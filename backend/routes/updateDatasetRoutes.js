import express from "express";
import { triggerUpdate, getStats } from "../controllers/updateDatasetController.js";

const router = express.Router();

// GET /api/update-datasets/stats - Get current dataset statistics
router.get("/update-datasets/stats", getStats);

// POST /api/update-datasets - Trigger dataset update
router.post("/update-datasets", triggerUpdate);

export default router;
