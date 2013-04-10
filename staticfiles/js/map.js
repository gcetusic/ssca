// list of current markers
var markersArray = [];

// Limiting scrolling past poles: http://stackoverflow.com/questions/3901611/google-maps-api-v3-limit-map-bounds
var allowedBounds = false;

// Google Maps callback (init) function as defined in main html src tag
function initialize() {

    /***************** Main map *******************/
    
    function loadMarkers() {
        // fetches new markers every time the map stops moving
        google.maps.event.addListener(map, 'idle', getMarkers);    
        google.maps.event.addListener(map, 'idle', function() {
            if (!allowedBounds) {
                // set initial bounds
                allowedBounds = map.getBounds();
            }
        });
        google.maps.event.addListener(map, 'drag', checkBounds);
        google.maps.event.addListener(map, 'zoom_changed', checkBounds); 
        google.maps.event.addListener(map, 'bounds_changed', checkBounds); 
    }
    
    // load markers with label lib
    var script = document.createElement("script");
    script.type = "text/javascript";
    script.src = markers_with_label_script_src;
    script.onload = loadMarkers;
    document.body.appendChild(script);

    // create map
    var map = new google.maps.Map(
        document.getElementById("map-canvas"), {
            // set options, some must be defined in the html 
            center: new google.maps.LatLng(center_latitude, center_longitude),
            zoom: map_zoom,
            minZoom: min_zoom,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        }
    );
    
    // Icons source: https://developers.google.com/chart/infographics/docs/dynamic_icons#pins    
    var pinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_xpin_letter_withshadow&chld=pin_star|%E2%80%A2|CC3300|000000|FF9900", new google.maps.Size(45, 42), new google.maps.Point(0, 0), new google.maps.Point(10, 34));
    var pinShadow = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_shadow", new google.maps.Size(40, 37), new google.maps.Point(0, 0), new google.maps.Point(12, 35));

    // Determines timezone of client browser
    /* This is important because a query to the database has to fetch
        markers by dates based on the client's timezone, not the server's  */
    function getTimezoneName() {
        timezone = jstz.determine();
        return timezone.name();
    }

    // Add marker but check if its category should be visible
    function addMarker(position, id, category, count) {        
        if (category == "cluster") {
            // Recipe from: http://jsfiddle.net/yV6xv/21/
            marker = new MarkerWithLabel({
                map: map,
                position: position,
                icon: pinImage,
                shadow: pinShadow,
                labelContent: count,
                labelAnchor: new google.maps.Point(12, -5),
                labelClass: "cluster-label"
            });        
        } else {
            marker = new google.maps.Marker({
                position: position,
                map: map,
            });
        }
        if ($("#type-filter input[value='" + category + "']").prop("checked") == false) {
            marker.setVisible(false);
        }

        marker.id = id;
        marker.category = category;

        markersArray.push(marker);
    }

    // Infowindow
    function prettyData(data, category) {
        var string;
        if (category=='members') {
            string = data.name + '<br />' + data.date + '<br />' + data.position;
        }
        else if (category=='guides') {
            string = data.title + '<br />' + data.date + '<br />' + data.author + '<br />' + data.portname;
        }
        else if (category=='stations') {
            string = data.name + '<br />' + data.phone + '<br />' + data.email +'<br />' + data.portname;
        }
        return string;
    }

    // Receives gmaps coordinates object
    function formatCoordinates(coord) {
        if (coord.lat() >= 0) {
            var latitude_degrees = Math.round(coord.lat()) + "N";
        } else {
            var latitude_degrees = Math.abs(Math.round(coord.lat())) + "S";
        }

        if (coord.lng() >= 0) {
            var longitude_degrees = Math.round(coord.lng()) + "E";
        } else {
            var longitude_degrees = Math.abs(Math.round(coord.lng())) + "W";
        }

        var latitude_minutes = (coord.lat() % 1)*60;
        latitude_minutes = latitude_minutes.toPrecision(2);

        var longitude_minutes = (coord.lng() % 1)*60;
        longitude_minutes = longitude_minutes.toPrecision(2);

        return latitude_degrees + " " + latitude_minutes + "'" + ", "
            + longitude_degrees  + " " + longitude_minutes + "'"
    }

    // Shows any marker currently in the marker array
    function showOverlays() {
        $("#center").html(formatCoordinates(map.getCenter()));

        if (markersArray) {
            for (i in markersArray) {
                // If the marker is a cluster center on it and zoom in
                // This will trigger the 'idle' event and consequently fetch new markers
                if (markersArray[i].category=='cluster') {
                    google.maps.event.addListener(markersArray[i], 'click', function() {
                        map.setZoom(map.getZoom()+1);
                        map.panTo(this.getPosition());
                    });
                }
                // Otherwise, fetch marker info from server by sending the id and display
                else { (function(marker) {
                    google.maps.event.addListener(marker, 'click', function () {
                        $.ajax({
                            async: false,
                            type: "POST",
                            url: marker_info,
                            dataType: "json",
                            data: {
                                "id": marker.id,
                                "category": marker.category,
                                "timezone": getTimezoneName()
                            },
                            success: function (data) {
                                infowindow = new google.maps.InfoWindow();
                                infowindow.setContent(prettyData(data, marker.category));
                                infowindow.open(map, marker);
                            }
                        });
                    });
                })(markersArray[i]);}
            }
        }
    }


    // Deletes all markers by removing references to them
    function deleteOverlays() {
        if (markersArray) {
            for (i in markersArray) {
                markersArray[i].setMap(null);
            }
            markersArray.length = 0;
        }
    }

    // Fetches markers from the server
    /* The function receives an integer argument that basically means:
        "Get me all markers that represent locations in the last n minutes "
        The default is 0 which means the latest location.
        What marker type this applies to is a server side decision. */
    function getMarkers(time) {

        /* Gather all the necessary data:
            current borders, client timezone name and the time parameter.
            Also, send zoom level for server to calculate clusters.
            The borders are used by the server to only calculate with
            those markers within the map to optimize performance.  */

        var time = time || 0;
        var center = map.getCenter().lat();
        var bounds = map.getBounds();
        var ne = bounds.getNorthEast();
        var sw = bounds.getSouthWest();
        var information = {
            "north": ne.lat(),
            "south": sw.lat(),
            "east": ne.lng(),
            "west": sw.lng(),
            "timezone": getTimezoneName(),
            "time": time,
            "zoom": map.getZoom(),
            "clustering": clustering
        }

        // Send gathered data to server and receive response
        /* The response is a json object that contains
            1. position - a tuple with latitude and longitude
            3. id - the specific id of the marker, sent only if the marker isn't a cluster
            2. category - a string, either 'stations', 'ports', 'members' or cluster
                - if the category is a cluster, the marker represents
                not a single precise location but a grouping of markers */

        $.ajax({
            async: false,
            type: "POST",
            url: gmaps_viewer,
            dataType: "json",
            data: information,
            success: function(data) {
                // Delete all the old markers
                deleteOverlays();
                // Add new markers and show them
                data.forEach(function(item) {
                    addMarker(
                        new google.maps.LatLng(item.position[0], item.position[1]),
                        item.id,
                        item.category,
                        item.count
                    );
                });
                showOverlays();
            }
        });
    }
    
    function checkBounds() {
        // limit the bounds on drag and zoom_changed to not go past the poles
        
        //if (map.getZoom() < 7) map.setZoom(7);    
        
        if (allowedBounds) {       
            var allowed_ne_lng = allowedBounds.getNorthEast().lng();
            var allowed_ne_lat = allowedBounds.getNorthEast().lat();
            var allowed_sw_lng = allowedBounds.getSouthWest().lng();
            var allowed_sw_lat = allowedBounds.getSouthWest().lat();
          
            var currentBounds = map.getBounds();
            var current_ne_lng = currentBounds.getNorthEast().lng();
            var current_ne_lat = currentBounds.getNorthEast().lat();
            var current_sw_lng = currentBounds.getSouthWest().lng();
            var current_sw_lat = currentBounds.getSouthWest().lat();
          
            var currentCenter = map.getCenter();
            var centerX = currentCenter.lng();
            var centerY = currentCenter.lat();
          
            // For now only limit Y
            
            //if (current_ne_lng > allowed_ne_lng) centerX = centerX-(current_ne_lng-allowed_ne_lng);
            if (current_ne_lat > allowed_ne_lat) centerY = centerY-(current_ne_lat-allowed_ne_lat);
            //if (current_sw_lng < allowed_sw_lng) centerX = centerX+(allowed_sw_lng-current_sw_lng);
            if (current_sw_lat < allowed_sw_lat) centerY = centerY+(allowed_sw_lat-current_sw_lat);
          
            map.setCenter(new google.maps.LatLng(centerY,centerX));
        }
    }

    /**********************************************/


    /***************** Overview Map ***************/
    var overlayMap = new google.maps.Map(
        document.getElementById('overlayMap'),
        {
            mapTypeId: google.maps.MapTypeId.ROADMAP, // Always show roadmap
            disableDefaultUI: true, // Turn off the controls
            scrollwheel: false, // Disable scrollwheel zooming
            disableDoubleClickZoom: true,
            center: new google.maps.LatLng(center_latitude, center_longitude),
            zoom: map_zoom,
        }
    );

    var translucentBox = new google.maps.Polygon({
        strokeColor: "#4444BB",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#4444BB",
        fillOpacity: 0.25
    });

    var transparentBox = new google.maps.Polygon({
        strokeColor: "#4444BB",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#4444BB",
        fillOpacity: 0.01
    });
    transparentBox.setMap(overlayMap);

    function pathFromBounds(bounds) {
        var northEastCorner = bounds.getNorthEast();
        var southWestCorner = bounds.getSouthWest();
        var northEastLat = northEastCorner.lat();
        var northEastLng = northEastCorner.lng();
        var southWestLat = southWestCorner.lat();
        var southWestLng = southWestCorner.lng();
        var southEastCorner = new google.maps.LatLng(southWestLat, northEastLng);
        var northWestCorner = new google.maps.LatLng(northEastLat, southWestLng);

        return [
            northEastCorner,
            southEastCorner,
            southWestCorner,
            northWestCorner,
            northEastCorner
        ];
    }

    function updateOverlayMapCenter() {
        var newCenter = map.getCenter();
        if (overlayMap.getCenter() !== newCenter) {
          overlayMap.panTo(newCenter);
        }
    }

    google.maps.event.addListener(map, 'bounds_changed', function () {
        var newBounds = map.getBounds();
        var path = [];
        if (newBounds !== undefined) {
            var mapWidth = null;
            var mapHeight = null;
            (function () {
                var northEastCorner = newBounds.getNorthEast();
                var southWestCorner = newBounds.getSouthWest();
                var northEastLat = northEastCorner.lat();
                var northEastLng = northEastCorner.lng();
                var southWestLat = southWestCorner.lat();
                var southWestLng = southWestCorner.lng();

                mapHeight = Math.abs(180 + northEastLat - southWestLat) - 180;
                mapWidth = Math.abs(360 + northEastLng - southWestLng) - 360;
            })();

            var overlayMapHeight = null;
            var overlayMapWidth = null;
            (function () {
                var overlayBounds = overlayMap.getBounds();
                var northEastCorner = overlayBounds.getNorthEast();
                var southWestCorner = overlayBounds.getSouthWest();
                var northEastLat = northEastCorner.lat();
                var northEastLng = northEastCorner.lng();
                var southWestLat = southWestCorner.lat();
                var southWestLng = southWestCorner.lng();

                overlayMapHeight = Math.abs(180 + northEastLat - southWestLat) - 180;
                overlayMapHeight = overlayMapHeight / 2;
                overlayMapWidth = Math.abs(360 + northEastLng - southWestLng) - 360;
            })();

            var heightOverage = (overlayMapHeight - mapHeight);
            var widthOverage = (overlayMapWidth - mapWidth);
            var margin = 0.2;
            var divisor = (2 + 2 * margin);
            var wayTooBig = false;
            if (
                // margin of one means zoom in when overage is big enough that
                // zooming in would leave > half of width
                // which would be when overage is > three quarters width

                // margin of zero mean zoom in when overage is > half width
                (widthOverage > (divisor - 1) * (overlayMapWidth / divisor)) &&
                (heightOverage > (divisor - 1) * (overlayMapHeight / divisor))
            ) {
                //FIXME: sometimes it isn't enough to change by only 1.
                overlayMap.setZoom(overlayMap.getZoom() + 2);
            } else if (
                // margin of one means, zoom out when overage is < half width
                // margin of half means zoom out when overage is < quarter width
                // margin of zero means zoom out when overage is < 0
                (widthOverage < margin * overlayMapWidth / 2) ||
                (heightOverage < margin * overlayMapHeight / 2)
            ) {
                var overlayZoom = overlayMap.getZoom();
                if (overlayZoom > 0) {
                  //FIXME: sometimes it isn't enough to change by only 1.
                    overlayMap.setZoom(overlayZoom - 1);
                } else {
                  wayTooBig = true;
                }
            }
            if (wayTooBig === false) {
                path = pathFromBounds(newBounds);
            }
        }
        translucentBox.setPath(path);
    });

    function degToRad(degrees) {
        return degrees * Math.PI / 180;
    }

    function latToY(latitude) {
        var lat = degToRad(latitude);
        return Math.log(Math.tan(lat) + 1 / Math.cos(lat));
    }

    function radToDeg(radians) {
        return radians * 180 / Math.PI;
    }

    function yToLat(y) {
        var angle = 2 * Math.atan(Math.pow(Math.E, y)) - Math.PI / 2;
        return radToDeg(angle);
    }

    google.maps.event.addListener(overlayMap, 'bounds_changed', function () {
        var mapBounds = map.getBounds();
        if (mapBounds !== undefined) {
            var northEastCorner = mapBounds.getNorthEast();
            var southWestCorner = mapBounds.getSouthWest();
            var northEastLat = northEastCorner.lat();
            var northEastLng = northEastCorner.lng();
            var southWestLat = southWestCorner.lat();
            var southWestLng = southWestCorner.lng();

            var mapCenter = map.getCenter();
            var overlayCenter = overlayMap.getCenter();
            var lngDelta = overlayCenter.lng() - mapCenter.lng();
            northEastLng += lngDelta;
            southWestLng += lngDelta;

            var overlayMapBounds = overlayMap.getBounds();
            var overlayTopLat = overlayMapBounds.getNorthEast().lat();
            var overlayBottomLat = overlayMapBounds.getSouthWest().lat();
            var overlayTop = latToY(overlayTopLat);
            var overlayBottom = latToY(overlayBottomLat);
            var overlayHeight = Math.abs(overlayTop - overlayBottom);
            var mapHeight = Math.abs(latToY(northEastLat) - latToY(southWestLat));

            var bottomLatDelta = overlayBottom + (overlayHeight - mapHeight) / 2;
            var topLatDelta = overlayTop - (overlayHeight - mapHeight) / 2;
            northEastLat = yToLat(topLatDelta);
            southWestLat = yToLat(bottomLatDelta);

            var sw = new google.maps.LatLng(southWestLat, southWestLng);
            var se = new google.maps.LatLng(southWestLat, northEastLng);
            var ne = new google.maps.LatLng(northEastLat, northEastLng);
            var nw = new google.maps.LatLng(northEastLat, southWestLng);
            transparentBox.setPath([sw, nw, ne, se, sw]);
        }
    });

    google.maps.event.addListener(map, 'zoom_changed', function () {
        var newZoom = Math.max(map.getZoom() - 4, 0);
        if (overlayMap.getZoom() !== newZoom) {
            overlayMap.setZoom(newZoom);
        }
    });

    var mapDragInProgress = false;
    var panHasBegun = false;

    google.maps.event.addListener(map, 'center_changed', function () {
        if ((mapDragInProgress === false) && (panHasBegun === false)) {
            updateOverlayMapCenter();
        }
    });

    google.maps.event.addListener(map, 'idle', function () {
        if (panHasBegun === true) {
            panHasBegun = false;
            mapDragInProgress = false;
        }
    });

    google.maps.event.addListener(map, 'dragstart', function () {
        panHasBegun = false;
        mapDragInProgress = true;
    });

    google.maps.event.addListener(map, 'dragend', function () {
        updateOverlayMapCenter();
        mapDragInProgress = false;
    });

    google.maps.event.addListener(overlayMap, 'dragstart', function () {
        panHasBegun = false;
        mapDragInProgress = true;
    });

    google.maps.event.addListener(overlayMap, 'dragend', function () {
        panHasBegun = true;
        var newCenter = overlayMap.getCenter();
        if (map.getCenter() !== newCenter) {
          map.panTo(newCenter);
        }
    });

    google.maps.event.addListener(overlayMap, 'dblclick', function (mEvent) {
        mapDragInProgress = true;
        overlayMap.panTo(mEvent.latLng);
        map.panTo(mEvent.latLng);
    });

    google.maps.event.addListener(map, 'maptypeid_changed', function () {
        overlayMap.setOptions({mapTypeId: map.getMapTypeId()});
    });

    overlayMap.setZoom(0);
    overlayMap.setCenter(new google.maps.LatLng(center_latitude, center_longitude));

    /************************************************/


    /***************** Map Controls *****************/
    // shows all markers of a particular category
    function showCategory(category) {
        for (var i=0; i<markersArray.length; i++) {
            if (markersArray[i].category == category) {
                markersArray[i].setVisible(true)
            }
        }
    }

    // hides all markers of a particular category
    function hideCategory(category) {
        for (var i=0; i<markersArray.length; i++) {
            if (markersArray[i].category == category) {
                markersArray[i].setVisible(false);
            }
        }
    }

    $(document).ready(function() {
        // Show all received markers by default, regardless of category
        $("#type-filter input[name='type']").prop("checked", true);
        $("#time-filter input[value='current']").prop("checked", true);
        $("#type-filter input[name='type']").live('click', function () {
            if ($(this).is(":checked")) {
                showCategory(this.value);
            }
            else {
                hideCategory(this.value);
            }
            if($("#type-filter input[name='type']:checked").length < 1) {
                // hide empty clusters
                hideCategory("cluster");
            }
        });

        // Refetch markers from server if timeframe is changed
        $("#time-filter input[name='time']").change(function () {
            var time;
            if ($(this).val() == 'current') {
                time = 0;
            }
            if ($(this).val() == 'recent') {
                time = 30;
            }
            getMarkers(time);
        });

        /************************************** Search ***************************************/
        /* The search is implemented using a typeahead input field.
            Normally, typeahead would send a request to the server on every keystroke.
            If the server is low on resources, this could become a problem.
            So instead of sending the string directly to the server, the string is put
            in an array that acts like a queue. Every two seconds only the latest string in
            the queue is sent to the server and the queue is emptied until the next keystroke.
            When user inputs text, a searchqueue is filled with the current input text.
        */
        var searchqueue = [];
        setInterval(function () {
            if (searchqueue.length > 0) {
            text = searchqueue.pop();
            text.call();
            searchqueue = [];
            }
        }, 2000);

        var wrapFunction = function(fn, context, params) {
            return function() {
                fn.apply(context, params);
            };
        }

        var search_results;
        function find(query, process) {
            var funsearch = function (query, process) {
                $.ajax({
                    type: "POST",
                    url: member_finder,
                    data: {
                        "search": query,
                        "timezone": getTimezoneName()
                    },
                    dataType: "json",
                    success: function (results) {
                        var resultsArray = new Array;
                        // A maximum of 20 results shown
                        if (results.length <= 20) {
                            search_results = results;
                            // We need the marker id to choose the correct one later
                            // Hide the id of the marker
                            results.forEach(function (item, index) {
                                result = "<div pk='" + index + "' style='visibility:hidden;'>" + "</div>"
                                    + item.fields.person.fields.user.fields.first_name + ' '
                                    + item.fields.person.fields.user.fields.last_name + ' ('
                                    + item.fields.person.fields.user.fields.email + ')'
                                resultsArray.push(result);
                            });
                            process(resultsArray);
                        }
                    }
                });
            };
            searchqueue.push(wrapFunction(funsearch, this, [query, process]));
        }

        $('#member_modal').modal({
            show: false,
            keyboard: false,
            backdrop: 'static'
        }).css({
            width: 'auto',
            'margin-left': function () {
                return -($(this).width() / 2);
            }
        });

        // When the find button is clicked, specific marker is located and zoomed on
        $('#modal_find').on('click', function () {
            $('#member_modal').modal('hide');
            var member = search_results[$("#modal_search").attr("pk")];
            var center = new google.maps.LatLng(member.fields.latitude, member.fields.longitude);
            map.panTo(center);
            // Zoom level is a "within a few miles" approximate
            map.setZoom(5);
        })

        // Clear the search field if modal is hidden
        $('#member_modal').on('hidden', function () {
            $(this).find("input[type=text], textarea").val("");
        })

        // Some functions aren't needed but included as templates
        $(".memberTypeahead").typeahead({
            minLength: 3,
            items: 10,
            source: find,
            updater: function(item) {
                // Extract the marker id
                var wrapper= document.createElement('div');
                wrapper.innerHTML= item;
                var div= wrapper.firstChild;
                $("#modal_search").attr("pk", $(div).attr('pk'));
                return item.split("/div>")[1];
            },
            matcher: function(item) {
                return true;
            },
            sorter: function(items) {
                return items;
            }
        })
    });
};
