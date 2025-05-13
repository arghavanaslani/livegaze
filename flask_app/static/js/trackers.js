$(document).ready(function() {
    // Create Socket.IO connection to /tracker
    const socket = io('/tracker');

    socket.on('connect', () => {
        socket.emit('subscribe_tracker_data');
        console.log("Connected to tracker socket");
    })

    socket.on('update_tracker_status', (data) => {
        console.log("Tracker status update:", data);
        tracker_id = data.tracker_id
        tracker_status = data.tracker_status
        // update the table, find the row with the tracker_id and update the status
        let row = document.getElementById(`tracker-${tracker_id}`);
        if (row) {
            let statusCell = row.querySelector('.tracker-status');
            if (statusCell) {
                console.log(tracker_status)
                switch (tracker_status) {
                    case 0:
                        statusCell.textContent = "Inactive";
                        break
                    case 1:
                        statusCell.textContent = "Ready";
                        break
                    case 2:
                        statusCell.textContent = "Sending Data";
                        break
                }
            }
        } else {
            //create a new row
            let table = document.getElementById("trackers-list-body");
            let newRow = document.createElement("tr");
            let statusText = ""
            switch (tracker_status) {
                    case 0:
                        statusText = "Inactive";
                        break
                    case 1:
                        statusText = "Ready";
                        break
                    case 2:
                        statusText = "Sending Data";
                        break
                }
            newRow.id = `tracker-${tracker_id}`;
            newRow.innerHTML = `
                <th scope="row">${tracker_id}</th>
                <td class="tracker-status">${statusText}</td>
            `;
            table.appendChild(newRow);
        }

    })

})