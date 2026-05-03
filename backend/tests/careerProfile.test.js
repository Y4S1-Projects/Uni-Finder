const request = require('supertest');
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const express = require('express');
const { mockAuth } = require('../middleware/mockAuth.js');
const careerProfileRoutes = require('../routes/careerProfileRoutes.js').default;
const CareerProfile = require('../models/CareerProfile.js').default;

const app = express();
app.use(express.json());
// Since Jest tests might run without Babel natively out-of-the-box in this repo,
// and we are using ES modules, we can write an integration test considering the app logic
// If using commonjs for tests we need to be careful with imports. Let's assume standard ES modules or Babel.
app.use('/api/career-profiles', careerProfileRoutes);

let mongoServer;

beforeAll(async () => {
    mongoServer = await MongoMemoryServer.create();
    const uri = mongoServer.getUri();
    await mongoose.connect(uri, {
        useNewUrlParser: true,
        useUnifiedTopology: true,
    });
});

afterAll(async () => {
    await mongoose.disconnect();
    await mongoServer.stop();
});

afterEach(async () => {
    await CareerProfile.deleteMany({});
});

describe('Career Profiles API', () => {
    const validPayload = {
        name: 'My Frontend Profile',
        skills: ['SK001', 'SK002', 'SK003', 'SK004', 'SK005'],
        experience_level: '1-3',
        education_level: 'bachelors',
        current_status: 'graduate',
        career_goal: 'first_job',
        preferred_domain: 'FRONTEND_ENGINEERING',
        preferred_job_type: 'full_time'
    };

    it('should create a profile successfully (valid payload, expect 201)', async () => {
        const response = await request(app)
            .post('/api/career-profiles')
            .send(validPayload);
        
        expect(response.status).toBe(201);
        expect(response.body.success).toBe(true);
        expect(response.body.data.name).toBe('My Frontend Profile');
        expect(response.body.data.skills.length).toBe(5);
        expect(response.body.data.profileId).toBeDefined();
    });

    it('should fail to create a profile with less than 5 skills', async () => {
        const invalidPayload = {
            ...validPayload,
            skills: ['SK001', 'SK002']
        };

        const response = await request(app)
            .post('/api/career-profiles')
            .send(invalidPayload);

        expect(response.status).toBe(400);
        expect(response.body.success).toBe(false);
        expect(response.body.message).toContain('At least 5 skills are required');
    });

    it('should enforce the maximum of 3 profiles limit', async () => {
        await request(app).post('/api/career-profiles').send(validPayload);
        await request(app).post('/api/career-profiles').send({...validPayload, name: 'Profile 2'});
        await request(app).post('/api/career-profiles').send({...validPayload, name: 'Profile 3'});
        
        // 4th should fail
        const response = await request(app)
            .post('/api/career-profiles')
            .send({...validPayload, name: 'Profile 4'});
            
        expect(response.status).toBe(400);
        expect(response.body.success).toBe(false);
        expect(response.body.message).toBe('Maximum 3 profiles allowed per user');
    });

    it('should fetch profiles returning only current user profiles', async () => {
        await request(app).post('/api/career-profiles').send(validPayload);
        
        const response = await request(app).get('/api/career-profiles');
        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data.length).toBe(1);
    });

    it('should update a profile successfully', async () => {
        const createRes = await request(app).post('/api/career-profiles').send(validPayload);
        const profileId = createRes.body.data.profileId;

        const response = await request(app)
            .put(`/api/career-profiles/${profileId}`)
            .send({ name: 'Updated Name', skills: ['SK01', 'SK02', 'SK03', 'SK04', 'SK05', 'SK06'] });

        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
        expect(response.body.data.name).toBe('Updated Name');
    });

    it('should delete a profile successfully', async () => {
        const createRes = await request(app).post('/api/career-profiles').send(validPayload);
        const profileId = createRes.body.data.profileId;

        const response = await request(app).delete(`/api/career-profiles/${profileId}`);
        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);

        const getRes = await request(app).get('/api/career-profiles');
        expect(getRes.body.data.length).toBe(0);
    });

    it('should return 404 for invalid update (wrong profileId)', async () => {
        const response = await request(app)
            .put('/api/career-profiles/invalid_id')
            .send({ name: 'Update attempt' });

        expect(response.status).toBe(404);
        expect(response.body.success).toBe(false);
    });
});
