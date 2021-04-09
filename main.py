import os.path

from data import db_session
from data.models.chats import Chat
from data.models.users import User


def main():
    session = db_session.create_session()
    user_zeculesu = session.query(User).filter(User.email == 'zeculesu@yandex.ru').first()
    user_elilcat = session.query(User).filter(User.email == 'elilcatness@gmail.com').first()
    chat = session.query(Chat).first()
    chat.users.append(user_zeculesu)
    print(f'Chat: {chat.title}')
    print(f'user_zeculesu.chats: {[ch.to_dict(only=("id", "title")) for ch in user_zeculesu.chats]}')
    print(f'chat.users: {[user.to_dict(only=("id", "username")) for user in chat.users]}')
    session.merge(chat)
    session.commit()


if __name__ == '__main__':
    db_session.global_init(os.path.join('db', 'vitamo_data.db'))
    main()
