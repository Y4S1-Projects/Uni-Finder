import express from 'express';
import { getProfiles, getProfileById, createProfile, updateProfile, deleteProfile } from '../controllers/careerProfileController.js';
import { mockAuth } from '../middleware/mockAuth.js';

const router = express.Router();

router.use(mockAuth);

router.get('/', getProfiles);
router.get('/:profileId', getProfileById);
router.post('/', createProfile);
router.put('/:profileId', updateProfile);
router.delete('/:profileId', deleteProfile);

export default router;
