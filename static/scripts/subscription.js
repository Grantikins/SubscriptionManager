if(document.getElementById("activate")){
    document.getElementById("activate").addEventListener("click", function(){
        fetch(window.location.origin + document.getElementById("activate").getAttribute("url"), {
            method: "POST"
        }).then(function(response){
            window.location.href = response.headers.get("Location")
        })
    })
}
else{
    document.getElementById("deactivate").addEventListener("click", function(){
        fetch(window.location.origin + document.getElementById("deactivate").getAttribute("url"), {
            method: "POST"
        }).then(function(response){
            window.location.href = response.headers.get("Location")
        })
    })
}

document.getElementById("delete").addEventListener("click", function(){
    const confirmed = confirm("Are you sure you want to delete the subscription?")
    if(confirmed){
        fetch(window.location.origin + document.getElementById("delete").getAttribute("url"), {
            method: "DELETE"
        }).then(function(response){
            window.location.href = response.headers.get("Location")
        })
    }else{
        console.log("Cool, you didn't delete the subscription, and you looked at the console logs. Look at you investigating.")
    }
})

document.getElementById("edit").addEventListener("click", function(){
    location.href = document.getElementById("edit").getAttribute("url")
})