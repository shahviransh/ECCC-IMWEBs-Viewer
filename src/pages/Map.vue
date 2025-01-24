<template>
    <!-- Main Content -->
    <div :class="[theme, 'content']" :style="{ height: heightVar() }">

        <!-- Component 1: Folder Navigation -->
        <div class="folder-navigation">
            <DatabaseDropdown />
        </div>

        <!-- Component 2: Column Navigation -->
        <div class="column-navigation">
            <ColumnDropdown :selectedDbsTables="selectedDbsTables" />
        </div>
        <div class="right-panel">
            <!-- Component 3: Selection, Interval, Aggregation, and Export Config -->
            <div class="settings-panel">
                <Selection />
                <IntervalDropdown />
                <StatisticsDropdown />
                <ExportConfig />
                <span>
                    <ExportTableStats />
                    <button @click="initializeMap">Fetch Map</button>
                    <button @click="exportData">Export Map</button>
                </span>
            </div>

            <!-- Component 4: Main View -->
            <div class="main-view">
                <!-- Map Display -->
                <div id="map" class="map-container"></div>
            </div>
        </div>
    </div>
</template>

<script>
import { mapState, mapActions } from "vuex";
import DatabaseDropdown from "../components/DatabaseDropdown.vue";
import ColumnDropdown from "../components/ColumnDropdown.vue";
import Selection from "../components/Selection.vue";
import IntervalDropdown from "../components/IntervalDropdown.vue";
import StatisticsDropdown from "../components/StatisticsDropdown.vue";
import ExportConfig from "../components/ExportConfig.vue";
import ExportTableStats from "../components/ExportTableStats.vue";
import axios from 'axios';
import Multiselect from "vue-multiselect";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

export default {
    name: "Map",
    components: {
        DatabaseDropdown,
        ColumnDropdown,
        Selection,
        IntervalDropdown,
        StatisticsDropdown,
        ExportConfig,
        ExportTableStats,
        Multiselect,
    },
    data() {
        return {
            stats: [],
            statsColumns: [],
            data: [],
            ID: [],
            map: null,
            geojson: null,
            bounds: null,
            center: null,
            layers: null,
            properties: null,
            image_url: null,
            raster_bounds: null,
        };
    },
    watch: {
        selectedColumns() {
            this.ID = this.selectedColumns.find((column) => column.includes('ID')) || "";
        },
        selectedGeoFolder(newFolder) {
            if (newFolder) {
                this.fetchGeoJson();
            }
        },
    },
    computed: {
        ...mapState(["selectedDbsTables", "selectedGeoFolder", "selectedColumns", "multiGraphType", "currentZoomStart", "currentZoomEnd", "selectedIds", "dateRange", "selectedInterval", "selectedStatistics", "selectedMethod", "exportColumns", "exportIds", "exportDate", "exportInterval", "dateType", "exportDateType", "exportPath", "exportFilename", "exportFormat", "exportOptions", "theme"]),
    },
    methods: {
        ...mapActions(["updateSelectedColumns", "updateExportOptions", "updateColumns", "pushMessage", "clearMessages"]),
        async fetchGeoJson() {
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/mapbox_shapefile`, {
                    params: {
                        file_path: this.selectedGeoFolder,
                    }
                });

                this.geojson = response.data?.geojson || null;
                this.bounds = response.data.bounds;
                this.center = response.data.center;
                this.layers = response.data.layers;
                this.raster_bounds = response.data?.raster_bounds || null;
                this.image_url = response.data?.image_url || null;
                this.properties = response.data?.properties || [];

                this.updateColumns(this.properties);

                this.pushMessage({ message: `GeoJSON loaded`, type: 'success' });
            } catch (error) {
                alert("Error fetching Mapbox data: ", error);
            }
        },
        initializeMap() {
            mapboxgl.accessToken = this.decodeToken(import.meta.env.VITE_MAPBOX_KEY);

            // Destroy existing map instance if it exists
            if (this.map) {
                this.map.remove();
                this.map = null;
            }

            if (this.selectedColumns.length === 0 && this.properties) {
                this.updateSelectedColumns(this.properties);
            }

            try {
                // Create the Mapbox map instance
                this.map = new mapboxgl.Map({
                    container: "map", // ID of the container
                    style: "mapbox://styles/mapbox/streets-v11",
                    center: this.center || [0, 0], // Use the center provided by the backend or default to [0, 0]
                    zoom: this.image_url ? 12 : 4, // Zoom level for the map
                });

                this.map.on("load", () => {
                    // Add GeoJSON source if present
                    if (this.geojson) {
                        this.map.addSource("shapefile", {
                            type: "geojson",
                            data: this.geojson,
                        });
                    }

                    // Fit map to bounds
                    if (this.bounds) {
                        this.map.fitBounds(this.bounds, { padding: 20 });
                    }

                    // Add geotiff layer if present
                    if (this.image_url) {
                        // Add the rendered PNG as a raster layer
                        this.map.addSource("geotiff", {
                            type: "image",
                            url: `${import.meta.env.VITE_API_BASE_URL}${this.image_url}`,
                            coordinates: this.raster_bounds,
                        });
                    }

                    // Add vector or raster layers from the backend
                    this.layers.forEach((layer) => {
                        this.map.addLayer(layer);
                    });

                    // Initialize popup for vector layers
                    const popup = new mapboxgl.Popup({
                        closeButton: false,
                        closeOnClick: false,
                    });

                    this.layers.forEach((layer) => {
                        // Add hover interaction for vector layers
                        if (layer.type !== "raster") {
                            this.map.on("mousemove", layer.id, (e) => {
                                this.map.getCanvas().style.cursor = "pointer";

                                const feature = e.features[0];

                                // Dynamically generate popup content from properties
                                const popupContent = this.properties
                                    .map((prop) => {
                                        if (this.selectedColumns.includes(prop)) {
                                            const value = feature.properties[prop];
                                            return `<strong>${prop}:</strong> ${typeof value === "number" ? value.toFixed(4) : value ?? "N/A"
                                                }`;
                                        }
                                    })
                                    .join("<br>");

                                popup.setLngLat(e.lngLat).setHTML(popupContent).addTo(this.map);

                                const conditions = this.selectedColumns.map((column) => [
                                    "==",
                                    ["get", column],
                                    feature.properties[column] || null,
                                ]);

                                const filter = ["all", ...conditions];

                                // Apply specific hover effects based on layer type
                                if (layer.type === "fill") {
                                    // Highlight hovered polygon
                                    this.map.setPaintProperty(layer.id, "fill-opacity", [
                                        "case",
                                        filter, // Highlight if conditions are met
                                        0.4, // Highlight opacity
                                        0.0, // Default opacity
                                    ]);
                                } else if (layer.type === "circle") {
                                    // Highlight hovered point
                                    this.map.setPaintProperty(layer.id, "circle-color", [
                                        "case",
                                        filter,
                                        "#FF0000",
                                        "#000000",
                                    ]);
                                } else if (layer.type === "line") {
                                    // Highlight hovered line (optional, example for line opacity)
                                    this.map.setPaintProperty(layer.id, "line-opacity", 0.7);
                                }
                            });

                            // Add mouseleave interaction to reset styles
                            this.map.on("mouseleave", layer.id, () => {
                                this.map.getCanvas().style.cursor = "";
                                popup.remove();

                                // Reset styles based on layer type
                                if (layer.type === "fill") {
                                    this.map.setPaintProperty(layer.id, "fill-opacity", 0.0);
                                } else if (layer.type === "circle") {
                                    this.map.setPaintProperty(layer.id, "circle-color", "#000000");
                                } else if (layer.type === "line") {
                                    this.map.setPaintProperty(layer.id, "line-opacity", 1.0);
                                }
                            });
                        }
                    });
                });

                // Add Mapbox controls
                this.addMapControls();
                const mapDirectory = this.selectedGeoFolder.split("/");
                this.pushMessage({
                    message: `${mapDirectory[mapDirectory.length - 1]} map loaded`,
                    type: "success",
                });
            } catch (error) {
                alert("Error loading Mapbox data: ", error);
            }
        },
        decodeToken(encodedToken) {
            // Reverse the string back
            const reversedString = encodedToken.split('').reverse().join('');

            // Base64 decode
            return atob(reversedString);
        },
        addMapControls() {
            // Fullscreen control
            this.map.addControl(new mapboxgl.FullscreenControl(), "top-right");

            // Geolocation control
            this.map.addControl(
                new mapboxgl.GeolocateControl({
                    positionOptions: {
                        enableHighAccuracy: true,
                    },
                    trackUserLocation: true,
                    showUserHeading: true,
                }),
                "top-right"
            );

            // Scale control
            const scale = new mapboxgl.ScaleControl({
                maxWidth: 200,
                unit: "metric", // Use "imperial" for miles/feet
            });
            this.map.addControl(scale);

            // Compass control
            this.map.addControl(
                new mapboxgl.NavigationControl({ showCompass: true }),
                "top-right"
            );
        },
        columnNeedsSecondaryAxis(column) {
            // Adjust logic based on actual data thresholds
            return this.data.some(row => row[column] > 100);
        },
        heightVar() {
            // Set the height based on the environment
            const isTauri = window.isTauri !== undefined;
            return isTauri ? "calc(100vh - 14vh)" : "calc(100vh - 16vh)";
        },
        // Fetch data from the API
        async fetchData() {
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/get_data`, {
                    params: {
                        db_tables: JSON.stringify(this.selectedDbsTables),
                        columns: JSON.stringify(this.selectedColumns.filter((column) => column !== 'Season')),
                        id: JSON.stringify(this.selectedIds),
                        start_date: this.dateRange.start,
                        end_date: this.dateRange.end,
                        date_type: this.dateType,
                        interval: this.selectedInterval,
                        statistics: JSON.stringify(this.selectedStatistics),
                        method: JSON.stringify(this.selectedMethod),
                    }
                });
                if (response.data.error) {
                    alert('Error fetching data: ' + response.data.error);
                    return;
                }
                if (this.selectedInterval === 'seasonally' && !this.selectedMethod.includes('Equal') && !this.selectedColumns.includes('Season')) {
                    this.updateSelectedColumns(this.selectedColumns.concat(['Season']));
                } else {
                    this.updateSelectedColumns(this.selectedColumns.filter((column) => column !== 'Season'));
                }
                this.data = response.data.data;
                this.stats = response.data.stats;
                this.statsColumns = response.data.statsColumns;

                this.$nextTick(() => {
                    this.pushMessage({ message: `Graph Loaded ${this.selectedColumns.length} columns x ${this.data.length} rows`, type: 'success' });
                });

                this.pushMessage({ message: `Graph Loading ${this.selectedColumns.length} columns x ${this.data.length} rows`, type: 'info' });
            } catch (error) {
                alert('Error fetching data: ' + error.message);
            }
        },
        // Export data to a file
        async exportData() {
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/export_data`, {
                    params: {
                        db_tables: JSON.stringify(this.selectedDbsTables),
                        columns: JSON.stringify(this.exportColumns.filter((column) => column !== 'Season')),
                        id: JSON.stringify(this.exportIds),
                        start_date: this.exportDate.start,
                        end_date: this.exportDate.end,
                        date_type: this.exportDateType,
                        interval: this.exportInterval,
                        statistics: JSON.stringify(this.selectedStatistics),
                        method: JSON.stringify(this.selectedMethod),
                        date_type: this.dateType,
                        export_path: this.exportPath,
                        export_filename: this.exportFilename,
                        export_format: this.exportFormat,
                        options: JSON.stringify(this.exportOptions),
                        graph_type: this.graphType,
                        multi_graph_type: JSON.stringify(this.multiGraphType),
                    }
                });
                if (response.data.error) {
                    alert('Error fetching data: ' + response.data.error);
                    return;
                }
                this.pushMessage({ message: `Exported ${this.exportColumns.length} columns x ${this.data.length} rows`, type: 'info' });
                if (this.selectedInterval === 'seasonally' && !this.selectedMethod.includes('Equal') && !this.selectedColumns.includes('Season')) {
                    this.updateSelectedColumns(this.selectedColumns.concat(['Season']));
                } else {
                    this.updateSelectedColumns(this.selectedColumns.filter((column) => column !== 'Season'));
                }
            } catch (error) {
                alert('Error exporting data: ' + error.message);
            }
        },
    },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
<style src="../assets/pages.css"></style>
<style>
.mapboxgl-ctrl button {
    padding: 0;
    /* Remove extra padding */
    margin: 0;
    /* Remove extra margin */
}
</style>