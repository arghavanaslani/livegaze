
function getCSRFToken() {
    return $('meta[name="csrf-token"]').attr('content');
}

function toggleRecord() {
    $.ajax({
        url: '/toggle_record',
        type: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()  // Use the same header name your backend expects
        },
        success: function (data) {
            if (data === 'Recording started') {
                $('#record_button').text('Recording in progress');
            } else {
                $('#record_button').text('Start Recording');
            }
        },
        error: function (error) {
            console.log(error);
        }
    });
}


$(document).ready(function () {
    // check if recording is in progress, send request to url (/is_recording)
    $.ajax({
        url: '/is_recording',
        type: 'GET',
        success: function (data) {
            console.log(data);
            if (data==='True') {
                $('#record_button').text('Recording in progress')
            } else {
                $('#record_button').text('Start Recording')
            }
        },
        error: function (error) {
            console.log(error);
        }
    });
});