const intervalNum = document.getElementById("intervalNum")
const interval = document.getElementById("interval")

// Set max interval value
interval.addEventListener("change", function(){
    var value = interval.options[interval.selectedIndex].value
    
    if(value == "Choose One" || value == "Year(s)"){
        intervalNum.max = "10"
    } else if(value == "Day(s)"){
        intervalNum.max = "30"
    } else if(value == "Week(s)"){
        intervalNum.max = "4"
    } else if(value == "Month(s)"){
        intervalNum.max = "11"
    }
})


// Set max date
var today = new Date();
var dd = today.getDate();
var mm = today.getMonth() + 1;
var yyyy = today.getFullYear();

if (dd < 10) {
    dd = '0' + dd;
}

if (mm < 10) {
    mm = '0' + mm;
}

today = yyyy + '-' + mm + '-' + dd;
document.getElementById("dateInput").setAttribute("max", today);

