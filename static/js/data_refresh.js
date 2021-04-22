var eventSource = new EventSource("/listen");
eventSource.addEventListener("new-message", function(event) {
    output = "";
    let data = JSON.parse(event.data);
    let chat_list = document.getElementById("chat-list")
    for (let div of chat_list.children) {
        chat_list.removeChild(div);
    }
    for (let chat of data) {
        elem = document.createElement('div');
        elem.className = 'alert alert-success';
        elem.innerText = chat['title'];
        chat_list.appendChild(elem);
    }
    });