
document
    .getElementById("district")
    .addEventListener("change", function() {
        const district = this.value;
        const upazillaSelect = document.getElementById("upazilla");
        upazillaSelect.innerHTML =
            '<option value="" disabled selected>Select upazilla</option>';

        if (district) {
            const cities = citiesBydistrict[district];
            cities.forEach((upazilla) => {
                const option = document.createElement("option");
                option.value = upazilla;
                option.textContent = upazilla;
                upazillaSelect.appendChild(option);
            });
        }
    });
     document
      .getElementById("district")
      .addEventListener("change", function () {
        const district = this.value;
        const upazillaSelect = document.getElementById("upazilla");
        upazillaSelect.innerHTML =
          '<option value="" disabled selected>Select upazilla</option>';

        if (district) {
          const cities = citiesBydistrict[district];
          cities.forEach((upazilla) => {
            const option = document.createElement("option");
            option.value = upazilla;
            option.textContent = upazilla;
            upazillaSelect.appendChild(option);
          });
        }
      });

function getLocation() {
    // Check if Geolocation is supported
    if (navigator.geolocation) {
        // Necessary: We need the user's location to show nearby service providers
navigator.geolocation.getCurrentPosition(showPosition, showError);
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        document.getElementById("location").innerHTML = "Geolocation is not supported by this browser.";
    }
}


function showPosition(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;
    document.getElementById("latitude").value = latitude;
    document.getElementById("longitude").value = longitude;
}


function showError(error) {
    // Handle errors
    switch (error.code) {
      case error.PERMISSION_DENIED:
        document.getElementById("location").innerHTML = "User denied the request for Geolocation.";
        break;
      case error.POSITION_UNAVAILABLE:
        document.getElementById("location").innerHTML = "Location information is unavailable.";
        break;
      case error.TIMEOUT:
        document.getElementById("location").innerHTML = "The request to get user location timed out.";
        break;
      case error.UNKNOWN_ERROR:
        document.getElementById("location").innerHTML = "An unknown error occurred.";
        break;
    }
  }
      // Initialize and add the map
      function initMap() {
        const map = new google.maps.Map(document.getElementById("map"), {
          center: { lat: 23.8103, lng: 90.4125 },
          zoom: 8,
        });
  
        const marker = new google.maps.Marker({
          position: { lat: 23.8103, lng: 90.4125 },
          map: map,
          draggable: true,
        });
  
        google.maps.event.addListener(marker, "position_changed", function () {
          const lat = marker.getPosition().lat();
          const lng = marker.getPosition().lng();
          document.getElementById("latitude").value = lat;
          document.getElementById("longitude").value = lng;
        });
  
        google.maps.event.addListener(map, "click", function (event) {
          marker.setPosition(event.latLng);
        });
      }