var eventSource = new EventSource("/listen")
eventSource.addEventListener("new-message", function(event) {
    document.getElementById("count").innerText = JSON.parse(event.data)
})