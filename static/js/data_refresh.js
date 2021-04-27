var eventSource = new EventSource("/listen");
eventSource.addEventListener("new-message", function(event) {
    let data = JSON.parse(event.data);
    let chat_list = document.getElementById("chat-list");
    while (chat_list.firstChild) {
        if (chat_list.lastChild.tagName != 'A') {
            chat_list.removeChild(chat_list.lastChild);
        }
        else {
            break;
        };
    };
    for (let chat of data) {
        if (document.getElementById(`chat-${chat['id']}`)) {
            continue;
        };
        elem = document.createElement('button');
        elem.id = `chat-${chat['id']}`;
        elem.className = 'alert alert-info';
        if (!chat['title']) {
            var users = [];
            for (let user of chat['users']) {
                users.push(user['username']);
            }
            var title = users.join(', ');
            if (title.length > 25) {
                title = title.substring(0, 22) + '...';
            };
            elem.innerText = title;
        }
        else {
            elem.innerText = chat['title'];
        }
        elem.style = 'width: 100%;';
        elem.setAttribute('onclick', `openChat(${chat['id']})`);
        chat_list.insertAdjacentElement('beforeend', elem);
    };
    openChat(null, false);
    });
