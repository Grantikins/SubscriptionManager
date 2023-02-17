let date = new Date()

async function getSubscriptionData(){
    userid = document.getElementsByName("userid")[0].getAttribute("value")
    data = await fetch(window.location.origin + `/api/user/${userid}`).then(response => response.json())
    return data
}

async function getPaymentData(id, year=date.getFullYear(), month=date.getMonth()){
    data = await fetch(window.location.origin + `/api/subscription/${id}/payment-days-in-month/${year}/${month+1}`).then(response => response.json())
    return data
}

async function prepareData(data, year=date.getFullYear(), month=date.getMonth()){
    let payDates = {}

    const promises = data.subscriptions.map(async function(sub){
        if(sub.startDate != null && sub.timeBetweenPayments != null){
            let dateList = await getPaymentData(sub.id, year, month)
            if(dateList){
                for(i = 0; i < dateList.length; i += 1){
                    if(!payDates.hasOwnProperty(dateList[i].slice(5, 7).trim()))
                        payDates[dateList[i].slice(5, 7).trim()] = []
                    payDates[dateList[i].slice(5, 7)].push(sub.serviceName)
                }
            }
        }
    })

    await Promise.all(promises)

    return payDates
}

async function updateMonthDays(year, month){
    data = await fetch(window.location.origin + `/api/subscription/${year}/${month + 1}`).then(response => response.json())
    calendar = document.getElementById("calendar-body")
    calendar.innerHTML = ``
    for(i = 0; i < data.length; i += 1){
        let date = new Date(data[i])
        
        dateElement = ``
        if(date.getUTCMonth() === month){
            dateElement = `<div class='calendar-date text-center' name='calendar-date' >
                <button class='date-item'>${data[i].slice(5, 7)}</button>
            </div>`
        } else{
            dateElement = `<div class='calendar-date text-center prev-month' name='calendar-date'>
                <button class='date-item'>${data[i].slice(5, 7)}</button>
            </div>`
        }
        calendar.innerHTML += dateElement
    }
}

function updateCalendar(payDates){
    document.getElementsByName("calendar-date").forEach(function(dateElement){
        if(payDates[dateElement.innerText] && !dateElement.getAttribute("class").includes("prev-month")){
            dateElement.setAttribute("class", "calendar-date text-center tooltip")
            tooltip = "You have payment(s):"
            for(let i = 0; i < payDates[dateElement.innerText].length; i += 1){
                tooltip += ` ${payDates[dateElement.innerText][i]}`
            }
            dateElement.setAttribute("data-tooltip", tooltip)
            dateElement.children[0].setAttribute("class", "date-item badge")
        } else if(!dateElement.getAttribute("class").includes("prev-month")){
            dateElement.setAttribute("class", "calendar-date text-center")
            dateElement.setAttribute("data-tooltip", "")
            dateElement.children[0].setAttribute("class", "date-item")
        }
    })
}

async function fixCalendar(){
    let data = await getSubscriptionData()
    let preparedData = await prepareData(data)
    updateCalendar(preparedData)
}

async function changeCalendarMonth(monthChange){
    currentDate = document.getElementsByName("calendar-title")[0].getAttribute("value")
    desiredDate = new Date(currentDate)
    desiredDate.setMonth(desiredDate.getMonth() + monthChange)
    document.getElementsByName("calendar-title")[0].setAttribute("value", desiredDate)
    document.getElementsByName("calendar-title")[0].innerText = desiredDate.toLocaleDateString("en-US", {month: "long", year: "numeric"})
    let data = await getSubscriptionData()
    let preparedData = await prepareData(data, desiredDate.getFullYear(), desiredDate.getMonth())
    await updateMonthDays(desiredDate.getFullYear(), desiredDate.getMonth())
    updateCalendar(preparedData)
}

document.getElementsByName("calendar-right-button")[0].addEventListener("click", function(){changeCalendarMonth(1)})
document.getElementsByName("calendar-left-button")[0].addEventListener("click", function(){changeCalendarMonth(-1)})

fixCalendar()

const calendarBox = document.getElementById("calendarBox")
const statBox = document.getElementById("statBox")

statBox.style.height = getComputedStyle(calendarBox).height
