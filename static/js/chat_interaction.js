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
        if (document.getElementById(`chat-${cookies['opened']}`)) { 
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
    }
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

function handleFieldPress (event) {
    if (event.key == 'Enter') {
        $(".send-button").click();
    };
};