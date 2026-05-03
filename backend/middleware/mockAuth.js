export const mockAuth = (req, res, next) => {
    req.user = {
        id: "demo_user_001",
        email: "demo@unifinder.lk",
        name: "Demo User"
    };
    next();
};
