DEBUG = true
let colors = {}
let markers = {}

function create_socket() {


    const socket = io('http://127.0.0.1:5001');


    socket.on('connect', () => {
        socket.emit('subscribe_gaze_data', {"board_id" : arucoId})
    })

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

//data is a json with list of gaze data each in form of {x:x, y:y}
function parse_gaze_data(data) {

    //place the gaze data on the image using the x and y coordinates
    //get the image element
    //print data
    if (DEBUG) console.log(data);
    for (let tracker_id in data) {
        if (colors[tracker_id] === undefined) {
            colors[tracker_id] = getRandomColor()
            // create a new marker from the image

        }
    }

}

$(document).ready(create_socket);