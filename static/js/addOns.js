let emailPopup = () => {
    console.log("popup")
    popup()
}

let popup = () => {
    $("section").prepend(
        `  
            <div>
                <span onclick="closePopup" id="close-popup">&times;</span>
                <p> Subscribe to our newsletter</p>
                <input type="text" />
            </div>
        `
    )
}



let time = 10000 //In millisec
let intervalId = setInterval(emailPopup, time)   
clearInterval(intervalId)

let closePopup = () => {
    alert("Work")
}