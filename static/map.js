// initiate the leaflet

var map = L.map('map');
// center of the map to Greece
map.setView([39, 25], 6);

// for satelite view of map
var Esri_WorldImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
}).addTo(map);
// for street view of map
var Esri_WorldStreetMap = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012'
});

var baseMaps = {
    "Satellite View": Esri_WorldImagery,
    "Street View": Esri_WorldStreetMap,
};
// add map views and scale details to controlers
L.control.layers(baseMaps).addTo(map);
L.control.scale({ position: 'bottomright' }).addTo(map);


// the group of points added to the map
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);
drawnItems.bindPopup('<table width=250><th>Moment Tensors in this area</th><tr><td>Quality</td><td>A3</td><tr><td colspan="2"><input type = "submit" class="btn btn-success" value = "Confirm" /></td></tr></table>', { maxWidth: 500 });

// create a variable to hold the geojson layer
var selected_geojson;
var selected_area;
// Function to toggle the GeoJSON layer visibility
// function toggleGeoJSONLayer() {
//     if (map.hasLayer(selected_geojson)) {
//         map.removeLayer(selected_geojson);
//     } else {
//         map.addLayer(selected_geojson);
//     }
// }

// console.log(selected_geojson);

// JavaScript to display the modal when the page loads
$(document).ready(function () {
    $('#questionModal').modal('show');
});

// Additional JavaScript for the modal in order to add the selected layer
function updateMap() {
    // Get the user's answer from the input field in the modal (which json file they want)
    var files = document.getElementsByName('selectedArea');

    // find the selection of the user
    for (i = 0; i < files.length; i++) {
        if (files[i].checked) {
            var answer = files[i].value;

            // Close the modal
            $('#questionModal').modal('hide');

            // Use the user's answer to update the map layer
            var selected = document.getElementById('selectedArea_file');
            selected.value = answer;
        }
    }

    // based on the selected area, find the corresponding file to add as layer
    var selectedAreaFile = $("#selectedArea_file").val();
    console.log("Selected Area File:", selectedAreaFile);

    // Load the selected GeoJSON data and create the layer
    $.getJSON("/static/data/" + $("#selectedArea_file").val(), function (data) {
        // Create the GeoJSON layer with custom popup content
        selected_geojson = L.geoJson(data, {
            onEachFeature: function (feature, featureLayer) {
                // Create the content for the popup
                // var popup = '<div class="popup">';
                // popup += '<h4>' + feature.properties.id + ". " + feature.properties.name + '</h4>';
                // popup += '<h5>Code: ' + feature.properties.code + '</h4>';
                // popup += '<p>Coordinates:</p>';
                // popup += '<ul>';
                // for (var i = 0; i < feature.geometry.coordinates[0].length - 1; i++) {
                //     var coordinate = feature.geometry.coordinates[0][i];
                //     popup += '<li>Lat: ' + coordinate[1] + ', Lon: ' + coordinate[0] + '</li>';
                // }
                // popup += '</ul>';
                // // Add the seismic events list
                // popup += '<h5>Seismic Events:</h5>';
                // popup += '<ul id="eventlist">';
                // // Add your seismic events data here
                // popup += '<li>Event 1</li>';
                // popup += '<li>Event 2</li>';
                // popup += '<li>Event 3</li>';
                // // ...
                // popup += '</ul>';
                // popup += '</div>';

                async function eventsperarea(areacode) {
                    const response = await fetch('/' + areacode);
                    // + new URLSearchParams({ postId: 1 }).toString());
                    const json = await response.json();
                    console.log(json);
                    return json;
                }


                featureLayer.on('click', function () {
                    console.log(feature.properties.code);
                    eventsperarea(feature.properties.code)
                        .then(response => {
                            console.log("yay");
                            // Create the content for the popup
                            var popup = '<div class="popup">';
                            popup += '<h4>' + feature.properties.id + ". " + feature.properties.name + '</h4>';
                            popup += '<h5>Code: ' + feature.properties.code + '</h4>';
                            popup += '<p>Coordinates:</p>';
                            popup += '<ul>';
                            for (var i = 0; i < feature.geometry.coordinates[0].length - 1; i++) {
                                var coordinate = feature.geometry.coordinates[0][i];
                                popup += '<li>Lat: ' + coordinate[1] + ', Lon: ' + coordinate[0] + '</li>';
                            }
                            popup += '</ul>';
                            // Add the seismic events list
                            popup += '<h5>Seismic Events:</h5>';
                            popup += '<ul id="eventlist">';
                            response.forEach((event, index) => {
                                const eventNumber = index + 1;
                                popup += '<li>' + eventNumber +':  <a href="#">' + String(event.mt).split("geofon/")[1] + '</a></li>';
                            });
                            popup += '</ul>';
                            popup += '</div>';
                            featureLayer.bindPopup(popup, {
                                minWidth: 300,
                                maxWidth: 1000
                            });
                        })
                        .catch(error => {
                            console.log("error!");
                            console.error(error);
                        });
                });
                

                featureLayer.on('mouseover', function () {
                    this.setStyle({
                        'fillColor': '#0000ff'
                    });
                    featureLayer.bindTooltip(feature.properties.code, { permanent: false, direction: "center", className: "my-labels" });

                });

                featureLayer.on('mouseout', function () {
                    this.setStyle({
                        'fillColor': '#3388ff'
                    });
                });
            }
        });

        // Add the layer to the map
        map.addLayer(selected_geojson);
        map.fitBounds(selected_geojson.getBounds());
    });



}

// // Create the toggle button
// var toggleButton = L.control({ position: 'topright' });
// toggleButton.onAdd = function (map) {
//     var buttonDiv = L.DomUtil.create('div', 'toggle-button');
//     buttonDiv.innerHTML = '<input type="checkbox" id="toggle-layer" onclick="toggleGeoJSONLayer()"><label for="toggle-layer">Toggle Layer</label>';
//     return buttonDiv;
// };
// toggleButton.addTo(map);

L.Control.SidePanel = L.Control.extend({ includes: L.Evented.prototype, options: { panelPosition: "left", hasTabs: !0, tabsPosition: "top", darkMode: !1, pushControls: !1, startTab: 1 }, initialize: function (t, o) { this._panel = L.DomUtil.get(t), L.setOptions(this, o) }, addTo: function (t) { L.DomUtil.addClass(this._panel, "sidepanel-" + this.options.panelPosition), this.options.darkMode && L.DomUtil.addClass(this._panel, "sidepanel-dark"), L.DomEvent.disableScrollPropagation(this._panel), L.DomEvent.disableClickPropagation(this._panel), this.options.hasTabs && this.initTabs(t, this.options.tabsPosition) }, initTabs: function (t, o) { "string" == typeof o && L.DomUtil.addClass(this._panel, "tabs-" + o); let s = this._panel.querySelectorAll("a.sidebar-tab-link"), e = this._panel.querySelectorAll(".sidepanel-tab-content"); s.forEach(function (t, o) { let i, a; "number" == typeof this.options.startTab && this.options.startTab - 1 === o && (i = t, a = e[o - 1]), "string" == typeof this.options.startTab && this.options.startTab === t.dataset.tabLink && (i = t, a = this._panel.querySelector(`.sidepanel-tab-content[data-tab-content="${this.options.startTab}"]`)), void 0 === i || L.DomUtil.hasClass(i, "active") || (L.DomUtil.addClass(i, "active"), L.DomUtil.addClass(a, "active")), L.DomEvent.on(t, "click", function (o) { if (L.DomEvent.preventDefault(o), !L.DomUtil.hasClass(t, "active")) { for (let t = 0; t < s.length; t++) { let o = s[t]; L.DomUtil.hasClass(o, "active") && L.DomUtil.removeClass(o, "active") } L.DomUtil.addClass(t, "active"), e.forEach(function (o) { t.dataset.tabLink === o.dataset.tabContent ? L.DomUtil.addClass(o, "active") : L.DomUtil.removeClass(o, "active") }) } }, t) }.bind(this)), this._toggleButton(t) }, _toggleButton: function (t) { const o = this._panel.querySelector(".sidepanel-toggle-container"), s = o.querySelector(".sidepanel-toggle-button"); L.DomEvent.on(s, "click", function (o) { let s = !0, e = L.DomUtil.hasClass(this._panel, "opened"), i = L.DomUtil.hasClass(this._panel, "closed"); if (e || i ? !e && i ? (L.DomUtil.addClass(this._panel, "opened"), L.DomUtil.removeClass(this._panel, "closed")) : e && !i ? (s = !1, L.DomUtil.removeClass(this._panel, "opened"), L.DomUtil.addClass(this._panel, "closed")) : L.DomUtil.addClass(this._panel, "opened") : L.DomUtil.addClass(this._panel, "opened"), this.options.pushControls) { let o = t.getContainer().querySelector(".leaflet-control-container"); L.DomUtil.addClass(o, "leaflet-anim-control-container"), s ? (L.DomUtil.removeClass(o, this.options.panelPosition + "-closed"), L.DomUtil.addClass(o, this.options.panelPosition + "-opened")) : (L.DomUtil.removeClass(o, this.options.panelPosition + "-opened"), L.DomUtil.addClass(o, this.options.panelPosition + "-closed")) } }.bind(this), o) } }), L.control.sidepanel = function (t, o) { return new L.Control.SidePanel(t, o) };

const panelRight = L.control.sidepanel('panelID', {
    panelPosition: 'right',
    hasTabs: true,
    tabsPosition: 'top',
    pushControls: true,
    darkMode: true,
    startTab: 'sidepanel-tab' //class of starting tab
}).addTo(map);

var drawControl = new L.Control.Draw({
    position: 'topleft',
    draw: {
        polygon: {
            shapeOptions: {
                color: 'purple' //polygons being drawn will be purple color
            },
            allowIntersection: true, // Will decide whether the line can intersect or not. If not an error message will be shown and drawing intersected lines will be prohibited
            drawError: {
                color: 'orange',
                timeout: 1000
            },
            showArea: true, //the area of the polygon will be displayed as it is drawn.
            metric: false,
            repeatMode: false //Prevents having to select the previously selected tool to draw another layer
        },
        polyline: false,
        circlemarker: false, //circlemarker type has been disabled.
        rect: {
            shapeOptions: {
                color: 'green'
            },
        },
        circle: false,
    },
    edit: {
        featureGroup: drawnItems
    }
});

map.addControl(drawControl);
map.on('draw:created', function (e) {
    var type = e.layerType,
        layer = e.layer;
    console.log(layer)
    drawnItems.addLayer(layer); //the layer is added to the map
    $('#polygon').val(JSON.stringify(layer.toGeoJSON())); //saving the layer to the input field using jQuery
    var json_shape = JSON.stringify(layer.toGeoJSON());
    // restore
    L.geoJSON(JSON.parse(json_shape)).addTo(map);
});
