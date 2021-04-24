alert($(function() {
    alert($.session.get("myVar"));
}))

var eventSource = new EventSource("/listen");
eventSource.addEventListener("new-message", function(event) {
    output = "";
    let data = JSON.parse(event.data);
    let chat_list = document.getElementById("chat-list");
    while (chat_list.firstChild) {
        chat_list.removeChild(chat_list.lastChild);
    };
    for (let chat of data) {
        elem = document.createElement('button');
        elem.className = 'alert alert-info';
        elem.innerText = chat['title'];
        elem.style = 'width: 100%;'
        chat_list.insertAdjacentElement('beforeend', elem)
    }
    });