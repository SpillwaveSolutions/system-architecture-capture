// Auth0 configuration
export const auth0 = {
  domain: process.env.AUTH0_DOMAIN,
  audience: "https://api.northstar.example",
};
// JWT validation middleware using jsonwebtoken
