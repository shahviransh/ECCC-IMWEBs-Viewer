<template>
    <!-- Main Content -->
    <div :class="[theme, 'content']" :style="{ height: heightVar() }">

        <!-- Component 1: Folder Navigation -->
        <div class="folder-navigation">
            <DatabaseDropdown />
        </div>

        <!-- Component 2: Column Navigation -->
        <div class="column-navigation">
            <ColumnDropdown />
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
                    <button @click="fetchMap">Fetch Map</button>
                    <button @click="exportMap">Export Map</button>
                </span>
            </div>

            <!-- Component 4: Main View -->
            <div class="main-view">
                <!-- Map Display -->
                <div id="map" class="map-container"></div>
            </div>

            <!-- Style Settings Modal -->
            <div v-if="showStylePopup" class="modal-overlay">
                <div class="modal">
                    <h3>Customize Map Style</h3>

                    <div class="style-settings">
                        <label>Polygon Color: <input type="color" v-model="polygonColor"></label>

                        <div class="slider-container">
                            <label>Polygon Opacity:</label>
                            <div class="slider-wrapper">
                                <input type="range" v-model="polygonOpacity" min="0" max="1" step="0.1">
                                <div class="slider-labels">
                                    <span v-for="n in opacitySteps" :key="n">{{ n }}</span>
                                </div>
                            </div>
                        </div>

                        <label>Line Color: <input type="color" v-model="lineColor"></label>

                        <div class="slider-container">
                            <label>Line Opacity:</label>
                            <div class="slider-wrapper">
                                <input type="range" v-model="lineOpacity" min="0" max="1" step="0.1">
                                <div class="slider-labels">
                                    <span v-for="n in opacitySteps" :key="n">{{ n }}</span>
                                </div>
                            </div>
                        </div>

                        <label>Point Color: <input type="color" v-model="pointColor"></label>

                        <div class="slider-container">
                            <label>Point Opacity:</label>
                            <div class="slider-wrapper">
                                <input type="range" v-model="pointOpacity" min="0" max="1" step="0.1">
                                <div class="slider-labels">
                                    <span v-for="n in opacitySteps" :key="n">{{ n }}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="modal-buttons">
                        <button @click="showStylePopup = false">Cancel</button>
                        <button @click="confirmStyleAndInitialize">Confirm</button>
                    </div>
                </div>
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
import 'leaflet/dist/leaflet.css';
import * as L from 'leaflet';
import 'leaflet.fullscreen';
import 'leaflet.fullscreen/Control.FullScreen.css';
import domtoimage from 'dom-to-image-more';
import _ from 'lodash';
import northarrow from "../assets/north-arrow.png";

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
            geojson: {},
            bounds: [],
            center: [],
            properties: [],
            image_urls: [],
            raster_levels: [],
            showStylePopup: false,
            polygonColor: "#3388ff",
            polygonOpacity: 0.0,
            lineColor: "#ff0000",
            lineOpacity: 0.7,
            pointColor: "#000000",
            pointOpacity: 0.8,
            opacitySteps: Array.from({ length: 11 }, (_, i) => (i * 0.1).toFixed(1)),
        };
    },
    watch: {
        selectedColumns() {
            this.ID = this.selectedColumns.find((column) => column.includes('ID')) || "";
        },
        selectedGeoFolders: {
            // Debounce is used to prevent multiple API calls in quick succession
            handler: _.debounce(function (newFolders) {
                if (newFolders.length > 0) {
                    this.fetchGeoJson();
                }
            }, 3000), // Adjust debounce delay as needed
            deep: true
        },
    },
    computed: {
        ...mapState(["selectedGeoFolders", "selectedColumns", "selectedIds", "dateRange", "selectedInterval", "selectedStatistics", "selectedMethod", "exportColumns", "exportIds", "exportDate", "exportInterval", "dateType", "exportDateType", "exportPath", "exportFilename", "exportFormat", "exportOptions", "theme"]),
    },
    methods: {
        ...mapActions(["updateSelectedColumns", "updateToolTipColumns", "updateColumns", "pushMessage", "clearMessages"]),
        confirmStyleAndInitialize() {
            this.showStylePopup = false;
            this.initializeMap(); // Initialize the map with the new styles
        },
        fetchMap() {
            // Destroy existing map instance if it exists
            if (this.map) {
                this.map.remove();
                this.map = null;
            }
            this.showStylePopup = true;
        },
        async fetchGeoJson() {
            try {
                // Fetch GeoTIFF and GeoJSON data from the backend
                const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/geospatial`, {
                    params: {
                        file_paths: JSON.stringify(this.selectedGeoFolders),
                    }
                });

                // Update the map with the fetched GeoTIFF and GeoJSON data
                this.geojson = response.data.geojson;
                this.bounds = response.data.bounds;
                this.center = response.data.center;
                this.image_urls = response.data.image_urls;
                this.properties = response.data.properties;
                this.raster_levels = response.data.raster_levels;

                this.updateToolTipColumns(response.data.tooltip);

                this.updateColumns(this.properties);

                if (response.data.error) {
                    alert("Error fetching Leaflet data: ", response.data.error);
                } else {
                    this.pushMessage({
                        message: this.image_urls.length > 0
                            ? (Object.keys(this.geojson).length > 0 ? 'GeoTIFF and GeoJSON loaded' : 'GeoTIFF loaded')
                            : 'GeoJSON loaded', type: 'success'
                    });
                }
            } catch (error) {
                alert("Error fetching Leaflet data: ", error);
            }
        },
        initializeMap() {
            if (this.selectedColumns.length === 0 && this.properties) {
                this.updateSelectedColumns(this.properties);
            }

            try {
                // Create the Leaflet map instance
                this.map = L.map('map').setView(this.center || [0, 0], 4);

                // Add a tile layer (equivalent to Leaflet styles)
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                    crossOrigin: true
                }).addTo(this.map);

                // Add GeoJSON layer if present
                if (Object.keys(this.geojson).length > 0) {
                    L.geoJSON(this.geojson, {
                        style: (feature) => {
                            // Apply dynamic styles based on geometry type or properties
                            if (feature.geometry.type === 'Polygon' || feature.geometry.type === 'MultiPolygon') {
                                return {
                                    color: this.polygonColor,
                                    weight: 2,
                                    fillColor: this.polygonColor,
                                    fillOpacity: this.polygonOpacity,
                                };
                            } else if (feature.geometry.type === 'LineString' || feature.geometry.type === 'MultiLineString') {
                                return {
                                    color: this.lineColor,
                                    weight: 2,
                                    opacity: this.lineOpacity,
                                };
                            }
                            // Return default styles for unsupported geometry types
                            return {};
                        },
                        pointToLayer: (feature, latlng) => {
                            // Customize the style for points
                            return L.circleMarker(latlng, {
                                radius: 5,
                                fillColor: this.pointColor,
                                color: this.pointColor,
                                weight: 2,
                                opacity: 1,
                                fillOpacity: this.pointOpacity,
                            });
                        },
                        onEachFeature: (feature, layer) => {
                            // Bind hover and click events
                            layer.on('mouseover', (e) => {
                                e.target.setStyle({
                                    fillOpacity: 0.4,
                                    opacity: 1,
                                    weight: 3,
                                });

                                // Generate popup content dynamically
                                const popupContent = Object.entries(feature.properties)
                                    .filter(([key, value]) => this.selectedColumns.includes(key) && value !== null) // Only process selected columns and non-null values
                                    .map(([key, value]) => {
                                        return `<strong>${key}:</strong> ${typeof value === 'number' ? value.toFixed(4) : value ?? 'N/A'}`;
                                    })
                                    .join('<br>');

                                L.popup({ closeButton: false, autoClose: false, autoPan: true, autoPanPadding: [20, 20] })
                                    .setLatLng(e.latlng)
                                    .setContent(popupContent)
                                    .openOn(this.map);
                            });

                            layer.on('mouseout', () => {
                                // Check if the layer has feature data and if it's a Point
                                if (feature.geometry.type === "Point" || feature.geometry.type === "MultiPoint") {
                                    layer.setStyle({
                                        fillOpacity: this.pointOpacity,
                                        weight: 2,
                                    });
                                } else if (feature.geometry.type === "Polygon" || feature.geometry.type === "MultiPolygon") {
                                    layer.setStyle({
                                        fillOpacity: this.polygonOpacity,
                                        weight: 2,
                                    });
                                } else {
                                    layer.setStyle({
                                        opacity: this.lineOpacity,
                                        weight: 2,
                                    });
                                }
                                this.map.closePopup();
                            });
                        },
                    }).addTo(this.map);

                    // Fit map to GeoJSON bounds
                    this.map.fitBounds(this.bounds, { padding: [20, 20] });
                }

                if (this.image_urls.length > 0) {
                    // Add raster images layer using Leaflet ImageOverlay
                    this.image_urls.forEach((url) => {
                        L.imageOverlay(import.meta.env.VITE_API_BASE_URL + url, this.bounds,
                            { opacity: 1.0 }).addTo(this.map);
                    });

                    // Fit map to raster image bounds
                    this.map.fitBounds(this.bounds, { padding: [20, 20] });
                }

                // Add Fullscreen Control
                L.control.fullscreen({
                    position: 'topright',
                    title: 'Toggle Fullscreen',
                    titleCancel: 'Exit Fullscreen',
                    forceSeparateButton: true,
                }).addTo(this.map);

                // Add Scale Control
                L.control.scale({ position: "bottomleft", metric: true, imperial: true }).addTo(this.map);

                if (this.raster_levels.length > 0) {
                    // Create a custom legend control
                    L.Control.RasterLegend = L.Control.extend({
                        onAdd(map) {
                            const div = L.DomUtil.create("div");

                            // Apply container styles
                            div.style.background = "rgba(255, 255, 255, 0.9)";
                            div.style.padding = "12px";
                            div.style.borderRadius = "8px";
                            div.style.boxShadow = "0 2px 10px rgba(0, 0, 0, 0.3)";
                            div.style.fontFamily = "Arial, sans-serif";
                            div.style.fontSize = "14px";
                            div.style.maxWidth = "220px";
                            div.style.border = "1px solid #ccc";
                            div.style.position = "relative";
                            div.style.zIndex = "1000";

                            // Legend title
                            const title = L.DomUtil.create("h4", "", div);
                            title.innerText = "Raster Legend";
                            title.style.textAlign = "center";
                            title.style.fontSize = "16px";
                            title.style.fontWeight = "bold";
                            title.style.color = "#333";
                            title.style.marginBottom = "8px";
                            title.style.marginTop = "0";

                            // Add legend items
                            this.options.raster_levels.forEach(level => {
                                const item = L.DomUtil.create("div", "", div);
                                item.style.display = "flex";
                                item.style.alignItems = "center";
                                item.style.marginBottom = "5px";

                                const colorBox = L.DomUtil.create("span", "", item);
                                colorBox.style.display = "inline-block";
                                colorBox.style.width = "25px";
                                colorBox.style.height = "15px";
                                colorBox.style.borderRadius = "4px";
                                colorBox.style.border = "1px solid #000";
                                colorBox.style.marginRight = "10px";
                                colorBox.style.backgroundColor = level.color;

                                const text = L.DomUtil.create("span", "", item);
                                text.innerText = `${level.min} - ${level.max}`;
                                text.style.whiteSpace = "nowrap";
                                text.style.flex = "1";
                                text.style.color = "#333";
                            });

                            return div;
                        }
                    });

                    // Function to create and add the legend
                    L.control.rasterLegend = (opts) => new L.Control.RasterLegend(opts)

                    // Add the legend to the map (Position: Bottom Left)
                    L.control.rasterLegend({ position: 'bottomleft', raster_levels: this.raster_levels }).addTo(this.map);
                }

                const mapDirectories = this.selectedGeoFolders.map((folder) => folder.split('/').pop());
                this.pushMessage({
                    message: `${mapDirectories.join(", ")} map loaded`,
                    type: 'success',
                });
            } catch (error) {
                alert('Error loading Leaflet data: ', error);
            }
        },
        heightVar() {
            // Set the height based on the environment
            const isTauri = window.isTauri !== undefined;
            return isTauri ? "calc(100vh - 14vh)" : "calc(100vh - 16vh)";
        },
        async exportMap() {
            const mapElement = document.getElementById("map");

            if (!mapElement) {
                alert("Map not found!");
                return;
            }

            L.Control.NorthArrow = L.Control.extend({
                onAdd(map) {
                    // Create an image element for the north arrow
                    const img = L.DomUtil.create("img", "leaflet-north-arrow");
                    img.src = this.options.northarrow;
                    img.style.width = "30px";
                    img.style.position = "relative";
                    img.style.top = "5px";
                    img.style.right = "5px";
                    img.style.zIndex = "1000";

                    return img;
                }
            });

            // Function to create and add the north arrow
            L.control.northArrow = (opts) => new L.Control.NorthArrow(opts);

            // Add it to the map
            const northArrow = L.control.northArrow({ position: 'topright', northarrow });
            northArrow.addTo(this.map);

            // Wait for the north arrow to load before capturing the map
            await new Promise((resolve) => setTimeout(resolve, 500));

            try {
                const blob = await domtoimage.toBlob(mapElement);

                // Convert to File and Send to Backend
                const formData = new FormData();
                formData.append("image", blob, `${this.exportFilename}.${this.exportFormat}`);
                formData.append("export_format", this.exportFormat);
                formData.append("export_path", this.exportPath);
                formData.append("export_filename", this.exportFilename);
                formData.append("file_paths", JSON.stringify(this.selectedGeoFolders));

                // Send to backend
                const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/export_map`, formData, {
                    headers: { "Content-Type": "multipart/form-data" }
                });

                if (response.data.error) {
                    alert("Error exporting map: ", response.data.error);
                } else {
                    this.pushMessage({
                        message: "Map image downloaded successfully",
                        type: "success",
                    });
                }
            } catch (error) {
                console.error("Error capturing map:", error);
            }

            this.map.removeControl(northArrow);
        },
    },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
<style src="../assets/pages.css"></style>

<style scoped>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
}

.modal {
    background: var(--background-color);
    padding: 20px;
    border-radius: 10px;
    width: 300px;
    text-align: center;
}

.modal-buttons {
    margin-top: 15px;
}

.modal-buttons button {
    margin: 5px;
    padding: 5px 10px;
    border: none;
    cursor: pointer;
}

.modal-buttons button:first-child {
    background: green;
    color: white;
}

.modal-buttons button:last-child {
    background: red;
    color: white;
}

.style-settings {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.slider-container {
    display: flex;
    flex-direction: column;
}

.slider-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
}

.slider-wrapper input[type="range"] {
    width: 100%;
}

.slider-labels {
    display: flex;
    justify-content: space-between;
    width: 100%;
    font-size: 12px;
    margin-top: 5px;
}
</style>