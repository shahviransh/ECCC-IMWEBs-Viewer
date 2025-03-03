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
            <div v-if="showStylePopup" class="modal-overlay-select">
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
            <div v-if="showTableStatsPopup" class="modal-overlay">
                <div class="modal" @mousedown="startDrag" :style="{ top: modalPosition.top, left: modalPosition.left }"
                    :key="modalKey">
                    <button class="close-button" @click="showTableStatsPopup = false">&times;</button>
                    <TableStatsDisplay :data="data" :stats="stats" :statsColumns="statsColumns" :properties="properties"
                        :selectedColumns="selectedColumns" :rowLimit="rowLimit" />
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
import TableStatsDisplay from "../components/TableStatsDisplay.vue";
import axios from 'axios';
import 'leaflet/dist/leaflet.css';
import * as L from 'leaflet';
import 'leaflet.fullscreen';
import 'leaflet.fullscreen/Control.FullScreen.css';
import _ from 'lodash';
import northarrow from "../assets/north-arrow.png";
import northarrowwhite from "../assets/north-arrow-white.png";

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
        TableStatsDisplay,
    },
    data() {
        return {
            stats: [],
            statsColumns: [],
            data: [],
            ID: '',
            map: null,
            geojson: {},
            bounds: [],
            center: [],
            properties: [],
            image_urls: [],
            raster_levels: [],
            showStylePopup: false,
            polygonOpacity: 0.0,
            lineOpacity: 0.7,
            pointOpacity: 0.8,
            opacitySteps: Array.from({ length: 11 }, (_, i) => (i * 0.1).toFixed(1)),
            showTableStatsPopup: false,
            selectedFeatureId: null,
            rowLimit: 100,
            modalKey: 0,
            modalPosition: {
                top: "50%",
                left: "50%",
                transform: "translate(-50%, -50%)"
            },
            dragging: false,
            offset: { x: 0, y: 0 },
        };
    },
    watch: {
        selectedGeoFolders: {
            // Debounce is used to prevent multiple API calls in quick succession
            handler: _.debounce(function (newFolders) {
                if (newFolders.length > 0) {
                    this.fetchGeoJson();
                }
            }, 1000), // Adjust debounce delay as needed
            deep: true
        },
    },
    computed: {
        ...mapState(["selectedDbsTables", "selectedGeoFolders", "selectedMonth", "selectedSeason", "selectedColumns", "allSelectedColumns", "selectedIds", "dateRange", "selectedInterval", "selectedStatistics", "selectedMethod", "exportColumns", "exportIds", "exportDate", "exportInterval", "dateType", "exportDateType", "exportPath", "exportFilename", "exportFormat", "exportOptions", "theme"]),
        polygonColor() {
            return this.theme === 'light' ? "#3388ff" : "#ff9800";
        },
        lineColor() {
            return this.theme === 'light' ? "#ff0000" : "#03A9F4";
        },
        pointColor() {
            return this.theme === 'light' ? "#000000" : "#ff5722";
        },
    },
    methods: {
        ...mapActions(["updateSelectedColumns", "addColumns", "updateToolTipColumns", "updateAllSelectedColumns", "updateSelectedIds", "updateColumns", "pushMessage", "clearMessages"]),
        arraysAreEqual(arr1, arr2) {
            if (arr1.length !== arr2.length) return false; // Different lengths → Not equal

            const sorted1 = [...arr1].sort();
            const sorted2 = [...arr2].sort();

            // Compare every element in both arrays
            return sorted1.every((value, index) => value === sorted2[index]);
        },
        openModal() {
            this.modalKey++; // Change key to re-mount modal
            this.showTableStatsPopup = true;
        },
        startDrag(event) {
            this.dragging = true;
            this.offset = {
                x: event.clientX - event.target.closest('.modal').offsetLeft,
                y: event.clientY - event.target.closest('.modal').offsetTop,
            };
            document.addEventListener("mousemove", this.onDrag);
            document.addEventListener("mouseup", this.stopDrag);
        },
        onDrag(event) {
            if (!this.dragging) return;
            this.modalPosition = {
                top: `${event.clientY - this.offset.y}px`,
                left: `${event.clientX - this.offset.x}px`,
                transform: "none" // Disable centering after drag starts
            };
        },
        stopDrag() {
            this.dragging = false;
            document.removeEventListener("mousemove", this.onDrag);
            document.removeEventListener("mouseup", this.stopDrag);
        },
        confirmStyleAndInitialize() {
            this.showStylePopup = false;
            // Choose all the columns if they are not selected
            if (this.selectedColumns.length === 0 || this.arraysAreEqual(this.selectedColumns, this.properties)) {
                this.updateSelectedColumns("All");
                this.updateAllSelectedColumns(true);
            }

            this.initializeMap(); // Initialize the map with the new styles
        },
        async fetchData() {
            // Clear data before setting new data
            this.data = [];
            this.statsColumns = [];
            this.stats = [];

            // Fetch the API data for the map
            const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/get_data`, {
                params: {
                    db_tables: JSON.stringify(this.selectedDbsTables),
                    columns: JSON.stringify(this.allSelectedColumns ? "All" : this.selectedColumns.filter((column) => column !== 'Season' && !this.properties.includes(column))),
                    id: JSON.stringify([this.selectedFeatureId.toString()]),
                    start_date: this.dateRange.start,
                    end_date: this.dateRange.end,
                    date_type: this.dateType,
                    interval: this.selectedInterval,
                    statistics: JSON.stringify(this.selectedStatistics),
                    method: JSON.stringify(this.selectedMethod),
                    month: JSON.stringify(this.selectedMonth),
                    season: JSON.stringify(this.selectedSeason),
                }
            });
            if (this.selectedInterval === 'seasonally' && !this.selectedMethod.includes('Equal') && !this.selectedColumns.includes('Season')) {
                this.updateSelectedColumns(this.selectedColumns.concat(['Season']));
            } else if (this.selectedColumns.includes('Season') && this.selectedInterval !== 'seasonally') {
                this.updateSelectedColumns(this.selectedColumns.filter((column) => column !== 'Season'));
            }
            this.data = response.data.data;
            this.stats = response.data.stats;
            this.statsColumns = response.data.statsColumns;
            this.ID = this.selectedColumns.find((column) => column.includes('ID'));
            if (response.data.error) {
                alert('Error fetching data: ' + response.data.error);
                return;
            } else {
                // Wait until the table has rendered, then trigger messages
                this.$nextTick(() => {
                    this.pushMessage({ message: `Fetched ${this.selectedColumns.length} columns x ${this.data.length} rows`, type: 'success' });
                    this.pushMessage({ message: `Loaded ${this.rowLimit} rows`, type: 'success' });
                    if (this.statsColumns.length > 0) {
                        this.pushMessage({ message: `Fetched ${this.statsColumns.length} statistics columns for ${this.selectedMethod || this.selectedStatistics}`, type: 'success' });
                    }
                });
            }
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

                this.addColumns(this.properties);

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
                console.error("Error fetching Leaflet data: ", error);
            }
        },
        initializeMap() {
            try {
                // Create the Leaflet map instance
                this.map = L.map('map').setView(this.center || [0, 0], 12);

                // Add a tile layer (equivalent to Leaflet styles)
                L.tileLayer(this.theme === 'light' ? 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png' : 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
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
                            // Bind click events to open table statistics popup
                            layer.on("click", () => {
                                const featureId = Object.entries(feature.properties)
                                    .filter(([key, value]) => key.toLowerCase().includes(this.ID.toLowerCase()) && value !== null)
                                    .map(([, value]) => value)?.[0] ?? null;
                                if (!featureId) {
                                    return;
                                }
                                this.selectedFeatureId = featureId;
                                if (this.selectedDbsTables.length > 0) {
                                    this.fetchData();
                                }

                                setTimeout(() => {
                                    this.openModal();
                                }, 100);
                            });

                            // Bind hover events to display popup
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
                }

                if (this.image_urls.length > 0) {
                    // Add raster images layer using Leaflet ImageOverlay
                    this.image_urls.forEach((url) => {
                        L.imageOverlay(import.meta.env.VITE_API_BASE_URL + url, this.bounds,
                            { opacity: 1.0 }).addTo(this.map);
                    });
                }

                this.map.fitBounds(this.bounds);

                // Add Fullscreen Control
                L.control.fullscreen({
                    position: 'topright',
                    title: 'Toggle Fullscreen',
                    titleCancel: 'Exit Fullscreen',
                    forceSeparateButton: true,
                }).addTo(this.map);

                // Add Scale Control
                L.control.scale({ position: "bottomleft", metric: true, imperial: true }).addTo(this.map);

                const mapDirectories = this.selectedGeoFolders.map((folder) => folder.split('/').pop());

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
                            title.innerText = `${this.options.tifFiles} Legend`;
                            title.style.textAlign = "center";
                            title.style.fontSize = "16px";
                            title.style.fontWeight = "bold";
                            title.style.color = this.options.theme === 'light' ? "#333" : "#fff";
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
                                text.style.color = this.options.theme === 'light' ? "#333" : "#fff";
                            });

                            return div;
                        }
                    });

                    // Function to create and add the legend
                    L.control.rasterLegend = (opts) => new L.Control.RasterLegend(opts)

                    // Add the legend to the map (Position: Bottom Left)
                    L.control.rasterLegend({ position: 'bottomleft', raster_levels: this.raster_levels, theme: this.theme, tifFiles: mapDirectories.filter(c => c.includes('.tif')).join(",") }).addTo(this.map);
                }

                this.pushMessage({
                    message: `${mapDirectories.join(", ")} map loaded`,
                    type: 'success',
                });
            } catch (error) {
                console.error('Error loading Leaflet data: ', error);
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
            const northArrow = L.control.northArrow({ position: 'topright', northarrow: this.theme === 'light' ? northarrow : northarrowwhite });
            northArrow.addTo(this.map);

            // Wait for the north arrow to load before capturing the map
            await new Promise((resolve) => setTimeout(resolve, 500));

            try {
                const domtoimage = await import("dom-to-image-more");
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
<style src="../assets/pages.css"></style>

<style scoped>
/* Theme variables */
.light {
    --background-color: white;
    --text-color: black;
    --button-primary: green;
    --button-danger: red;
    --overlay-background: rgba(0, 0, 0, 0.5);
}

.dark {
    --background-color: #222;
    --text-color: white;
    --button-primary: #28a745;
    --button-danger: #dc3545;
    --overlay-background: rgba(0, 0, 0, 0.8);
}

.modal-overlay,
.modal-overlay-select {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-overlay-select {
    background: var(--overlay-background);
}

.modal {
    position: absolute;
    background: var(--background-color);
    padding: 20px;
    border-radius: 10px;
    width: 25%;
    text-align: center;
    color: var(--text-color);
}

.modal-buttons {
    margin-top: 15px;
}

.modal-buttons button {
    margin: 5px;
    padding: 5px 10px;
    border: none;
    cursor: pointer;
    color: white;
}

.modal-buttons button:first-child {
    background: var(--button-primary);
}

.modal-buttons button:last-child {
    background: var(--button-danger);
}

.close-button {
    position: absolute;
    top: 0px;
    right: 0px;
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: var(--text-color);
    z-index: 1100;
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