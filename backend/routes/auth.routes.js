import express from 'express'
import { signin, signup,signout,allitems ,add_reviews} from '../controllers/auth.controller.js';


const router=express.Router();

router.post("/signup",signup)//register
router.post("/signin",signin)//login

router.get('/signout',signout)




router.get("/users/items",allitems)
router.post("/add_reviews",add_reviews)
export default router