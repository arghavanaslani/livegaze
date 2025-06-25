function drop(event) {
    const parent = $("#board_parent")[0];
    event.preventDefault();
    const jsonString = event.dataTransfer.getData("application/json");
    if (jsonString) {
        const data = JSON.parse(jsonString);
        if (data && data.type === "stimulus" && data.stimtype === "0") {
            const draggedElement = document.getElementById(data.id);
            const src = draggedElement.src;
            const newElement = document.createElement("img");
            newElement.src = src;
            newElement.className = "stim-on-board";
            // extract id of the stimulus from element id : stimulusImg<id>
            newElement.dataset.id = data.id.split("stimulusImg")[1];
            parent.appendChild(newElement);
        } else if (data && data.type === "stimulus" && data.stimtype === "1") {
            const newElement = document.createElement("video");
            newElement.autoplay = true;
            newElement.muted = true;
            newElement.className = "stim-on-board";
            newElement.dataset.id = data.id.split("stimulusImg")[1];
            newElement.controls = true;

            const source = document.createElement("source");
            source.src = data.src;
            source.type = "video/mp4";
            newElement.appendChild(source);
            parent.appendChild(newElement);
        } else if (data && data.type === "stimulus" && data.stimtype === "2") {
            const newElement = document.createElement("iframe");
            newElement.src = "https://www.youtube.com/embed/" + data.src + "?autoplay=1&mute=1&showinfo=0";
            newElement.className = "stim-on-board";
            newElement.dataset.id = data.id.split("stimulusImg")[1];
            parent.appendChild(newElement);
        } else if (data && data.type === "stimulus" && data.stimtype === "3") {
            const newElement = document.createElement("iframe");
            newElement.src = data.src;
            newElement.className = "stim-on-board";
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
        var sendData = {"type": "stimulus", "id": event.target.id, "stimtype": event.target.dataset.stimtype,
        "src": event.target.dataset.src};
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

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });
}

function prepare_submit_youtube() {
    $("#youtube_form").submit(function (event) {
        event.preventDefault();


    });

    $("#upload-form").submit(function (event) {
        event.preventDefault();

        let filetype = $("#fileType").val();
        if (filetype === "0") {
            upload_image();
        } else if (filetype === "1") {
            upload_video();
        } else if (filetype === "2") {
            upload_youtube();
        } else if (filetype === "3") {
            upload_webpage();
        }
    });
}

function create_new_card(stim_id, stim_path, thumbnail_path, stim_type) {
    let newStim = document.createElement('div');
    newStim.classList = 'col-md-4'
    newStim.style="margin-top: 1vh"
    newStim.id = 'stimulus' + stim_id

    let innerCard = document.createElement('div');
    innerCard.classList = 'card stim-card justify-content-center border-0'
    newStim.appendChild(innerCard);
    let cardImg;
    if (stim_type !== 'webpage') {
        cardImg = document.createElement('img');
        cardImg.classList = 'card-img draggable-img'
        cardImg.alt = '...'
        cardImg.id = "stimulusImg" + stim_id
        cardImg.draggable = this
        console.log('stim_type', stim_type);
        if (stim_type === 'image') {
            console.log('image', stim_path);
            cardImg.src = '../' + stim_path
            cardImg.dataset.stimtype = "0"
            cardImg.dataset.src = stim_path
        } else if (stim_type.includes('youtube')) {
            console.log('youtube', stim_path);
            cardImg.src = 'https://img.youtube.com/vi/' + stim_path + '/hqdefault.jpg'
            cardImg.dataset.stimtype = "2"
            cardImg.dataset.src = stim_path
        }
        if (stim_type === 'video') {
            console.log('video', stim_path);
            // remove the extension from the path add jpg
            cardImg.dataset.src = '../' + stim_path
            cardImg.src = '../' + thumbnail_path
            cardImg.dataset.stimtype = "1"
        }
    } else if (stim_type === 'webpage') {
        cardImg = document.createElement('h5');
        console.log('webpage', stim_path);
        cardImg.classList = 'card-img draggable-img'
        cardImg.id = "stimulusImg" + stim_id
        cardImg.draggable = this
        cardImg.src = '../' + thumbnail_path
        cardImg.dataset.stimtype="3"
        cardImg.dataset.src = stim_path
        cardImg.tagName = 'h5'
        cardImg.innerText = stim_path;
    }
    cardImg.style = "cursor: grab"
    innerCard.appendChild(cardImg);
    if (stim_type.includes('youtube')) {
        let youtubeIcon = document.createElement('img');
        youtubeIcon.src = '../static/icons/youtube.png';
        youtubeIcon.classList = 'stim-vid-icon card-img';
        innerCard.appendChild(youtubeIcon);
    } else if (stim_type === 'video') {
        let youtubeIcon = document.createElement('img');
        youtubeIcon.src = '../static/icons/play.png';
        youtubeIcon.classList = 'stim-vid-icon card-img';
        innerCard.appendChild(youtubeIcon);
    } else if (stim_type === 'webpage') {
        let webpageIcon = document.createElement('img');
        webpageIcon.src = '../static/icons/webpage.png';
        webpageIcon.classList = 'stim-vid-icon card-img';
        innerCard.appendChild(webpageIcon);
    }

    add_draggable_functions(cardImg);
    let stim_parent = document.getElementById('stimuli_parent')
    let last_child = stim_parent.lastChild
    let second_last_child = last_child.previousSibling
    stim_parent.insertBefore(newStim, second_last_child)
}

function upload_image() {
    let fileInput = document.getElementById("imageFile");
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
            $("#uploadModal").modal("hide");
            create_new_card(response.stim_id, response.stim_path, response.stim_path,'image');
        },
        error: function (response) {
            console.log(response);
            $("#error-message").text("Error submitting video");
            alert("Error uploading stimulus");
        }
    })
}

function upload_video() {
    let fileInput = document.getElementById("videoFile");
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
            $("#uploadModal").modal("hide");
            create_new_card(response.stim_id, response.stim_path, response.thumbnail_path,'video');
        },
        error: function (response) {
            console.log(response.responseText);
            $("#error-message").text("Error submitting video");
            alert("Error uploading stimulus");
        }
    })
}

function upload_youtube() {
    let videoId = $("#youtube_video_id").val();

    $.ajax({
        type: "POST",
        url: "submit_youtube",
        data: {video_id: videoId},
        success: function (response) {
            console.log(response);
            $("#uploadModal").modal("hide");
            $("#youtube_video_id").val("");
            console.log(response.stim_id, response.stim_path, 'youtube');
            // create a card from the video and append it to the list of cards
            create_new_card(response.stim_id, response.stim_path, response.stim_path, 'youtube');

        },
        error: function (response) {
            $("#error-message").text("Error submitting video");
        }
    });
}

function upload_webpage() {
    let webUrl = $("#webpageEmbedUrl").val();

    $.ajax({
        type: "POST",
        url: "submit_webpage",
        data: {web_url: webUrl},
        success: function (response) {
            console.log(response);
            $("#uploadModal").modal("hide");
            $("#webpageEmbedUrl").val("");
            console.log(response.stim_id, response.stim_path, 'webpage');
            // create a card from the video and append it to the list of cards
            create_new_card(response.stim_id, response.stim_path, response.stim_path, 'webpage');

        },
        error: function (response) {
            $("#error-message").text("Error submitting video");
        }
    });
}

function save_board() {
    const parent = $("#board_parent")[0];
    const board_name = $("#board_name_input").val();
    if (board_name === "") {
        alert("Please enter a name for the board");
        return;
    }
    const stimuli = [];
    const stimuli_types = [];
    for (let i = 0; i < parent.children.length; i++) {
        const child = parent.children[i];
        if (child.className !== "stim-on-board") {
            continue;
        }
        stimuli.push(child.dataset.id);
        stimuli_types.push(child.dataset.stimtype);
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

function changeInputGroup() {
    let selectedInputGroup = document.getElementById("fileType").value;
    let imageInputGroup = document.getElementById("imageInputGroup");
    let videoInputGroup = document.getElementById("videoInputGroup");
    let youtubeInputGroup = document.getElementById("youtubeInputGroup");
    let webpageInputGroup = document.getElementById("webpageEmbedInputGroup");
    if (selectedInputGroup=== "0") {
        imageInputGroup.style.display = "";
        videoInputGroup.style.display = "none";
        youtubeInputGroup.style.display = "none";
        webpageInputGroup.style.display = "none";
    } else if (selectedInputGroup === "1") {
        imageInputGroup.style.display = "none";
        videoInputGroup.style.display = "";
        youtubeInputGroup.style.display = "none";
        webpageInputGroup.style.display = "none";
    } else if (selectedInputGroup === "2") {
        imageInputGroup.style.display = "none";
        videoInputGroup.style.display = "none";
        youtubeInputGroup.style.display = "";
        webpageInputGroup.style.display = "none";
    } else if (selectedInputGroup === "3") {
        imageInputGroup.style.display = "none";
        videoInputGroup.style.display = "none";
        youtubeInputGroup.style.display = "none";
        webpageInputGroup.style.display = "";
    } else {
        imageInputGroup.style.display = "none";
        videoInputGroup.style.display = "none";
        youtubeInputGroup.style.display = "none";
        webpageInputGroup.style.display = "none";
    }
}


$(document).ready(initialize_drag)
$(document).ready(prepare_submit_youtube);
