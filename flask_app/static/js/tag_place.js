

function  create_tags(){
    var dictionary = new AR.Dictionary("ARUCO");
    var maxInput = dictionary.codeList.length - 1;
    var arucoTag0 = document.getElementById("arucoTag0");
    var arucoTag1 = document.getElementById("arucoTag1");
    var arucoTag2 = document.getElementById("arucoTag2");
    var arucoTag3 = document.getElementById("arucoTag3");
    //var arucoId = {{ aruco_id }
    arucoTag0.innerHTML = dictionary.generateSVG(arucoId);
    arucoTag1.innerHTML = dictionary.generateSVG(arucoId + 1);
    arucoTag2.innerHTML = dictionary.generateSVG(arucoId + 2);
    arucoTag3.innerHTML = dictionary.generateSVG(arucoId + 3);
}


$(document).ready(create_tags)