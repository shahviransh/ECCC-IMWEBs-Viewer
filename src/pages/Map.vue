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
                    <button @click="initializeMap">Fetch Map</button>
                    <button @click="exportMap">Export Map</button>
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
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import 'leaflet.fullscreen';
import 'leaflet.fullscreen/Control.FullScreen.css';
import domtoimage from 'dom-to-image-more';

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
        };
    },
    watch: {
        selectedColumns() {
            this.ID = this.selectedColumns.find((column) => column.includes('ID')) || "";
        },
        selectedGeoFolders(newFolders) {
            if (newFolders.length > 0) {
                this.fetchGeoJson();
            }
        },
    },
    computed: {
        ...mapState(["selectedGeoFolders", "selectedColumns", "selectedIds", "dateRange", "selectedInterval", "selectedStatistics", "selectedMethod", "exportColumns", "exportIds", "exportDate", "exportInterval", "dateType", "exportDateType", "exportPath", "exportFilename", "exportFormat", "exportOptions", "theme"]),
    },
    methods: {
        ...mapActions(["updateSelectedColumns", "updateColumns", "pushMessage", "clearMessages"]),
        async fetchGeoJson() {
            try {
                const response = await axios.get(`${import.meta.env.VITE_API_BASE_URL}/api/geospatial`, {
                    params: {
                        file_paths: JSON.stringify(this.selectedGeoFolders),
                    }
                });

                this.geojson = response.data.geojson;
                this.bounds = response.data.bounds;
                this.center = response.data.center;
                this.image_urls = response.data.image_urls;
                this.properties = response.data.properties;

                this.updateToolTipColumns(response.data.tooltip);

                this.updateColumns(this.properties);

                if (response.data.error) {
                    alert("Error fetching Leaflet data: ", response.data.error);
                } else { this.pushMessage({ message: this.image_urls.length > 0 ? 'GeoTIFF loaded' : 'GeoJSON loaded', type: 'success' }); }
            } catch (error) {
                alert("Error fetching Leaflet data: ", error);
            }
        },
        initializeMap() {
            // Destroy existing map instance if it exists
            if (this.map) {
                this.map.remove();
                this.map = null;
            }

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
                if (this.geojson) {
                    L.geoJSON(this.geojson, {
                        style: (feature) => {
                            // Apply dynamic styles based on geometry type or properties
                            if (feature.geometry.type === 'Polygon' || feature.geometry.type === 'MultiPolygon') {
                                return {
                                    color: '#3388ff',
                                    weight: 2,
                                    fillColor: '#3388ff',
                                    fillOpacity: 0,
                                };
                            } else if (feature.geometry.type === 'LineString' || feature.geometry.type === 'MultiLineString') {
                                return {
                                    color: '#ff0000',
                                    weight: 2,
                                    opacity: 0.5,
                                };
                            }
                            // Return default styles for unsupported geometry types
                            return {};
                        },
                        pointToLayer: (feature, latlng) => {
                            // Customize the style for points
                            return L.circleMarker(latlng, {
                                radius: 5,
                                fillColor: "#000000",
                                color: "#000",
                                weight: 2,
                                opacity: 1,
                                fillOpacity: 0.8,
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
                                    .filter(([key]) => this.selectedColumns.includes(key)) // Only process selected columns
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
                                        fillOpacity: 0.8,
                                        weight: 2,
                                    });
                                } else {
                                    layer.setStyle({
                                        fillOpacity: 0,
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

                if (this.image_urls) {
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

                const mapDirectory = this.selectedGeoFolders.split('/');
                this.pushMessage({
                    message: `${mapDirectory[mapDirectory.length - 1]} map loaded`,
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

            try {
                const blob = await domtoimage.toBlob(mapElement);

                // Convert to File and Send to Backend
                const formData = new FormData();
                formData.append("image", blob, `${this.exportFilename}.${this.exportFormat}`);
                formData.append("export_format", this.exportFormat);
                formData.append("export_path", this.exportPath);
                formData.append("export_filename", this.exportFilename);

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
        },
    },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
<style src="../assets/pages.css"></style>