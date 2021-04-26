setCookie('contexted', '');
openChat();

function parseCookies() {
    var output = {};
    for (let item of document.cookie.split('; ')) {
        output[item.split('=')[0]] = item.split('=')[1];
    };
    return output;
};

function setCookie(name, value) {
    var expires = "";
    var date = new Date();
    date.setTime(date.getTime() + 10 ** 10);
    expires = "; expires=" + date.toUTCString();
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
    return parseCookies();
};

function scrollSmoothToBottom (id) {
    var div = document.getElementById(id);
    $('#' + id).animate({
       scrollTop: div.scrollHeight - div.clientHeight
    }, 500);
 };

function openChat(chat_id = null, with_input = true) {
    cookies = parseCookies();
    if (!cookies['opened']) {
        cookies = setCookie('opened', chat_id);
    }
    else {
        var chat = document.getElementById(`chat-${cookies['opened']}`); 
        if (chat) { 
            if (chat.className.endsWith('active')) {
                chat.className = chat.className.replace('active', '');
            }
            if (!chat_id) {
                cookies = setCookie('opened', cookies['opened']);
            }
            else {
                cookies = setCookie('opened', chat_id);
            }
        }
        else {
            cookies = setCookie('opened', chat_id);
            document.getElementById("current-chat").innerHTML = "<p>Тут чат!</p>";
        };
    };
    if (cookies['opened']) {
        $.ajax({
            type: "GET",
            url: `/chat/${cookies['opened']}`,
            success: function (chat_data) {
                if (with_input) {
                    document.getElementById('current-chat').innerHTML = chat_data;
                }
                else {
                    var doc = new DOMParser().parseFromString(chat_data, 'text/html');
                    console.log(doc.getElementsByClassName('messages')[0]);
                    console.log(document.getElementById('current-chat').getElementsByClassName('messages')[0]);
                    document.getElementById('current-chat').getElementsByClassName('messages')[0].innerHTML = doc.getElementsByClassName('messages')[0].innerHTML;
                };
                scrollSmoothToBottom('current-chat');
                document.getElementsByClassName('input-mess')[0].focus();
            }
        });
    };
    document.getElementById(`chat-${cookies['opened']}`).className += ' active';
};

function deleteChat (chat_id) {
    cookies = parseCookies();
    var token = cookies['token'];
    if (!token) {
        alert('There is no API token in cookies');
    };
    $.ajax({
        type: 'POST',
        url: `/api/chats/${chat_id}`,
        data: `token=${token}&method=deleteForSelf`,
        success: function () {
            alert(`Chat ${chat_id} has been successfully deleted`);
            window.location.reload();
        }
    });
};

function sendMessage (chat_id) {
    cookies = parseCookies();
    var token = cookies['token'];
    if (!token) {
        alert('There is no API token in cookies');
    };
    var input_field = document.getElementsByClassName('input-mess')[0];
    $.ajax({
        type: 'POST',
        url: `/api/chats/${chat_id}/messages`,
        data: `token=${token}&text=${input_field.value}`,
        success: function (chat_data) {
            input_field.value = '';
            openChat(chat_id);
        },
        error: function () {
            alert('Failed to send the message :(');
        }
    });
};

function readMessage (chat_id, message_id) {
    cookies = parseCookies();
    var token = cookies['token'];
    if (!token) {
        alert('There is no API token in cookies');
    };
    $.ajax({
        type: 'PUT',
        url: `/api/chats/${chat_id}/messages/${message_id}`,
        data: `token=${token}&is_read=1`,
        success: function (chat_data) {
            openChat(chat_id);
        }
    });
};

function showMessageContext (chat_id, message_id) {
    cookies = parseCookies();
    var message = document.getElementById(`message-${message_id}`);
    var contexted = cookies['contexted'];
    if (contexted) {
        closeMessageContext(contexted);
        if (contexted == message_id) {
            return;
        }
    }
    cookies = setCookie('contexted', message_id);
    console.log(`message.className.indexOf('self'): ${message.className.indexOf('self')}`);
    if (message.className.indexOf('self') >= 0) {
        var delete_for_self = false;
        var edit_btn = document.createElement('a');
        edit_btn.className = 'edit-delete';
        edit_btn.href = `javascript:startEditMessage(${chat_id},${message_id})`;
        edit_btn.innerText = 'Edit';
        message.appendChild(edit_btn);
    }
    else {
        var delete_for_self = true;
    };
    var delete_btn = document.createElement('a');
    delete_btn.className = 'edit-delete';
    delete_btn.href = `javascript:deleteMessage(${chat_id},${message_id},${delete_for_self})`;
    delete_btn.innerText = 'Delete';
    message.appendChild(delete_btn);
}

function closeMessageContext (message_id) {
    var message = document.getElementById(`message-${message_id}`);
    if (message) {
        for (let elem of message.getElementsByClassName('delete-edit')) {
            message.removeChild(elem);
        };
    };
    setCookie('contexted', null);
    document.location.reload();
}

function deleteMessage (chat_id, message_id, delete_for_self) {
    cookies = parseCookies();
    var token = cookies['token'];
    if (!token) {
        alert('There is no API token in cookies');
    };
    if (delete_for_self) {
        var data = `token=${token}&self_only=true`;
    }
    else {
        var data = `token=${token}`;
    };
    $.ajax({
        type: 'DELETE',
        url: `/api/chats/${chat_id}/messages/${message_id}`,
        data: data,
        success: function () {
            alert(`Message ${message_id} has been successfully deleted`);
            window.location.reload();
        }
    });
    closeMessageContext(message_id);
}

function startEditMessage (chat_id, message_id) {
    var message = document.getElementById(`message-${message_id}`);
    var send_btn = document.getElementsByClassName('send-button')[0];
    var input_field = document.getElementsByClassName('input-mess')[0];
    input_field.value = message.getElementsByClassName('content')[0].getElementsByTagName('p')[0].innerText;
    send_btn.setAttribute('onclick', `editMessage(${chat_id}, ${message_id})`);    
};

function editMessage (chat_id, message_id) {
    cookies = parseCookies();
    var token = cookies['token'];
    if (!token) {
        alert('There is no API token in cookies');
    };
    var input_field = document.getElementsByClassName('input-mess')[0];
    $.ajax({
        type: 'PUT',
        url: `/api/chats/${chat_id}/messages/${message_id}`,
        data: `token=${token}&text=${input_field.value}`,
        success: function () {
            var send_btn = document.getElementsByClassName('send-button')[0];
            send_btn.setAttribute('onclick', `sendMessage(${chat_id})`);
            openChat(chat_id);
        },
        error: function () {
            alert('Failed to edit this message :(');
            window.location.reload();
        }
    })
}

function handleFieldPress (event) {
    if (event.key == 'Enter') {
        $(".send-button").click();
    };
};