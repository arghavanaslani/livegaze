function drop(event) {
    const parent = $("#board_parent")[0];
    event.preventDefault();
    const jsonString = event.dataTransfer.getData("application/json");
    if (jsonString) {
        const data = JSON.parse(jsonString);
        if (data && data.type === "stimulus") {
            const draggedElement = document.getElementById(data.id);
            const src = draggedElement.src;
            const newElement = document.createElement("img");
            newElement.src = src;
            newElement.className = "stim-on-board";
            // extract id of the stimulus from element id : stimulusImg<id>
            newElement.dataset.id = data.id.split("stimulusImg")[1];
            parent.appendChild(newElement);
        }
    }
}

function allowDrop(event) {
    event.preventDefault();
}


function add_draggable_functions(child) {
    child.addEventListener("dragstart", function (event) {
            var sendData = {"type": "stimulus", "id": event.target.id};
            event.dataTransfer.setData("application/json", JSON.stringify(sendData));
            event.dataTransfer.setDragImage(event.target, 0, 0);
            event.target.style.opacity = "0.5";
            // event.dataTransfer.effectAllowed = "copy"; // Enables the green plus sign
        });

        child.addEventListener("dragend", (event) => {
            event.target.style.opacity = "1";
        });
}

function initialize_drag() {
    console.log("initialize_drag");
    const images = $(".draggable-img");
    for (let i = 0; i < images.length; i++) {
        if (!images[i].draggable) continue;
        const child = images[i]

        add_draggable_functions(child);
    }

    const board_parent = $("#board_parent");
    // board_parent.on("dragover", function (event) {
    //     // event.dataTransfer.dropEffect = "copy"; // Shows the green plus sign
    // });

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });
}

function upload_stim() {
    let fileInput = document.getElementById("fileInput");
    let file = fileInput.files[0];
    if (!file) {
        return;
    }
    console.log(file);
    let formData = new FormData();
    formData.append("stim_file", file);

    $.ajax({
        url: '/boards/upload_stim',
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function (response) {
            console.log(response);
            let newStim = document.createElement('div');
            newStim.classList = ['col-md-4']
            newStim.id = 'stimulus'+response.stim_id

            let innerCard = document.createElement('div');
            innerCard.classList = ['card', 'stim-card', 'justify-content-center', 'border-0']
            newStim.appendChild(innerCard);

            let cardImg = document.createElement('img');
            cardImg.classList = 'card-img draggable-img'
            cardImg.alt = '...'
            cardImg.id="stimulusImg"+response.stim_id
            cardImg.draggable = this
            cardImg.src = '../'+response.stim_path
            cardImg.style = "cursor: grab"
            innerCard.appendChild(cardImg);

            add_draggable_functions(cardImg);
            let stim_parent = document.getElementById('stimuli_parent')
            let last_child = stim_parent.lastChild
            let second_last_child = last_child.previousSibling
            stim_parent.insertBefore(newStim, second_last_child)
        },
        error: function (response) {
            console.log(response);
            alert("Error uploading stimulus");
        }
    })
}

function save_board() {
    const parent = $("#board_parent")[0];
    const board_name = $("#board_name_input").val();
    if (board_name === "") {
        alert("Please enter a name for the board");
        return;
    }
    const stimuli = [];
    for (let i = 0; i < parent.children.length; i++) {
        const child = parent.children[i];
        if (child.className !== "stim-on-board") {
            continue;
        }
        stimuli.push(child.dataset.id);
    }
    if (stimuli.length === 0) {
        alert("Please add at least one stimulus to the board");
        return;
    }
    const data = {
        "board_name": board_name,
        "stimuli": stimuli
    };
    //POST request to save the board at /save_board
    $.ajax({
        type: "POST",
        url: "/boards/save_board",
        data: data,
        // contentType: "application/json",
        success: function (response) {
            console.log(response);
            window.location.href = "/";
        },
        error: function (response) {
            console.log(response);
            alert("Error saving board");
        }
    });
}


$(document).ready(initialize_drag)