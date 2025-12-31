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
dotenv.config();

const PORT = process.env.PORT || 5000;
const ALLOWED_ORIGINS = (process.env.CORS_ORIGINS || "http://localhost:3000,http://localhost:8080")
	.split(",")
	.map((origin) => origin.trim());

mongoose
	.connect(process.env.MONGO)
	.then(() => {
		console.log("Connected to Mongodb");
	})
	.catch((err) => {
		console.log(err);
	});

// Enable CORS for all origins

const app = express();

app.use(express.json());
app.use(cookieParser());

app.use(
	cors({
		origin: ALLOWED_ORIGINS,
		credentials: true,
	})
);

app.listen(PORT, () => {
	console.log(`server listening on port ${PORT}!`);
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

app.use((err, req, res, next) => {
	const statusCode = err.statusCode || 500;
	const message = err.message || "internal server error";
	return res.status(statusCode).json({
		success: false,
		message,
		statusCode,
	});
});
