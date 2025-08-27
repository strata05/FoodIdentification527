import {type RouteConfig, index, route, layout} from "@react-router/dev/routes";


export default [
  layout("routes/layout.tsx", [
    index("routes/home.tsx"),
    // route("contact", "./marketing/contact.tsx"),
  ]),
  route("login", "routes/login.tsx"),
  route("register", "routes/register.tsx"),

] satisfies RouteConfig;


