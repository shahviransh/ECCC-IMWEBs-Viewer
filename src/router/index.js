import { createRouter, createWebHistory } from "vue-router";
import App from "../App.vue";
import Project from "../pages/Project.vue";
// import Table from "../components/Table.vue";
// import Graph from "../components/Graph.vue";
// import Map from "../components/Map.vue";
// import Calibration from "../components/Calibration.vue";
// import BMP from "../components/BMP.vue";
// import Tools from "../components/Tools.vue";
// import Help from "../components/Help.vue";

const routes = [
  {
    path: "/",
    component: App,
  },
  {
    path: "/project",
    name: "Project",
    component: Project,
  },
  // {
  //   path: "/table",
  //   name: "Table",
  //   component: Table,
  // },
  // {
  //   path: "/graph",
  //   name: "Graph",
  //   component: Graph,
  // },
  // {
  //   path: "/map",
  //   name: "Map",
  //   component: Map,
  // },
  // {
  //   path: "/calibration",
  //   name: "Calibration",
  //   component: Calibration,
  // },
  // {
  //   path: "/bmp",
  //   name: "BMP",
  //   component: BMP,
  // },
  // {
  //   path: "/tools",
  //   name: "Tools",
  //   component: Tools,
  // },
  // {
  //   path: "/help",
  //   name: "Help",
  //   component: Help,
  // },
];

const router = createRouter({
  history: createWebHistory(), // Use default web history
  routes,
});

export default router;