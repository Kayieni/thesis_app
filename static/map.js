
$(function() {
    $('.slider').on('input change', function(){
        $(this).next($('.slider_label')).html(this.value);
    });
    $('.slider_label').each(function(){
        var value = $(this).prev().attr('value');
        $(this).html(value);
    });              
})

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
// document.addEventListener('click', function(event) {
//     var panel = document.getElementById('panelID');
//     var tabContent = document.getElementById('tab-1');

//     if (!panel.contains(event.target)) {
//         panel.classList.remove('opened');
//         tabContent.innerHTML = '<h4><em>Select an area to view the details</em></h4>'; // Clear the contents of tab-1
//     }
// });

// create a variable to hold the geojson layer
var selected_geojson;
var selected_area;


// JavaScript to display the modal and beachballs when the page loads
$(document).ready(function () {
    $('#questionModal').modal('show');
    /*  
    // get events of db when page is loaded
    $.ajax({
        // type: "GET",
        url: "http://localhost:8000/allevents",
        dataType: "json",
        // data: data,

        success: function (result) {
            var data = result;
            console.log(data)
            // initiate icon library
            
            
            // Loop through the data.elements array
            if(data.length > 0) {
                // for(i=0;i<data.length;i++) {
                for(let i in data) {
                    var Icon = new L.Icon({
                            // iconAnchor: new L.Point(16, 16),
                            iconUrl: "./static/beachballs/beachball_" + data[i].id + ".png",
                            // iconSize: [20,20],
        
                    });

                    // Create the div element and the marker object
                    var div = document.createElement('div');
                    div.setAttribute("id", data[i].id );
                    // Get the marker position
                    div.innerHTML = `<h1>Moment Tensor Solution</h1>.` + 
                        `<img src="./static/beachballs/beachball_${data[i].id}.png"/>` +
                        `<p>${data[i].id}</p>` +
                        `<p>${data[i].time}</p>`;

                    var marker = L.marker([data[i].latitude, data[i].longitude], {
                        icon: Icon,
                        name: data[i].id,
                        title: data[i].id
                    })
                    .bindPopup(div);
                    if(data[i].id.split(":")[0]=="smi"){
                        continue
                    }else{
                        marker.addTo(map)
                    }



                }
            }else {
                throw error
            }

        },
        error: function(error) {
            console.error("Error:", error);
        }
    })
    */
});

// create a layer of all events
var allevents_markers = L.layerGroup();
// create a layer of filtered events
filter_markers =  L.layerGroup();


// to show all events (from filter tab button and for beggining of page)
function showallevents() {
    if(map.hasLayer(filter_markers)) {
        map.removeLayer(filter_markers)
    }
    if(!map.hasLayer(allevents_markers)){
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
        // type: "GET",
        url: "http://localhost:8000/allevents",
        dataType: "json",
        // data: data,

        success: function (result) {
            var data = result;
            console.log(data)
            // initiate icon library
            
            
            // Loop through the data.elements array
            if(data.length > 0) {

                for(let i in data) {
                    var Icon = new L.Icon({
                            // iconAnchor: new L.Point(16, 16),
                            iconUrl: "./static/beachballs/beachball_" + data[i].id + ".png",
                            // iconSize: [20,20],
        
                    });

                    // Create the div element and the marker object
                    var div = document.createElement('div');
                    div.setAttribute("id", data[i].id );
                    // Get the marker position
                    div.innerHTML = `<h1>Moment Tensor Solution</h1>.` + 
                        `<img src="./static/beachballs/beachball_${data[i].id}.png"/>` +
                        `<p>${data[i].id}</p>` +
                        `<p>${data[i].time}</p>`;

                    var marker = L.marker([data[i].latitude, data[i].longitude], {
                        icon: Icon,
                        name: data[i].id,
                        title: data[i].id
                    })
                    .bindPopup(div);
                    if(data[i].id.split(":")[0]=="smi"){
                        continue
                    }else{
                        allevents_markers.addLayer(marker);
                        // marker.addTo(map)
                    }
                }

                // to show all events 
                showallevents()

                // to add an overlay (checkbox) for all events
                // var overlay = {'all events': allevents_markers};
                // L.control.layers(null, overlay).addTo(map);
            
            }else {
                throw error
            }



        },
        error: function(error) {
            console.error("Error:", error);
        }
    })
    
    // sent the selected area in the back, to manage events per area, and update the database
    $.ajax ({
        type: "POST",
        url: "/geojson_selected",
        data: {"file":selectedAreaFile},
        dataType: 'json',

        success: function (result) {
            console.log("Success:", result);
        },
        error: function(error) {
            // print(data)
            console.error("Error:", error);
        }
    })

    // Load the selected GeoJSON data and create the layer
    $.getJSON("/static/data/" + $("#selectedArea_file").val(), function (data) {
        // Create the GeoJSON layer with custom popup content
        // for street view of map

        // when an area gets selected
        selected_geojson = L.geoJson(data, {
            onEachFeature: function (feature, featureLayer) {

                // to fetch and show in sidepanel the selected area's events only 
                async function eventsperarea(areacode) {
                    const response = await fetch('/' + areacode);
                    // + new URLSearchParams({ postId: 1 }).toString());
                    const json = await response.json();
                    console.log(json);
                    return json;
                }

                var areaheader = document.getElementById("areaheader");
                var arealist = document.getElementById("arealist");

                // to create the content of the selected areas sidepanel
                featureLayer.on('click', function () {
                    console.log(feature.properties.code);

                    eventsperarea(feature.properties.code)
                        .then(response => {
                            console.log("yay");
                            // Create the content for the sidepanel
                            areaheader = '<h2>'+feature.properties.id + '. ' + feature.properties.name+'</h2><br>';
                            areaheader += '<h6>Area code: '+feature.properties.code+'</h6><hr>';
                            // areaheader.innerHTML = feature.properties.code;
                            var popup = '<div class="popup">';
                            // popup += '<h4>' + feature.properties.id + ". " + feature.properties.name + '</h4>';
                            // popup += '<h5>Code: ' + feature.properties.code + '</h4>';
                            // popup += '<p>Coordinates:</p>';
                            // popup += '<ul>';
                            // for (var i = 0; i < feature.geometry.coordinates[0].length - 1; i++) {
                            //     var coordinate = feature.geometry.coordinates[0][i];
                            //     popup += '<li>Lat: ' + coordinate[1] + ', Lon: ' + coordinate[0] + '</li>';
                            // }
                            // popup += '</ul>';
                            // Add the seismic events list
                            // popup += '<h5>Seismic Events:</h5>';
                            // popup += '<ol id="eventlist">';
                            if (response.length>0) {
                                response.forEach((event, index) => {
                                    // const eventNumber = index + 1;
                                    // arealist += '<li><a href="#"> Event ID: ' + String(event.id) + " | Strike: " + String(event.strike) + " | Dip: "  + String(event.dip) + " | Rake: "  + String(event.rake) + '<img src="./static/beachballs/beachball_'+ String(event.id) + '.png"/></a></li>';
                                    arealist += '<div><input type="checkbox" value="' + String(event.mtlist) + '" id="'+ String(event.id) + '" name="moment-tensors" checked/><label for="'+ String(event.id) + '"><a href="#"> Event ID: ' + String(event.id) + " <br/> Time: " + String(event.time) + " <br/> Mw: "  + String(event.Mw) + " <br/> D(km): "  + String(event.depth) + " <br/> Rake: "  + String(event.rake) + '<img src="./static/beachballs/beachball_'+ String(event.id) +'.png"/><br/></a></label></div>';
                                });
                            } else {
                                arealist += '<li style="list-style-type: None;"> No seismic events found in this area. </li>';
                            }
                            // popup += '</ol>';
                            // popup += '</div>';

                            this.setStyle({
                                'fillColor': '#0000ff'
                            });
                            featureLayer.bindTooltip(feature.properties.code, { permanent: false, direction: "center", className: "my-labels" });


                            // Change 'tab-1' to the appropriate tab ID
                            // $('#tab-1').html(popup);
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
$(document).on('reset','#filter',function(e) {
    e.preventDefault();
    if(map.hasLayer(filter_markers)) {
        map.removeLayer(filter_markers)
        var wrap = document.getElementById("filter-wrap");
        wrap.setAttribute("hidden","hidden");
        var mt = document.getElementById("averageMT");
        mt.setAttribute("hidden","hidden");
    }

})

// if filter has been applied
$(document).on('submit','#filter',function(e) {
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
            if(data.length > 0) {
                // remove all events layer if exists
                if(map.hasLayer(allevents_markers)) {
                    map.removeLayer(allevents_markers)
                }

                if(wrap.hasAttribute("hidden")){
                    wrap.removeAttribute("hidden");
                }

                for(let i in data) {
                    // to not allow duplicate markers
                    if(document.querySelector('[title="'+ data[i].id +'"]')){
                        continue
                    }else{
                        // icon for each marker
                        var Icon = new L.Icon({
                                // iconAnchor: new L.Point(16, 16),
                                iconUrl: "./static/beachballs/beachball_" + data[i].id + ".png",
                                // iconSize: [20,20],
            
                        });
                    
                        // Create the div element for the popup of the markers and the marker object
                        var div = document.createElement('div');
                        div.setAttribute("id", data[i].id );

                        // Get the marker position
                        div.innerHTML = `<h1>Moment Tensor Solution</h1>.` + 
                            `<img src="./static/beachballs/beachball_${data[i].id}.png"/>` +
                            `<p>${data[i].id}</p>` +
                            `<p>${data[i].time}</p>`;

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
                        // var side = document.getElementById("filterlist");
                        side = '<div><input type="checkbox" value="'+ String(data[i].mtlist) + '" id="'+ String(data[i].id) + '" name="moment-tensors" checked/><label for="'+ String(data[i].id) + '"><a href="#"> Event ID: ' + String(data[i].id) + " <br/> Time: " + String(data[i].time) + " <br/> Mw: "  + String(data[i].Mw) + " <br/> D(km): "  + String(data[i].depth) + " <br/> Rake: "  + String(data[i].rake) + '<img src="./static/beachballs/beachball_'+ String(data[i].id) +'.png"/><br/></a></label></div>';
                        
                    }
                    $('#filterlist').append(side);
                }
            
                // Change 'tab-1' to the appropriate tab ID
                // $('#filterlist').append(side);
                // Open the side panel
                $("#panelID").addClass("opened");

                filter_markers.addTo(map)





            }else {
                console.log("no events found")
                if(wrap.getAttribute(hidden)){
                    filter_errors_div.classList.add("btn-outline-warning")
                    filter_errors_div.innerHTML+=`<hr/><h3>no events found</h3>`
                }
            }

        },
        error: function(error) {
            console.error("Error:", error);
        }
    })
})

// send data to backend to calculate the average MT
// if filter has been applied
$(document).on('submit','#filterlistform',function(e) {
    e.preventDefault();

    var inputs = document.getElementsByName("moment-tensors");

    // data = {}
    // data = []
    ids = []
    for(var i = 0; i < inputs.length; i++) {
        if(inputs[i].checked) {
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
        data: JSON.stringify({"data": ids, "filter": filter}),

        success: function (result) {
            console.log(result)
            console.log(String(result))
            var avMT = document.getElementById("averageMT")
            avMT.innerHTML='<a href="static/Figures/P_T_axes.png"><img style="width:100%" src="static/Figures/P_T_axes.png" target="_blank"></a>' + 
            '<a href="static/Figures/Mohr_circles.png" target="_blank"><img style="width:100%" src="static/Figures/Mohr_circles.png"></a>' +
            '<a href="static/Figures/shape_ratio.png" target="_blank"><img style="width:100%" src="static/Figures/shape_ratio.png"></a>' +
            '<a href="static/Figures/stress_directions.png" target="_blank"><img style="width:100%" src="static/Figures/stress_directions.png"></a>'+
            '<a href="static/Figures/red.png" target="_blank"><img style="width:100%" src="static/Figures/red.png"></a>'
            console.log(result)
        },
        error: function(error) {
            console.error("Error:", error);
        }
    })
})


// send data to backend to calculate the average MT
// if filter has been applied
$(document).on('submit','#arealistform',function(e) {
    e.preventDefault();

    var inputs = document.getElementsByName("moment-tensors");
    var areacode = document.getElementById( "areaheader" ).getElementsByTagName( 'h6' )[0];
    console.log(areacode)
    
    ids = []
    for(var i = 0; i < inputs.length; i++) {
        if(inputs[i].checked) {
            var values = inputs[i].value;
            list = values.split("/")
            // data.push(list)
            ids.push(inputs[i].id)
        }  
    }

    console.log(ids)
    // filter = {
    //     starttime: $("#starttime").val(),
    //     endtime: $("#endtime").val(),
    //     magnitude: $("#magnitude").val(),
    //     depth: $("#depth").val(),
    //     rake: $("#rake").val()
    // }

    $.ajax({
        type: 'POST',
        url: "http://localhost:8000/averageMT",
        contentType: "application/json",
        data: JSON.stringify({"data": ids, "code": String(areacode)}),
        // data: JSON.stringify({"data": ids, "filter": filter}),

        success: function (result) {
            console.log(result)
            console.log(String(result))
            var avMT = document.getElementById("areasaverageMT")
            avMT.innerHTML='<a href="static/Figures/P_T_axes.png"><img style="width:100%" src="static/Figures/P_T_axes.png" target="_blank"></a>' + 
            '<a href="static/Figures/Mohr_circles.png" target="_blank"><img style="width:100%" src="static/Figures/Mohr_circles.png"></a>' +
            '<a href="static/Figures/shape_ratio.png" target="_blank"><img style="width:100%" src="static/Figures/shape_ratio.png"></a>' +
            '<a href="static/Figures/stress_directions.png" target="_blank"><img style="width:100%" src="static/Figures/stress_directions.png"></a>'+
            '<a href="static/Figures/red.png" target="_blank"><img style="width:100%" src="static/Figures/red.png"></a>'
            console.log(result)
        },
        error: function(error) {
            console.error("Error:", error);
        }
    })
})



// The controler of drawing some areas
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

// When we want to draw a specific area
map.on('draw:created', function (e) {
    var layer = e.layer;
    console.log(layer.toGeoJSON())
    var json_shape = JSON.stringify(layer.toGeoJSON());

    // Create a new layer from the drawn GeoJSON shape for displaying coordinates
    drawnShape = L.geoJSON(JSON.parse(json_shape), {
        style: {
            color: 'red', // Customize the color of the drawn shape
        },
        onEachFeature: function (feature, featureLayer) {
            if (feature.geometry.type === 'Polygon') {
                // collect feature geometry to send in backend, to query the database of events included
                data_2sent = JSON.stringify(feature.geometry) 
                console.log(data_2sent)
                $.ajax({
                    type: "POST",
                    url: "drawnshape",
                    contentType: "application/json",
                    data: data_2sent,

                    success: function (result) {
                        console.log("Success:", result);

                        // popup the coordinates of the drawn shape
                        var popupContent = '<ul>';
                        for (var i = 0; i < feature.geometry.coordinates[0].length; i++) {
                            var coordinate = feature.geometry.coordinates[0][i];
                            var coordinate_prev = feature.geometry.coordinates[0][i-1];
                            if( i==0 || coordinate[1]!== coordinate_prev[1] || coordinate[0]!== coordinate_prev[0]) {
                                popupContent += '<li>Lat: ' + coordinate[1] + ', Lon: ' + coordinate[0] + '</li>';
                            }
                        }
                        popupContent += '</ul>';
                        featureLayer.bindPopup(popupContent);

                        console.log("yay---2");

                        // Create the content for the sidepanel
                        var popup = '<div class="popup">';
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
                                popup += '<li><a href="#"> Event ID: ' + String(event.id) + " | Strike: " + String(event.strike) + " | Dip: "  + String(event.dip) + " | Rake: "  + String(event.rake) + '<img src="static/beachballs/beachball_'+ String(event.id) + '.png"/></a></li>';

                            });
                        } else {
                            popup += '<li style="list-style-type: None;"> No seismic events found in this area. </li>';
                        }
                        popup += '</ol>';
                        popup += '</div>';

                        // to create the content of the selected areas sidepanel
                        // featureLayer.on('click', function () {
                        // Change 'tab-1' to the appropriate tab ID
                        $('#tab-1').html(popup);
                        // Open the side panel
                        $("#panelID").addClass("opened");
                        // })
    

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