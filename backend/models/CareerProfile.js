import mongoose from "mongoose";

const careerProfileSchema = new mongoose.Schema({
    userId: { type: String, required: true },
    profileId: { type: String, required: true },
    name: { type: String, required: true },
    skills: { 
        type: [String],
        validate: {
            validator: function(val) {
                return Array.isArray(val) && val.length >= 5;
            },
            message: "At least 5 skills are required"
        }
    },
    experience_level: { type: String, enum: ["0", "0-1", "1-3", "3-5", "5+"] },
    education_level: { type: String, enum: ["al", "diploma", "bachelors", "masters"] },
    current_status: { type: String, enum: ["student", "graduate", "working"] },
    career_goal: { type: String },
    preferred_domain: { type: String },
    preferred_job_type: { type: String, enum: ["full_time", "internship", "remote"] },
    isDefault: { type: Boolean, default: false }
}, { timestamps: true });

careerProfileSchema.index({ userId: 1, profileId: 1 }, { unique: true });

const CareerProfile = mongoose.model("CareerProfile", careerProfileSchema);

export default CareerProfile;
