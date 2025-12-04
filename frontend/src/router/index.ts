import { createRouter, createWebHashHistory, RouteRecordRaw } from "vue-router";
import Dashboard from "../views/Dashboard.vue";
import Recommendation from "../views/Recommendation.vue";
import Promotion from "../views/Promotion.vue";
import Forecast from "../views/Forecast.vue";
import Clustering from "../views/Clustering.vue";

const routes: Array<RouteRecordRaw> = [
  { path: "/", name: "dashboard", component: Dashboard },
  { path: "/recommend", name: "recommend", component: Recommendation },
  { path: "/promotion", name: "promotion", component: Promotion },
  { path: "/forecast", name: "forecast", component: Forecast },
  { path: "/clustering", name: "clustering", component: Clustering }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

export default router;
