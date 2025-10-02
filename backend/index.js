import express from 'express';
import mongoose from 'mongoose';
import dotenv from 'dotenv';
import Admin from "./models/manager.model.js";
import cors from 'cors';
import adminroutes from './routes/admin.routes.js'
import cookieParser from 'cookie-parser';
import authroutes from './routes/auth.routes.js'
dotenv.config();

mongoose.connect(process.env.MONGO).then(()=>{
    console.log('Connected to Mongodb')
}).catch((err)=>{
    console.log(err)
})


// Enable CORS for all origins

const app = express();

app.use(express.json());
app.use(cookieParser());

app.use(cors({
    origin: 'http://localhost:3001', // Replace with your frontend's URL
}));
app.listen(3000, () => {
    console.log('server listen on port 3000!')
});

app.use("/api/auth",authroutes)
// app.post('/api/admin/admin_signup', async(req, res) => {
//     const data=new Admin(req.body)
//     await data.save()
//     res.send({success:true,message:"data created successfuly"})
//     res.json({ success: true });
// });


app.use("/api/admin",adminroutes)

app.use((err,req,res,next)=>{
    const statusCode=err.statusCode||500;
    const message=err.message||'internal server error'
    return res.status(statusCode).json({
        success:false,
        message,
        statusCode,
    })
})