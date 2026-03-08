import User from "../models/user.model.js";

import bcryptjs from 'bcryptjs';
import { errorHandler } from "../utils/error.js";
import jwt from 'jsonwebtoken'
import Review from "../models/review.model.js";

export const signup=async(req,res,next)=>{
    const {username,email,password}=req.body;
    if (!username || !email || !password) {
        return next(errorHandler(400, "Username, email, and password are required"));
    }
    const hashPassword=bcryptjs.hashSync(password,10)
    const newUser=new User({username,email,password:hashPassword});
    try{
        await newUser.save();
        res.status(201).json({ success: true, message: "User created successfully" });
    }catch(error){
        if (error.code === 11000) {
            const field = Object.keys(error.keyPattern || {})[0] || "field";
            return next(errorHandler(400, `${field === "email" ? "Email" : "Username"} already exists`));
        }
        next(error);
    }
}
//login - accepts email or username (if no @, treat as username)
export const signin =async(req,res,next)=>{
    const{email,password}=req.body
    if (!email || !password) {
        return next(errorHandler(400, "Email/username and password are required"));
    }
    try{
        let validUser = await User.findOne({ email });
        if (!validUser && !email.includes("@")) {
            validUser = await User.findOne({ username: email });
        }
        if(!validUser) return next(errorHandler(404,'user not found'));
        const validPassword = bcryptjs.compareSync(password,validUser.password)
        if(!validPassword) return next(errorHandler(401,'wrong credentials'))
            const token=jwt.sign({id:validUser._id},process.env.JWT_SECRET)
        const{password:hashedPassword,...rest}=validUser._doc;

        const expiryDate = new Date(Date.now() + 24 * 60 * 60 * 1000); // 1 day from now
        res.cookie('access_token', token, { httpOnly: true, expires: expiryDate })
        .status(200)
        .json(rest);

    }catch(error){
        next(error)
    }
}


//item register

//item register
export const add_reviews=async(req,res,next)=>{
    const {userId,
        place,
        review,
       
   
        }=req.body;

    //create auto id for orderid
    function idGen(userId){
        const randomString=Math.random().toString(36).substring(2,10);
        const id='ORD'+randomString+userId;
        return id;
    }
    const petId=idGen(userId)
   

    const newItem=new Review({petId,userId,
        place,
        review,
        });
    try{
        await newItem.save();
        res.status(202).json({message:"item created successfully"});
    }catch(error){
        next(error);
    }
   
}






//all items
export const allitems = async (req, res, next) => {
    try{
    
        const orders=await Review.find({})
        res.json(orders)
    }catch(error){
        console.log(error)
        res.status(500).json({error:'Internal server error'})
    }
};








export const signout=(req,res)=>{
    res.clearCookie('access_token').status(200).json('Signout Success')
}