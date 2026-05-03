import express from "express";
import mongoose from "mongoose";
import dotenv from "dotenv";
import Admin from "./models/manager.model.js";
import cors from "cors";
import adminroutes from "./routes/admin.routes.js";
import cookieParser from "cookie-parser";
import authroutes from "./routes/auth.routes.js";
import budgetroutes from "./routes/budget.routes.js";
import scholarshipMatcherRoutes from "./routes/scholarshipMatcherRoutes.js";
import updateDatasetRoutes from "./routes/updateDatasetRoutes.js";
import careerProfileRoutes from "./routes/careerProfileRoutes.js";
dotenv.config();

const PORT = process.env.PORT || 5000;
const LOCAL_MONGO_URI = "mongodb://127.0.0.1:27017/unifinder";
const MONGO_URI = (process.env.MONGO_URI || process.env.MONGO || "").trim();
const ALLOWED_ORIGINS = (process.env.CORS_ORIGINS || "http://localhost:3000,http://localhost:8080")
	.split(",")
	.map((origin) => origin.trim());

mongoose.set("bufferCommands", false);

function sanitizeMongoUri(uri) {
	if (!uri) return "(not configured)";
	return uri.replace(/\/\/([^:]+):([^@]+)@/, "//$1:****@");
}

async function connectMongo() {
	const primaryUri = MONGO_URI || LOCAL_MONGO_URI;
	const connectOptions = { serverSelectionTimeoutMS: 8000 };

	try {
		console.log(`Connecting to MongoDB: ${sanitizeMongoUri(primaryUri)}`);
		await mongoose.connect(primaryUri, connectOptions);
		console.log("MongoDB Connected");
	} catch (err) {
		console.error("MongoDB primary connection failed:", err.message);

		if (primaryUri !== LOCAL_MONGO_URI) {
			try {
				console.log(`Falling back to MongoDB: ${LOCAL_MONGO_URI}`);
				await mongoose.connect(LOCAL_MONGO_URI, connectOptions);
				console.log("MongoDB Connected using local fallback");
				return;
			} catch (fallbackErr) {
				console.error("MongoDB local fallback failed:", fallbackErr.message);
			}
		}
	}
}

mongoose.connection.on("disconnected", () => {
	console.error("MongoDB disconnected");
});

mongoose.connection.on("error", (err) => {
	console.error("MongoDB connection error:", err.message);
});

// Enable CORS for all origins

const app = express();

app.use(express.json());
app.use(cookieParser());

app.use(
	cors({
		origin: ALLOWED_ORIGINS,
		credentials: true,
	}),
);

// Health check endpoint
app.get("/health", (req, res) => {
	res.status(200).json({ status: "ok", service: "backend" });
});

app.use("/api/auth", authroutes);
// app.post('/api/admin/admin_signup', async(req, res) => {
//     const data=new Admin(req.body)
//     await data.save()
//     res.send({success:true,message:"data created successfuly"})
//     res.json({ success: true });
// });

app.use("/api/admin", adminroutes);
app.use("/api/budget", budgetroutes);

app.use("/api/scholarships", scholarshipMatcherRoutes);
app.use("/api", updateDatasetRoutes);
app.use("/api/career-profiles", (req, res, next) => {
	if (mongoose.connection.readyState !== 1) {
		return res.status(503).json({
			success: false,
			message: "Database connection is not ready. Check MongoDB connection.",
		});
	}
	next();
});
app.use("/api/career-profiles", careerProfileRoutes);

app.use((err, req, res, next) => {
	const statusCode = err.statusCode || 500;
	const message = err.message || "internal server error";
	return res.status(statusCode).json({
		success: false,
		message,
		statusCode,
	});
});

//Start server (must be at the end after all routes are defined)
app.listen(PORT, () => {
	console.log(`server listening on port ${PORT}!`);
});

connectMongo();
