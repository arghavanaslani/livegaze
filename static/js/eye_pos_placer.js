DEBUG = true
let markerBases = {}
let marker_parent = null
var selected_marker_url = null

function create_socket() {


    const socket = io('http://127.0.0.1:5001/board');

    marker_parent = document.getElementById("markerParent")

    socket.on('connect', () => {
        socket.emit('subscribe_gaze_data', {"board_id": arucoId})
    })

    let marker_urls = ['../../static/gradientCircle.svg', '../../static/circleFullWhite.png', '../../static/circleFullWhite.png']
    selected_marker_url = marker_urls[selectedMarkerId];


    socket.on('gaze_data', (data) => {
        parse_gaze_data(data)
    })
}

function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function parse_gaze_data(data) {

    let tag = document.getElementById("arucoTag0")
    let tag_size = tag.getBoundingClientRect().width;
    for (let tracker_id in data) {
        if (markerBases[tracker_id] === undefined) {
            let color = getRandomColor()
            let markerBase = document.createElement('div');
            markerBase.style.position = "absolute";

            markerBase.style.transform = "translate(-50%, -50%)";

            markerBases[tracker_id] = markerBase;

            fetch(selected_marker_url).then(response => response.text()).then(svgContent => {
                markerBase.innerHTML = svgContent

                const style = markerBase.querySelector('style');
                if (style) {
                    console.log("style found")
                    style.textContent = style.textContent.replace(/\.cls-1/g, `.cls-1-${tracker_id}`);
                }

                const ellipse = markerBase.querySelector('ellipse');
                if (ellipse) {
                    ellipse.setAttribute('class', `cls-1-${tracker_id}`);
                }

                const radialGradient = markerBase.querySelector('#radial-gradient');
                if (radialGradient) {
                    const newId = 'radial-gradient-'+tracker_id;
                    radialGradient.id = newId;

                    // Update all references to the old ID in the SVG
                    const style = markerBase.querySelector('style');
                    if (style) {
                        style.textContent = style.textContent.replace(/#radial-gradient/g, `#${newId}`);
                    }

                    // Update any other references within the SVG
                    const elementsUsingGradient = markerBase.querySelectorAll(`[fill="url(#radial-gradient)"]`);
                    elementsUsingGradient.forEach(el => {
                        el.setAttribute('fill', `url(#${newId})`);
                    });
                }

                if (selectedMarkerId === 0) {
                    const stops = markerBase.querySelectorAll('stop')
                    stops.forEach(stop => {
                        stop.setAttribute('stop-color', color);
                    })
                }
            }).catch(error => {
                console.error('Error fetching the SVG:', error);
            });

            marker_parent.appendChild(markerBase);

        }
        let min_img_l = Math.min(window.innerWidth, window.innerHeight)
        let pointer_size_pixel = Math.floor(pointerSize * min_img_l * 0.25)

        let x = data[tracker_id]['pos_x'] * (window.innerWidth - tag_size) + tag_size / 2;
        let y = data[tracker_id]['pos_y'] * (window.innerHeight - tag_size) + tag_size / 2;
        markerBases[tracker_id].style.height = pointer_size_pixel + 'px';
        markerBases[tracker_id].style.width = pointer_size_pixel + 'px';
        markerBases[tracker_id].style.left = x + 'px';
        markerBases[tracker_id].style.top = y + 'px';
    }

}

$(document).ready(create_socket);