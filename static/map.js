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

// initiate the sidepanel
L.Control.SidePanel = L.Control.extend({ includes: L.Evented.prototype, options: { panelPosition: "left", hasTabs: !0, tabsPosition: "top", darkMode: !1, pushControls: !1, startTab: 1 }, initialize: function (t, o) { this._panel = L.DomUtil.get(t), L.setOptions(this, o) }, addTo: function (t) { L.DomUtil.addClass(this._panel, "sidepanel-" + this.options.panelPosition), this.options.darkMode && L.DomUtil.addClass(this._panel, "sidepanel-dark"), L.DomEvent.disableScrollPropagation(this._panel), L.DomEvent.disableClickPropagation(this._panel), this.options.hasTabs && this.initTabs(t, this.options.tabsPosition) }, initTabs: function (t, o) { "string" == typeof o && L.DomUtil.addClass(this._panel, "tabs-" + o); let s = this._panel.querySelectorAll("a.sidebar-tab-link"), e = this._panel.querySelectorAll(".sidepanel-tab-content"); s.forEach(function (t, o) { let i, a; "number" == typeof this.options.startTab && this.options.startTab - 1 === o && (i = t, a = e[o - 1]), "string" == typeof this.options.startTab && this.options.startTab === t.dataset.tabLink && (i = t, a = this._panel.querySelector(`.sidepanel-tab-content[data-tab-content="${this.options.startTab}"]`)), void 0 === i || L.DomUtil.hasClass(i, "active") || (L.DomUtil.addClass(i, "active"), L.DomUtil.addClass(a, "active")), L.DomEvent.on(t, "click", function (o) { if (L.DomEvent.preventDefault(o), !L.DomUtil.hasClass(t, "active")) { for (let t = 0; t < s.length; t++) { let o = s[t]; L.DomUtil.hasClass(o, "active") && L.DomUtil.removeClass(o, "active") } L.DomUtil.addClass(t, "active"), e.forEach(function (o) { t.dataset.tabLink === o.dataset.tabContent ? L.DomUtil.addClass(o, "active") : L.DomUtil.removeClass(o, "active") }) } }, t) }.bind(this)), this._toggleButton(t) }, _toggleButton: function (t) { const o = this._panel.querySelector(".sidepanel-toggle-container"), s = o.querySelector(".sidepanel-toggle-button"); L.DomEvent.on(s, "click", function (o) { let s = !0, e = L.DomUtil.hasClass(this._panel, "opened"), i = L.DomUtil.hasClass(this._panel, "closed"); if (e || i ? !e && i ? (L.DomUtil.addClass(this._panel, "opened"), L.DomUtil.removeClass(this._panel, "closed")) : e && !i ? (s = !1, L.DomUtil.removeClass(this._panel, "opened"), L.DomUtil.addClass(this._panel, "closed")) : L.DomUtil.addClass(this._panel, "opened") : L.DomUtil.addClass(this._panel, "opened"), this.options.pushControls) { let o = t.getContainer().querySelector(".leaflet-control-container"); L.DomUtil.addClass(o, "leaflet-anim-control-container"), s ? (L.DomUtil.removeClass(o, this.options.panelPosition + "-closed"), L.DomUtil.addClass(o, this.options.panelPosition + "-opened")) : (L.DomUtil.removeClass(o, this.options.panelPosition + "-opened"), L.DomUtil.addClass(o, this.options.panelPosition + "-closed")) } }.bind(this), o) } }), L.control.sidepanel = function (t, o) { return new L.Control.SidePanel(t, o) };

const panelRight = L.control.sidepanel('panelID', {
    panelPosition: 'left',
    hasTabs: true,
    tabsPosition: 'top',
    pushControls: true,
    darkMode: true,
    startTab: 'tab-1' //class of starting tab
}).addTo(map);

// create a variable to hold the geojson layer
var selected_geojson;
var selected_area;


// JavaScript to display the modal and beachballs when the page loads
$(document).ready(function () {
    $('#questionModal').modal('show');
    // Initialize the magnitude slider
    $(".magnitude_slider").ionRangeSlider({
        type: "double",
        grid_margin: false,
        hide_min_max: true,
        extra_classes: "color: 'blue'",
        min: 0,
        max: 10,
        step: 0.1,
        from: 0, // Initial left value
        to: 10,  // Initial right value
    });

    // Initialize the depth slider
    $(".depth_slider").ionRangeSlider({
        type: "double",
        grid_margin: false,
        min: 0,
        max: 200,
        from: 0, // Initial left value
        to: 200,  // Initial right value
    });

    // Initialize the rake slider
    $(".rake_slider").ionRangeSlider({
        type: "double",
        grid_margin: false,
        min: -200,
        max: 200,
        from: -200, // Initial left value
        to: 200,  // Initial right value
    });
});

// create a layer of all events
var allevents_markers = L.layerGroup();
// create a layer of filtered events
filter_markers = L.layerGroup();


// to show all events (from filter tab button and for beggining of page)
function showallevents() {
    if (map.hasLayer(filter_markers)) {
        filter_markers.eachLayer(function (layer) {
            filter_markers.removeLayer(layer)
        })
    }
    if (!map.hasLayer(allevents_markers)) {
        allevents_markers.addTo(map);
    }
}

// When we want to select a geojson with polygons
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

    // show beachballs of all events
    $.ajax({
        url: "http://localhost:8000/allevents",
        dataType: "json",
        
        success: function (result) {
            var data = result;
            console.log(data)
            // initiate icon library


            // Loop through the data.elements array
            if (data.length > 0) {

                for (let i in data) {
                    var Icon = new L.Icon({
                        // iconAnchor: new L.Point(16, 16),
                        iconUrl: "./static/beachballs/beachball_" + data[i].id + ".png",
                        iconSize: [data[i].Mw * 10, data[i].Mw * 10]
                    });

                    // Create the div element and the marker object
                    var div = document.createElement('div');
                    div.setAttribute("id", data[i].id);
                    // Get the marker position
                    div.innerHTML = `<table class="table" width="250">` +
                        `<tbody>` +
                        `<tr>` +
                        `<th><h3>Moment Tensor Solution</h3></th>` +
                        `<th><img src="./static/beachballs/beachball_${data[i].id}.png" height="100" width="100"/></th>` +
                        `</tr>` +
                        `<tr>` +
                        `<td>Event ID </td>` +
                        `<td>${data[i].id}</td>` +
                        `</tr>` +
                        `<tr>` +
                        `<td>Quality </td>` +
                        `<td>${data[i].quality}</td>` +
                        `</tr>` +
                        `<tr>` +
                        `<td>C.Time[GMT] </td>` +
                        `<td>${data[i].time}</td>` +
                        `</tr>` +
                        `<tr>` +
                        `<td>C.Magnitude[Mw] </td>` +
                        `<td>${data[i].Mw}</td>` +
                        `</tr>` +
                        `<tr>` +
                        `<td>H.Magnitude[MLh] </td>` +
                        `<td>${data[i].MLh}</td>` +
                        `</tr>` +
                        `<tr>` +
                        `<td>C.Latitude[°N] </td>` +
                        `<td>${data[i].latitude}</td>` +
                        `</tr>` +
                        `<tr>` +
                        `<td>C.Longitude[°E] </td>` +
                        `<td>${data[i].longitude}</td>` +
                        `</tr>` +
                        `<tr>` +
                        `<td>C.Depth[Km] </td>` +
                        `<td>${data[i].depth}</td>` +
                        `</tr>` +
                        `<tr>` +
                        `<td>Strike Dip Rake </td>` +
                        `<td>${data[i].strike} ${data[i].dip} ${data[i].rake} </td>` +
                        `</tr>` +
                        `</tbody>` +
                        `</table>`
                    ;

                    // create marker for the event
                    var marker = L.marker([data[i].latitude, data[i].longitude], {
                        icon: Icon,
                        name: data[i].id,
                        title: data[i].id
                    })
                        .bindPopup(div);
                    if (data[i].id.split(":")[0] == "smi") {
                        continue
                    } else {
                        allevents_markers.addLayer(marker);
                    }
                }

                // to show all events 
                showallevents()

            } else {
                throw error
            }



        },
        error: function (error) {
            console.error("Error:", error);
        }
    })

    // sent the selected area in the back, to manage events per area, and update the database
    $.ajax({
        type: "POST",
        url: "/geojson_selected",
        data: { "file": selectedAreaFile },
        dataType: 'json',

        success: function (result) {
            console.log("Success:", result);
        },
        error: function (error) {
            // print(data)
            console.error("Error:", error);
        }
    })

    // Load the selected GeoJSON data and create the layer
    $.getJSON("/static/data/" + $("#selectedArea_file").val(), function (data) {
        // Create the GeoJSON layer with custom popup content
        // for street view of map
        console.log($("#selectedArea_file").val())
        // when an area gets selected
        selected_geojson = L.geoJson(data, {
            onEachFeature: function (feature, featureLayer) {

                // to fetch and show in sidepanel the selected area's events only 
                async function eventsperarea(areacode) {
                    const response = await fetch('/' + areacode);
                    const json = await response.json();
                    console.log(json);
                    return json;
                }

                var areaheader = document.getElementById("areaheader");
                var arealist = document.getElementById("arealist");

                // to create the content of the selected areas sidepanel
                featureLayer.on('click', function () {
                    console.log(feature.properties.code);
                    document.getElementById("averageMT").innerHTML = "";

                    eventsperarea(feature.properties.code)
                        .then(response => {
                            console.log("yay");
                            // Create the content for the sidepanel
                            areaheader = '<h2>' + feature.properties.id + '. ' + feature.properties.name + '</h2><br>';
                            areaheader += '<h6>Area code: ' + feature.properties.code + '</h6><hr>';

                            if (response.length > 0) {
                                response.forEach((event, index) => {
                                    arealist += '<tr id="' + String(event.id) + '">' +
                                        '<td><input class="filter-checkbox form-check-input" type="checkbox" value="' + String(event.mtlist) + '" id="' + String(event.id) + '" name="moment-tensors" checked/></td>' +
                                        '<td>' + String(event.time) + '</td>' +
                                        '<td>' + String(event.Mw) + '</td>' +
                                        '<td>' + String(event.depth) + '</td>' +
                                        '<td>' + String(event.rake) + '</td>' +
                                        '<td>' + String(event.quality) + '</td>' +
                                        '<td><img src="static/beachballs/beachball_' + String(event.id) + '.png" height="30" width="30"/></td>' +
                                        '</tr>';
                                });
                            } else {
                                arealist += '<li style="list-style-type: None;"> No seismic events found in this area. </li>';
                            }


                            var tableRows = document.querySelectorAll('#arealist tr');

                            tableRows.forEach(function (row, index) {
                                var lastDataCell = row.querySelector('td:last-child');
                                lastDataCell.addEventListener('click', function () {
                                    var checkboxId = row.attr('id');
                                    // Find the marker with the same ID as the checkbox
                                    var marker = allevents_markers.getLayers().find(function (layer) {
                                        return layer.options.name === checkboxId;
                                    });
                                    // Get the associated marker based on the row's data
                                    
                                    // Get the marker's coordinates
                                    var markerLatlng = marker.getLatLng();
                                    console.log(markerLatlng)

                                    // Center the map view on the marker's coordinates
                                    map.setView(markerLatlng, 6);

                                    // Open the marker's popup
                                    marker.openPopup();
                                });
                            });

                            this.setStyle({
                                'fillColor': '#0000ff'
                            });
                            featureLayer.bindTooltip(feature.properties.code, { permanent: false, direction: "center", className: "my-labels" });

                            $('#areaheader').html(areaheader);
                            $('#arealist').html(arealist);

                            // Open the side panel
                            $("#panelID").addClass("opened");


                        })
                        .catch(error => {
                            console.log("error!");
                            console.error(error);
                        });
                });

                // to create some mouseover effect when cursor goes over an area
                featureLayer.on('mouseover', function () {
                    this.setStyle({
                        'fillColor': '#0000ff'
                    });
                    featureLayer.bindTooltip(feature.properties.code, { permanent: false, direction: "center", className: "my-labels" });

                });

                // to return to the initial effect
                featureLayer.on('mouseout', function () {
                    this.setStyle({
                        'fillColor': '#3388ff'
                    });
                });
            }
        });

        // Add the layer of polygons to the map
        map.addLayer(selected_geojson);
        map.fitBounds(selected_geojson.getBounds());

        // to show a control panel with the available options of the selected area and the drawing 
        var files_control = {
            "draw": drawnItems,
            "areas": selected_geojson,
        };

        // add map views and scale details to controlers
        L.control.layers(files_control).addTo(map);

    });

}

// remove filtered layer when clear is clicked
$(document).on('reset', '#filter', function (e) {
    e.preventDefault();
    if (map.hasLayer(filter_markers)) {
        // Find the marker with the same ID as the checkbox
        filter_markers.eachLayer(function (layer) {
            filter_markers.removeLayer(layer)
        })
        var filter_values = document.getElementById("filterlist")
        filter_values.innerHTML = "";
        var avMT_values = document.getElementById("averageMT")
        avMT_values.innerHTML = "";
    }
    $(".magnitude_slider").data("ionRangeSlider").reset();
    $(".depth_slider").data("ionRangeSlider").reset();
    $(".rake_slider").data("ionRangeSlider").reset();

})

// if filter has been applied
$(document).on('submit', '#filter', function (e) {
    e.preventDefault();
    $.ajax({
        type: 'POST',
        url: "http://localhost:8000/filter_events",
        data: {
            starttime: $("#starttime").val(),
            endtime: $("#endtime").val(),
            magnitude: $("#magnitude").val(),
            depth: $("#depth").val(),
            rake: $("#rake").val()
        },

        success: function (result) {
            var data = result;
            console.log("result ok ")
            // get the div for errors
            filter_errors_div = document.getElementById("filter_errors")
            // to hide the filtered list div
            var wrap = document.getElementById("filter-wrap");

            // get div to insert list of element of sidepanel
            var side = document.getElementById("filterlist");

            // Loop through the data.elements array
            if (data.length > 0) {
                // remove all events layer if exists
                if (map.hasLayer(allevents_markers)) {
                    map.removeLayer(allevents_markers)
                }

                if (wrap.hasAttribute("hidden")) {
                    wrap.removeAttribute("hidden");
                    filter_errors_div.innerHTML = ""

                }

                for (let i in data) {
                    // to not allow duplicate markers
                    if (document.querySelector('[title="' + data[i].id + '"]')) {
                        continue
                    } else {
                        // icon for each marker
                        var Icon = new L.Icon({
                            // iconAnchor: new L.Point(16, 16),
                            iconUrl: "./static/beachballs/beachball_" + data[i].id + ".png",
                            iconSize: [data[i].Mw * 10, data[i].Mw * 10]

                        });

                        // Create the div element for the popup of the markers and the marker object
                        var div = document.createElement('div');
                        div.setAttribute("id", data[i].id);

                        // Get the marker position
                        div.innerHTML = `<table class="table" width="250">` +
                            `<tbody>` +
                            `<tr>` +
                            `<th><h3>Moment Tensor Solution</h3></th>` +
                            `<th><img src="./static/beachballs/beachball_${data[i].id}.png" height="100" width="100"/></th>` +
                            `</tr>` +
                            `<tr>` +
                            `<td>Event ID </td>` +
                            `<td>${data[i].id}</td>` +
                            `</tr>` +
                            `<tr>` +
                            `<td>Quality </td>` +
                            `<td>${data[i].quality}</td>` +
                            `</tr>` +
                            `<tr>` +
                            `<td>C.Time[GMT] </td>` +
                            `<td>${data[i].time}</td>` +
                            `</tr>` +
                            `<tr>` +
                            `<td>C.Magnitude[Mw] </td>` +
                            `<td>${data[i].Mw}</td>` +
                            `</tr>` +
                            `<tr>` +
                            `<td>H.Magnitude[MLh] </td>` +
                            `<td>${data[i].MLh}</td>` +
                            `</tr>` +
                            `<tr>` +
                            `<td>C.Latitude[°N] </td>` +
                            `<td>${data[i].latitude}</td>` +
                            `</tr>` +
                            `<tr>` +
                            `<td>C.Longitude[°E] </td>` +
                            `<td>${data[i].longitude}</td>` +
                            `</tr>` +
                            `<tr>` +
                            `<td>C.Depth[Km] </td>` +
                            `<td>${data[i].depth}</td>` +
                            `</tr>` +
                            `<tr>` +
                            `<td>Strike Dip Rake </td>` +
                            `<td>${data[i].strike} ${data[i].dip} ${data[i].rake} </td>` +
                            `</tr>` +
                            `</tbody>` +
                            `</table>`
                            ;

                        // create the marker leaflet object
                        var marker = L.marker([data[i].latitude, data[i].longitude], {
                            icon: Icon,
                            name: data[i].id,
                            title: data[i].id
                        })
                            .bindPopup(div);
                        // add marker to layer group of all filtered markers
                        filter_markers.addLayer(marker)

                        // create the sidepanel content
                        side = '<tr id="' + String(data[i].id) + '">' +
                            '<td><input class="filter-checkbox form-check-input" type="checkbox" value="' + String(data[i].mtlist) + '" id="' + String(data[i].id) + '" name="moment-tensors" checked/></td>' +
                            '<td>' + String(data[i].time) + '</td>' +
                            '<td>' + String(data[i].Mw) + '</td>' +
                            '<td>' + String(data[i].depth) + '</td>' +
                            '<td>' + String(data[i].rake) + '</td>' +
                            '<td>' + String(data[i].quality) + '</td>' +
                            '<td><img src="./static/beachballs/beachball_' + String(data[i].id) + '.png" height="30" width="30"/></td>' +
                            '</tr>';

                    }
                    $('#filterlist').append(side);



                    var tableRows = document.querySelectorAll('#filterlist tr');

                    tableRows.forEach(function (row, index) {
                        var lastDataCell = row.querySelector('td:last-child');
                        lastDataCell.addEventListener('click', function () {
                            var checkboxId = row.getAttribute('id');
                            // Find the marker with the same ID as the checkbox
                            var marker = filter_markers.getLayers().find(function (layer) {
                                return layer.options.name === checkboxId;
                            });
                            // // Get the associated marker based on the row's data
                            // var associatedMarker = markers[index].marker;

                            // Get the marker's coordinates
                            var markerLatlng = marker.getLatLng();
                            console.log(markerLatlng)

                            // Center the map view on the marker's coordinates
                            map.setView(markerLatlng, 6);

                            // Open the marker's popup
                            marker.openPopup();
                        });
                    });
                }

                // Change 'tab-1' to the appropriate tab ID
                // $('#filterlist').append(side);
                // Open the side panel
                $("#panelID").addClass("opened");

                filter_markers.addTo(map)





            } else {
                console.log("no events found")
                // if(wrap.hasAttribute(hidden)){
                filter_errors_div.classList.add("btn-outline-warning")
                filter_errors_div.innerHTML += `<hr/><h3>no events found</h3>`
                wrap.setAttribute("hidden", "hidden")
                // }
            }

        },
        error: function (error) {
            console.error("Error:", error);
        }
    })
})


// Add an event listener for checkbox change events
$(document).on('change', '.filter-checkbox', function () {
    var checkboxId = $(this).attr('id');
    var isChecked = $(this).is(':checked');

    // Find the marker with the same ID as the checkbox
    var marker = filter_markers.getLayers().find(function (layer) {
        return layer.options.title === checkboxId;
    });

    if (marker) {
        if (isChecked) {
            // Add the marker back to the map
            map.addLayer(marker);
        } else {
            // Remove the marker from the map
            map.removeLayer(marker);
        }
    }
});



// send data to backend to calculate the average MT
// if filter has been applied
$(document).on('submit', '#filterlistform', function (e) {
    var avMT = document.getElementById("modal_MT_body");
    avMT.innerHTML = "Waiting for calculation...";
    e.preventDefault();
    // to open the modal to show the results    
    $('#basicModal').modal('show');
    document.getElementById("averageMT").innerHTML = "";
    var inputs = document.getElementsByName("moment-tensors");

    // data = {}
    // data = []
    ids = []
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].checked) {
            var values = inputs[i].value;
            list = values.split("/")
            // data.push(list)
            ids.push(inputs[i].id)
        }
    }

    console.log(ids)
    filter = {
        starttime: $("#starttime").val(),
        endtime: $("#endtime").val(),
        magnitude: $("#magnitude").val(),
        depth: $("#depth").val(),
        rake: $("#rake").val()
    }

    $.ajax({
        type: 'POST',
        url: "http://localhost:8000/averageMT",
        contentType: "application/json",
        // data: JSON.stringify({"data": data}),
        data: JSON.stringify({ "data": ids, "filter": filter }),

        success: function (result) {
            console.log(result)
            // var avMT = document.getElementById("modal_MT_body")
            avMT.innerHTML = '<div class="row"><div class="col-md-6"><a href="static/Figures/P_T_axes.png"><img style="width:100%" src="static/Figures/P_T_axes.png?' + (new Date()).getTime() + '" target="_blank"></a></div>' +
                '<div class="col-md-6"><a href="static/Figures/Mohr_circles.png" target="_blank"><img style="width:100%" src="static/Figures/Mohr_circles.png?' + (new Date()).getTime() + '"></a></div></div>' +
                '<div class="row"><div class="col-md-6"><a href="static/Figures/shape_ratio.png" target="_blank"><img style="width:100%" src="static/Figures/shape_ratio.png?' + (new Date()).getTime() + '"></a></div>' +
                '<div class="col-md-6"><a href="static/Figures/stress_directions.png" target="_blank"><img style="width:100%" src="static/Figures/stress_directions.png?' + (new Date()).getTime() + '"></a></div></div>' +
                '<div class="row"><div class="col-md-6"><a href="static/Figures/red.png" target="_blank"><img style="width:100%" src="static/Figures/red.png?' + (new Date()).getTime() + '"></a></div>' +
                '<div class="col-md-6"><a href="static/Figures/blue.png" target="_blank"><img style="width:100%" src="static/Figures/blue.png?' + (new Date()).getTime() + '"></a></div></div>'
        },
        error: function (error) {
            console.error("Error:", error);
        }
    })
})


// calculate the inversion of (drawn) area
$(document).on('submit', '#arealistform', function (e) {
    e.preventDefault();
    document.getElementById("areasaverageMT").innerHTML = "";

    var inputs = document.getElementsByName("moment-tensors");
    var areacode = document.getElementById("areaheader").getElementsByTagName('h6')[0];
    console.log(areacode)

    ids = []
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].checked) {
            var values = inputs[i].value;
            list = values.split("/")
            // data.push(list)
            ids.push(inputs[i].id)
        }
    }

    console.log(ids)

    // to calculate the average MT
    $.ajax({
        type: 'POST',
        url: "http://localhost:8000/averageMT",
        contentType: "application/json",
        data: JSON.stringify({ "data": ids, "code": String(areacode) }),
        
        success: function (result) {
            console.log(result)
            var avMT = document.getElementById("areasaverageMT")
            avMT.innerHTML += '<a href="static/Figures/P_T_axes.png"><img style="width:100%" src="static/Figures/P_T_axes.png?' + (new Date()).getTime() + '" target="_blank"></a>' +
                '<a href="static/Figures/Mohr_circles.png" target="_blank"><img style="width:100%" src="static/Figures/Mohr_circles.png?' + (new Date()).getTime() + '"></a>' +
                '<a href="static/Figures/shape_ratio.png" target="_blank"><img style="width:100%" src="static/Figures/shape_ratio.png?' + (new Date()).getTime() + '"></a>' +
                '<a href="static/Figures/stress_directions.png" target="_blank"><img style="width:100%" src="static/Figures/stress_directions.png?' + (new Date()).getTime() + '"></a>' +
                '<a href="static/Figures/red.png" target="_blank"><img style="width:100%" src="static/Figures/red.png?' + (new Date()).getTime() + '"></a>' +
                '<a href="static/Figures/blue.png" target="_blank"><img style="width:100%" src="static/Figures/blue.png?' + (new Date()).getTime() + '"></a>'


        },
        error: function (error) {
            console.error("Error:", error);
        }
    })
})

// export button for stress inversion
function Export() {
    // let table = document.getElementById("dtBasicExample");

    const rows = document.querySelectorAll("#dtBasicExample tbody tr");
    // const dataToExport = [];

    rows.forEach((row) => {
        const checkbox = row.querySelector("input[type='checkbox']");
        if (!checkbox.checked) {
            row.classList.add("no-export");
        }
    })

    $('#dtBasicExample').table2excel({
        exclude: ".no-export",
        filename: "stressinversionMT.xls",
        fileext: ".xls",
        exclude_links: false,
        exclude_img: false,
        name: "Moment Tensors",
        exclude_inputs: true
    });


    // Prepare the image URLs (replace with your actual image URLs)
    const imageUrls = [
        "http://localhost:8000/static/Figures/P_T_axes.png",
        "http://localhost:8000/static/Figures/Mohr_circles.png",
        "http://localhost:8000/static/Figures/stress_directions.png",
        "http://localhost:8000/static/Figures/shape_ratio.png",
        "http://localhost:8000/static/Figures/red.png",
        "http://localhost:8000/static/Figures/blue.png",
    ];


    // Create a new instance of JSZip
    const zip = new JSZip();

    // Fetch and add each image as a separate file in the ZIP archive
    const imagePromises = imageUrls.map((imageUrl, index) =>
        fetch(imageUrl)
            .then((response) => response.blob())
            .then((imageBlob) => {
                zip.file(`image${index + 1}.png`, imageBlob);
            })
    );

    // Wait for all image fetch operations to complete
    Promise.all(imagePromises)
        .then(() => {
            // Generate the ZIP archive and trigger the download
            zip.generateAsync({ type: "blob" }).then((zipBlob) => {
                // Create a download link for the ZIP file
                const downloadLink = document.createElement("a");
                downloadLink.href = URL.createObjectURL(zipBlob);
                downloadLink.download = "ExportedData.zip";

                // Trigger the download link
                downloadLink.click();
            });
        })
        .catch((error) => {
            console.error("Error fetching or processing images:", error);
        });
}

// the group of points added to the map
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

var drawControl = new L.Control.Draw({
    position: 'topright',
    draw: {
        polyline: false,
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
        rect: {
            shapeOptions: {
                color: 'green'
            },
        },
        circle: false,
        marker: false,
        circlemarker: false
    },
    edit: {
        featureGroup: drawnItems,
        remove: true
    }

});

map.addControl(drawControl);

// // When we want to draw a specific area
map.on('draw:created', function (e) {
    var layer = e.layer;
    console.log(layer)
    document.getElementById("arealist").innerHTML = "";
    document.getElementById("areasaverageMT").innerHTML = "";
    drawnItems.addLayer(layer);
    handleShape(layer);
});

// // When we want to draw a specific area
map.on('draw:edited', function (e) {
    var layers = e.layers;
    console.log(layers.toGeoJSON())
    layers.eachLayer(function (layer) {
        handleShape(layer);
    })
});

map.on('draw:deleted', function (e) {
    var layers = e.layers;
    layers.eachLayer(function (layer) {
        document.getElementById("arealist").innerHTML = "";
        document.getElementById("areasaverageMT").innerHTML = "";
    })
})

// Function to handle the logic for drawing and clicking
function handleShape(layer) {
    var json_shape = JSON.stringify(layer.toGeoJSON());

    // Create a new layer from the drawn GeoJSON shape for displaying coordinates
    var drawnShape = L.geoJSON(JSON.parse(json_shape), {
        style: {
            color: 'red', // Customize the color of the drawn shape
        },
        onEachFeature: function (feature, featureLayer) {
            if (feature.geometry.type === 'Polygon') {


                // Collect feature geometry to send to the backend for database query
                data_2sent = JSON.stringify(feature.geometry);
                console.log(data_2sent);
                $.ajax({
                    type: "POST",
                    url: "drawnshape",
                    contentType: "application/json",
                    data: data_2sent,

                    success: function (result) {
                        console.log("Success:", result);

                        // Popup the coordinates of the drawn shape
                        var popupContent = '<ul>';
                        for (var i = 0; i < feature.geometry.coordinates[0].length; i++) {
                            var coordinate = feature.geometry.coordinates[0][i];
                            var coordinate_prev = feature.geometry.coordinates[0][i - 1];
                            if (i == 0 || coordinate[1] !== coordinate_prev[1] || coordinate[0] !== coordinate_prev[0]) {
                                popupContent += '<li>Lat: ' + coordinate[1] + ', Lon: ' + coordinate[0] + '</li>';
                            }
                        }
                        popupContent += '</ul>';
                        featureLayer.bindPopup(popupContent);

                        console.log("yay---2");

                        // Create the content for the side panel
                        var popup = '<div class="popup">';

                        document.getElementById("arealistform").removeAttribute("hidden");
                        document.querySelector("#area-wrap h5").innerHTML = "Drawn Area\'s Events:"
                        // Add the seismic events list
                        if (result.length > 0) {

                            result.forEach((event, index) => {
                                popup += '<tr id="' + String(event.id) + '">' +
                                    '<td><input class="filter-checkbox form-check-input" type="checkbox" value="' + String(event.mtlist) + '" id="' + String(event.id) + '" name="moment-tensors" checked/></td>' +
                                    '<td>' + String(event.time) + '</td>' +
                                    '<td>' + String(event.Mw) + '</td>' +
                                    '<td>' + String(event.depth) + '</td>' +
                                    '<td>' + String(event.rake) + '</td>' +
                                    '<td>' + String(event.quality) + '</td>' +
                                    '<td><img src="static/beachballs/beachball_' + String(event.id) + '.png" height="30" width="30"/></td>' +
                                    '</tr>';
                            });
                        } else {
                            document.querySelector("#area-wrap h5").innerHTML += '<p style="list-style-type: None;"> No seismic events found in this area. </p>';
                            document.getElementById("arealistform").setAttribute("hidden", "hidden");
                        }
                        $('#arealist').html(popup);
                        // Open the side panel
                        $("#panelID").addClass("opened");



                        var tableRows = document.querySelectorAll('#arealist tr');

                        tableRows.forEach(function (row, index) {
                            var lastDataCell = row.querySelector('td:last-child');

                            lastDataCell.addEventListener('click', function () {
                                var checkboxId = row.attr('id');
                                // Find the marker with the same ID as the checkbox
                                var marker = allevents_markers.getLayers().find(function (layer) {
                                    return layer.options.name === checkboxId;
                                });

                                // Get the marker's coordinates
                                var markerLatlng = marker.getLatLng();
                                console.log(markerLatlng)

                                // Center the map view on the marker's coordinates
                                map.setView(markerLatlng, 6);

                                // Open the marker's popup
                                marker.openPopup();
                            });
                        });
                    },
                    error: function (error) {
                        console.error("Error:", error);
                    }
                })

            }
        },
    });
}

// Function to open the side panel with content
function openSidePanel(content) {
    // Change 'tab-1' to the appropriate tab ID
    $('#tab-1').html(content);
    // Open the side panel
    $("#panelID").addClass("opened");
}