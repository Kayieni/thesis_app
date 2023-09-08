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
// drawnItems.bindPopup('<table width=250><th>Moment Tensors in this area</th><tr><td>Quality</td><td>A3</td><tr><td colspan="2"><input type = "submit" class="btn btn-success" value = "Confirm" /></td></tr></table>', { maxWidth: 500 });

// initiate the sidepanel
L.Control.SidePanel = L.Control.extend({ includes: L.Evented.prototype, options: { panelPosition: "left", hasTabs: !0, tabsPosition: "top", darkMode: !1, pushControls: !1, startTab: 1 }, initialize: function (t, o) { this._panel = L.DomUtil.get(t), L.setOptions(this, o) }, addTo: function (t) { L.DomUtil.addClass(this._panel, "sidepanel-" + this.options.panelPosition), this.options.darkMode && L.DomUtil.addClass(this._panel, "sidepanel-dark"), L.DomEvent.disableScrollPropagation(this._panel), L.DomEvent.disableClickPropagation(this._panel), this.options.hasTabs && this.initTabs(t, this.options.tabsPosition) }, initTabs: function (t, o) { "string" == typeof o && L.DomUtil.addClass(this._panel, "tabs-" + o); let s = this._panel.querySelectorAll("a.sidebar-tab-link"), e = this._panel.querySelectorAll(".sidepanel-tab-content"); s.forEach(function (t, o) { let i, a; "number" == typeof this.options.startTab && this.options.startTab - 1 === o && (i = t, a = e[o - 1]), "string" == typeof this.options.startTab && this.options.startTab === t.dataset.tabLink && (i = t, a = this._panel.querySelector(`.sidepanel-tab-content[data-tab-content="${this.options.startTab}"]`)), void 0 === i || L.DomUtil.hasClass(i, "active") || (L.DomUtil.addClass(i, "active"), L.DomUtil.addClass(a, "active")), L.DomEvent.on(t, "click", function (o) { if (L.DomEvent.preventDefault(o), !L.DomUtil.hasClass(t, "active")) { for (let t = 0; t < s.length; t++) { let o = s[t]; L.DomUtil.hasClass(o, "active") && L.DomUtil.removeClass(o, "active") } L.DomUtil.addClass(t, "active"), e.forEach(function (o) { t.dataset.tabLink === o.dataset.tabContent ? L.DomUtil.addClass(o, "active") : L.DomUtil.removeClass(o, "active") }) } }, t) }.bind(this)), this._toggleButton(t) }, _toggleButton: function (t) { const o = this._panel.querySelector(".sidepanel-toggle-container"), s = o.querySelector(".sidepanel-toggle-button"); L.DomEvent.on(s, "click", function (o) { let s = !0, e = L.DomUtil.hasClass(this._panel, "opened"), i = L.DomUtil.hasClass(this._panel, "closed"); if (e || i ? !e && i ? (L.DomUtil.addClass(this._panel, "opened"), L.DomUtil.removeClass(this._panel, "closed")) : e && !i ? (s = !1, L.DomUtil.removeClass(this._panel, "opened"), L.DomUtil.addClass(this._panel, "closed")) : L.DomUtil.addClass(this._panel, "opened") : L.DomUtil.addClass(this._panel, "opened"), this.options.pushControls) { let o = t.getContainer().querySelector(".leaflet-control-container"); L.DomUtil.addClass(o, "leaflet-anim-control-container"), s ? (L.DomUtil.removeClass(o, this.options.panelPosition + "-closed"), L.DomUtil.addClass(o, this.options.panelPosition + "-opened")) : (L.DomUtil.removeClass(o, this.options.panelPosition + "-opened"), L.DomUtil.addClass(o, this.options.panelPosition + "-closed")) } }.bind(this), o) } }), L.control.sidepanel = function (t, o) { return new L.Control.SidePanel(t, o) };

const panelRight = L.control.sidepanel('panelID', {
    panelPosition: 'left',
    hasTabs: true,
    tabsPosition: 'left',
    pushControls: true,
    darkMode: true,
    startTab: 'tab-1' //class of starting tab
}).addTo(map);

// Add an event listener to the document to close the panel when clicking outside
document.addEventListener('click', function(event) {
    var panel = document.getElementById('panelID');
    var tabContent = document.getElementById('tab-1');

    if (!panel.contains(event.target)) {
        panel.classList.remove('opened');
        tabContent.innerHTML = '<h4><em>Select an area to view the details</em></h4>'; // Clear the contents of tab-1
    }
});



// create a variable to hold the geojson layer
var selected_geojson;
var selected_area;


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
        console.log(files[i].value)
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
        // for street view of map

        // when an area gets selected
        selected_geojson = L.geoJson(data, {
            onEachFeature: function (feature, featureLayer) {
       
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
                            popup += '<ol id="eventlist">';
                            if (response.length>0) {
                                response.forEach((event, index) => {
                                    // const eventNumber = index + 1;
                                    popup += '<li><a href="#"> Event ID: ' + String(event.id) + " | Strike: " + String(event.try) + " | Dip: "  + String(event.mt) + " | Rake: "  + String(event.mwa) + '<img src="./static/beachballs/beachball_'+ String(event.id) + '.png"/></a></li>';
                                });
                            } else {
                                popup += '<li style="list-style-type: None;"> No seismic events found in this area. </li>';
                            }
                            popup += '</ol>';
                            popup += '</div>';
                            // featureLayer.bindPopup(popup, {
                            //     minWidth: 300,
                            //     maxWidth: 1000
                            // }).openPopup();;


                            this.setStyle({
                                'fillColor': '#0000ff'
                            });
                            featureLayer.bindTooltip(feature.properties.code, { permanent: false, direction: "center", className: "my-labels" });


                            $('#tab-1').html(popup);
                            // Open the side panel
                            $("#panelID").addClass("opened");
                             // Change 'tab-1' to the appropriate tab ID
        

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

        var files_control = {
            "draw": drawnItems,
            "areas": selected_geojson,
        };

        // add map views and scale details to controlers
        L.control.layers(files_control).addTo(map);
        
    });
}


var drawControl = new L.Control.Draw({
    position: 'topright',
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
    var layer = e.layer;
    console.log(layer.toGeoJSON())
    var json_shape = JSON.stringify(layer.toGeoJSON());

    // Create a new layer from the GeoJSON shape for displaying coordinates
    drawnShape = L.geoJSON(JSON.parse(json_shape), {
        style: {
            color: 'red', // Customize the color of the drawn shape
        },
        onEachFeature: function (feature, featureLayer) {
            if (feature.geometry.type === 'Polygon') {
                // drawn_polygon(feature.geometry)
                // data = 
                // console.log(data)
                data_2sent = JSON.stringify(feature.geometry) 
                console.log(data_2sent)
                $.ajax({
                    type: "POST",
                    url: "drawnshape",
                    contentType: "application/json",
                    data: data_2sent,

                    success: function (result) {
                        console.log("Success:", result);

                        var popupContent = '<ul>';
                            for (var i = 0; i < feature.geometry.coordinates[0].length; i++) {
                                var coordinate = feature.geometry.coordinates[0][i];
                                var coordinate_prev = feature.geometry.coordinates[0][i-1];
                                // console.log(coordinate)
                                // console.log(coordinate_prev)
                                if( i==0 || coordinate[1]!== coordinate_prev[1] || coordinate[0]!== coordinate_prev[0]) {
                                    popupContent += '<li>Lat: ' + coordinate[1] + ', Lon: ' + coordinate[0] + '</li>';
                                }
                            }
                            popupContent += '</ul>';
                        featureLayer.bindPopup(popupContent);

                        console.log("yay---2");
                        // Create the content for the popup
                        var popup = '<div class="popup">';
                        // popup += '<h4>' + feature.properties.id + ". " + feature.properties.name + '</h4>';
                        // popup += '<h5>Code: ' + feature.properties.code + '</h4>';
                        popup += '<p>Coordinates:</p>';
                        popup += '<ul>';
                        for (var i = 0; i < feature.geometry.coordinates[0].length - 1; i++) {
                            var coordinate = feature.geometry.coordinates[0][i];
                            popup += '<li>Lat: ' + coordinate[1] + ', Lon: ' + coordinate[0] + '</li>';
                        }
                        popup += '</ul>';
                        // Add the seismic events list
                        popup += '<h5>Seismic Events:</h5>';
                        popup += '<ol id="eventlist">';
                        if (result.length>0) {
                            result.forEach((event, index) => {
                                // const eventNumber = index + 1;
                                popup += '<li><a href="#"> Event ID: ' + String(event.id) + " | Strike: " + String(event.try) + " | Dip: "  + String(event.mt) + " | Rake: "  + String(event.mwa) + '<img src="static/beachballs/beachball_'+ String(event.id) + '.png"/></a></li>';

                            });
                        } else {
                            popup += '<li style="list-style-type: None;"> No seismic events found in this area. </li>';
                        }
                        popup += '</ol>';
                        popup += '</div>';
                        // featureLayer.bindPopup(popup, {
                        //     minWidth: 300,
                        //     maxWidth: 1000
                        // }).openPopup();;


                        // this.setStyle({
                        //     'fillColor': '#0000ff'
                        // });
                        // featureLayer.bindTooltip(feature.properties.code, { permanent: false, direction: "center", className: "my-labels" });


                        $('#tab-1').html(popup);
                        // Open the side panel
                        $("#panelID").addClass("opened");
                            // Change 'tab-1' to the appropriate tab ID
    

                    },
                    error: function(error) {
                        console.error("Error:", error);
                    }
                })
                
            }
        },
    });

    drawnShape.addTo(drawnItems); // Add the drawn layer to the map
});