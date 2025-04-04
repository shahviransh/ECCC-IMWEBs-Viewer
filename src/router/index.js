import { createRouter, createWebHistory } from "vue-router";
import Project from "../pages/Project.vue";
import Graph from "../pages/Graph.vue";
import Map from "../pages/Map.vue";
import Help from "../pages/Help.vue";

const routes = [
  {
    path: "/IMWEBs-Viewer",
    component: Project,
  },
  {
    path: "/IMWEBs-Viewer/project",
    name: "Project",
    component: Project,
  },
  {
    path: "/IMWEBs-Viewer/table",
    name: "Table",
    component: Project,
  },
  {
    path: "/IMWEBs-Viewer/graph",
    name: "Graph",
    component: Graph,
  },
  {
    path: "/IMWEBs-Viewer/map",
    name: "Map",
    component: Map,
  },
  {
    path: "/IMWEBs-Viewer/help",
    name: "Help",
    component: Help,
  },
];

const router = createRouter({
  history: createWebHistory(), // Use default web history
  routes,
});

export default router;