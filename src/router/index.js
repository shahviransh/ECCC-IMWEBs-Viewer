import { createRouter, createWebHistory } from "vue-router";
import Project from "../pages/Project.vue";
import Table from "../pages/Table.vue";
import Graph from "../pages/Graph.vue";
import Map from "../pages/Map.vue";
import Calibration from "../pages/Calibration.vue";
import BMP from "../pages/BMP.vue";
import Tools from "../pages/Tools.vue";
import Help from "../pages/Help.vue";

const routes = [
  {
    path: "/",
    component: Project,
  },
  {
    path: "/project",
    name: "Project",
    component: Project,
  },
  {
    path: "/table",
    name: "Table",
    component: Table,
  },
  {
    path: "/graph",
    name: "Graph",
    component: Graph,
  },
  {
    path: "/map",
    name: "Map",
    component: Map,
  },
  {
    path: "/calibration",
    name: "Calibration",
    component: Calibration,
  },
  {
    path: "/bmp",
    name: "BMP",
    component: BMP,
  },
  {
    path: "/tools",
    name: "Tools",
    component: Tools,
  },
  {
    path: "/help",
    name: "Help",
    component: Help,
  },
];

const router = createRouter({
  history: createWebHistory(), // Use default web history
  routes,
});

export default router;