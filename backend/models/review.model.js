import mongoose from "mongoose";

const adminSchema =new mongoose.Schema({
    petId: {
        type: String,
        required: true,
        unique: true,
        trim: true
    },
    userId: {
        type: String,
        required: true,
        trim: true
    },
    place:{
        type:String,
        required:true,
       
    },
    review:{
        type:String,
        required:true,
      

    },
    
    
},{timestamps:true});

const Review=mongoose.model("Reviewsn",adminSchema)

export default Review;

