var selected_marker_url = null

function setup() {
    let randomSeed = Date.now();

    let marker_urls = ['../circleWireWhite.png', '../circleFullWhite.png', '../circleFullWhite.png']
    selected_marker_url = marker_urls[selectedMarkerId];
    // let marker = cv.imread(selected_marker_url);
}

function seededRandom(seed) {
    let m = 2 ** 31 - 1; // A large prime number
    let a = 16807;       // A multiplier
    let c = 0;           // Increment

    seed = (seed * a + c) % m;
    return seed / m; // Return a value between 0 and 1
}


function set_markers(data) {
    gaze_data = data['gaze_data']
    let markerParent = document.getElementById('markerParent');
    // empty the markerParent
    markerParent.innerHTML = '';
    for (let i = 0; i < gaze_data.length; i++) {
        let x = gaze_data[i]['x'];
        let y = gaze_data[i]['y'];
        let marker = document.createElement('img');
        marker.src = selected_marker_url;
        marker.className = 'marker';
        marker.style.left = x + 'px';
        marker.style.top = y + 'px';
        markerParent.appendChild(marker);
    }
}


$(document).ready(setup);

