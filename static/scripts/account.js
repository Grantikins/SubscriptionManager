const nameBut = document.getElementById("nameButton")
const emailBut = document.getElementById("emailButton")
const passBut = document.getElementById("passwordButton")
var submitButton = null
var cancelButton = null

function cancelEdit(fieldID, fieldValue){
    var field = document.getElementById(fieldID)
    var newID = ""
    switch (fieldID){
        case "name": 
            newID = "nameButton" 
        break
        case "email": 
            newID = "emailButton"
        break
        case "password": 
            newID = "passwordButton"
        break
    }

    field.innerHTML = `<p>
        ${fieldValue}
        <button class="btn btn-link tooltip" data-tooltip="Edit" id="${newID}">
            <i class="icon icon-edit"></i>
        </button>
    </p>`
    var newBut = document.getElementById(newID)
    newBut.addEventListener("click", function(){
        replaceWithForm(fieldID)
    })

    document.getElementById("nameButton").removeAttribute("disabled")
    document.getElementById("emailButton").removeAttribute("disabled")
    document.getElementById("passwordButton").removeAttribute("disabled")
}

function replaceWithForm(fieldID){
    var field = document.getElementById(fieldID)
    var fieldValue = field.innerText
    var type = ""

    switch (fieldID){
        case "name": 
            type = "text" 
            document.getElementById("emailButton").setAttribute("disabled", true)
            document.getElementById("passwordButton").setAttribute("disabled", true)
        break
        case "email": 
            type = "email"
            document.getElementById("nameButton").setAttribute("disabled", true)
            document.getElementById("passwordButton").setAttribute("disabled", true)
        break
        case "password": 
            type = "password"
            document.getElementById("nameButton").setAttribute("disabled", true)
            document.getElementById("emailButton").setAttribute("disabled", true)
        break
    }
    
    field.innerHTML = `<form class='form-group form-button-container' action='/account' method='POST'> 
        <input class='form-input' type='${type}' name=${fieldID}Value placeholder='${fieldValue}'></input> 
        <button class='btn btn-link tooltip' data-tooltip='Submit' type='submit' id='submitButton'><i class='icon icon-check'></i></button> 
        <button class='btn btn-link tooltip' data-tooltip='Cancel' id='cancelButton${fieldID}' type='button'><i class='icon icon-cross'></i></button> 
    </form>`
    cancelButton = document.getElementById(`cancelButton${fieldID}`)
    cancelButton.addEventListener("click", function(){
        cancelEdit(fieldID, fieldValue)
    })

}


nameBut.addEventListener("click", function(){
    replaceWithForm("name")
})

emailBut.addEventListener("click", function(){
    replaceWithForm("email")
})

passBut.addEventListener("click", function(){
    replaceWithForm("password")
})