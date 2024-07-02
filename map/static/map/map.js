
        let map, infoWindow
        let pos = { lat: 33.44, lng: -84.23 };

        async function initMap() {
        const { Map, InfoWindow } = await google.maps.importLibrary("maps");
        const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

        map = new Map(document.getElementById("map"), {
            center: pos,
            zoom: 15,
            mapId: "123891748939",
        });

        pos = getUserPos();

        const locationButton = document.createElement("button");

        locationButton.textContent = "Pan to Current Location";
        locationButton.classList.add("custom-map-control-button");
        map.controls[google.maps.ControlPosition.TOP_CENTER].push(locationButton);
        locationButton.addEventListener("click", () => {
            getUserPos();
        });

        nearbySearch();
    }

    async function nearbySearch() {
      //@ts-ignore
      const { Place, SearchNearbyRankPreference } = await google.maps.importLibrary(
        "places",
      );
      const { AdvancedMarkerElement, PinElement } = await google.maps.importLibrary("marker");
      // Restrict within the map viewport.
      let center = map.center;
      const request = {
        // required parameters
        fields: ["displayName", "location", "businessStatus", ],
        locationRestriction: {
          center: center,
          radius: 100000,
        },
        // optional parameters
        includedPrimaryTypes: ["restaurant"],
        maxResultCount: 10,
        rankPreference: SearchNearbyRankPreference.POPULARITY,
        language: "en-US",
        region: "us",
      };
      //@ts-ignore
      const { places } = await Place.searchNearby(request);

      infoWindow2 = new google.maps.InfoWindow();
      if (places.length) {
        console.log(places);

        const { LatLngBounds } = await google.maps.importLibrary("core");
        const bounds = new LatLngBounds();

        // Loop through and get all the results.
        places.forEach((place) => {
            const pin = new PinElement({
            scale: 1,
        });

          const marker = new AdvancedMarkerElement({
            map,
            position: place.location,
            title: place.displayName,

              content: pin.element,
              gmpClickable: true,
          });

        marker.addListener("click", ({ domEvent, latLng }) => {
            const { target } = domEvent;
            infoWindow2.close();
            infoWindow2.setContent(marker.title);
            infoWindow2.open(marker.map, marker);
        });

          bounds.extend(place.location);
          console.log(place);
        });
        map.fitBounds(bounds);
      } else {
        console.log("No results");
      }
    }

    initMap();

    function getUserPos() {
    let userPos;
    if (infoWindow) {
        infoWindow.close();
    }
    infoWindow = new google.maps.InfoWindow();
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    userPos = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                    };

                    infoWindow.setPosition(userPos);
                    infoWindow.open(map);
                    map.setCenter(userPos);
                },

                () => {
                    handleLocationError(true, infoWindow, map.getCenter());
                },
            );
        } else {
            // Browser doesn't support Geolocation
            handleLocationError(false, infoWindow, map.getCenter());
        }
        return userPos;
    }

    function handleLocationError(browserHasGeolocation, infoWindow, pos) {
      infoWindow.setPosition(pos);
      infoWindow.setContent(
        browserHasGeolocation
          ? "Error: The Geolocation service failed."
          : "Error: Your browser doesn't support geolocation.",
      );
      infoWindow.open(map);
    }