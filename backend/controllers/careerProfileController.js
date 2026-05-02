import CareerProfile from '../models/CareerProfile.js';
import { v4 as uuidv4 } from 'uuid';

const allowedFields = [
    "name",
    "skills",
    "experience_level",
    "education_level",
    "current_status",
    "career_goal",
    "preferred_domain",
    "preferred_job_type",
    "isDefault"
];

const normalizePreferredJobType = (value) => {
    const normalized = String(value || "")
        .trim()
        .toLowerCase()
        .replace(/[\s-]+/g, "_");
    const aliases = {
        fulltime: "full_time",
        full_time: "full_time",
        internship: "internship",
        intern: "internship",
        remote: "remote"
    };
    return aliases[normalized] || undefined;
};

const sanitizeData = (body) => {
    const filteredData = {};
    allowedFields.forEach(field => {
        if (body[field] !== undefined) {
            filteredData[field] = body[field];
        }
    });

    if (filteredData.preferred_job_type !== undefined) {
        const preferredJobType = normalizePreferredJobType(filteredData.preferred_job_type);
        if (preferredJobType) {
            filteredData.preferred_job_type = preferredJobType;
        } else {
            delete filteredData.preferred_job_type;
        }
    }

    if (filteredData.preferred_domain === "") {
        delete filteredData.preferred_domain;
    }

    return filteredData;
};

export const transformProfileToMLInput = (profile) => {
    return {
        user_skill_ids: profile.skills,
        experience_level: profile.experience_level,
        education_level: profile.education_level,
        current_status: profile.current_status,
        career_goal: profile.career_goal,
        preferred_domain: profile.preferred_domain,
        preferred_job_type: profile.preferred_job_type
    };
};

// Get all profiles for a user
export const getProfiles = async (req, res, next) => {
    try {
        const userId = req.user.id;
        const profiles = await CareerProfile.find({ userId }).sort({ updatedAt: -1 });
        res.status(200).json({ success: true, data: profiles });
    } catch (error) {
        next(error);
    }
};

// Get a single profile by ID
export const getProfileById = async (req, res, next) => {
    try {
        const { profileId } = req.params;
        const userId = req.user.id;

        const profile = await CareerProfile.findOne({ profileId, userId });
        
        if (!profile) {
            return res.status(404).json({ success: false, message: "Profile not found" });
        }
        
        res.status(200).json({ success: true, data: profile });
    } catch (error) {
        next(error);
    }
};

// Create a new profile
export const createProfile = async (req, res, next) => {
    try {
        const userId = req.user.id;
        const filteredData = sanitizeData(req.body);
        
        if (!filteredData.name) {
            return res.status(400).json({ success: false, message: "Name is required" });
        }
        if (!filteredData.skills || !Array.isArray(filteredData.skills) || filteredData.skills.length < 5) {
            return res.status(400).json({ success: false, message: "At least 5 skills are required" });
        }

        // Check profile limit
        const profileCount = await CareerProfile.countDocuments({ userId });
        if (profileCount >= 3) {
            return res.status(400).json({ success: false, message: "Maximum 3 profiles allowed per user" });
        }

        const profileId = "prof_" + uuidv4();
        
        const newProfile = new CareerProfile({
            ...filteredData,
            userId,
            profileId
        });

        const savedProfile = await newProfile.save();
        res.status(201).json({ success: true, data: savedProfile });
    } catch (error) {
        next(error);
    }
};

// Update an existing profile
export const updateProfile = async (req, res, next) => {
    try {
        const { profileId } = req.params;
        const userId = req.user.id;
        const filteredData = sanitizeData(req.body);

        if (filteredData.skills && (!Array.isArray(filteredData.skills) || filteredData.skills.length < 5)) {
            return res.status(400).json({ success: false, message: "At least 5 skills are required" });
        }

        const updatedProfile = await CareerProfile.findOneAndUpdate(
            { profileId, userId },
            { $set: filteredData },
            { new: true, runValidators: true }
        );

        if (!updatedProfile) {
            return res.status(404).json({ success: false, message: "Profile not found" });
        }

        res.status(200).json({ success: true, data: updatedProfile });
    } catch (error) {
        next(error);
    }
};

// Delete a profile
export const deleteProfile = async (req, res, next) => {
    try {
        const { profileId } = req.params;
        const userId = req.user.id;

        const deletedProfile = await CareerProfile.findOneAndDelete({ profileId, userId });

        if (!deletedProfile) {
            return res.status(404).json({ success: false, message: "Profile not found" });
        }

        res.status(200).json({ success: true, message: "Profile deleted successfully" });
    } catch (error) {
        next(error);
    }
};
