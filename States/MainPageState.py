from States.BaseState import BaseState
from States.CreateChatState import CreateChatState
from States.CreateGroupState import CreateGroupState
from States.ShowChatState import ShowChatState
from States.ShowContactsState import ShowContactsState
from States.ShowGroupState import ShowGroupState
import time


class MainPageState(BaseState):
    def __init__(self, r, userId):
        self.userId = userId
        self.r = r

    def process(self):
        chatids = self.r.zrevrange(self.userId + ':chatslist', 0, 10)

        if len(chatids) == 0:
            print('Your chats list is empty.')
            print('\n')
        else:
            for i, id in enumerate(chatids):
                id = id.decode('ascii')
                if id.startswith('PV'):
                    splitted = id.split(':')
                    name = splitted[2] if splitted[1] == self.userId else splitted[1]
                    name = self.r.hget(name, 'name').decode('ascii')
                else:
                    name = 'G\t' + self.r.hget(id, 'name').decode('ascii')
                t = self.r.get(self.userId+':'+id+':lastSeen')
                chatLastSeen = int(t.decode('ascii') if t else '0')
                unreadCount = str(self.r.zcount(
                    id+':messages', chatLastSeen, time.time()*1000))
                print(i + 1, name, (unreadCount +
                                    ' New') if not unreadCount == '0' else '')

        print('\n\n:create chat: to start a new chat')
        print(':create group: to make a new group')
        print(':contacts: contacts list')
        print(':open ##: view messages of the specified ##')
        selection = input('Enter command > ')

        if selection == 'create chat':
            return CreateChatState(self.r, self.userId)
        elif selection == 'create group':
            return CreateGroupState(self.r, self.userId)
        elif selection == 'contacts':
            return ShowContactsState(self.r, self.userId)
        elif selection.startswith('open'):
            cmd = selection.split(' ')
            idx = int(cmd[1]) - 1
            if chatids[idx].decode('ascii').startswith('PV'):
                return ShowChatState(self.r, self.userId, chatids[idx].decode('ascii'))
            elif chatids[idx].decode('ascii').startswith('GP'):
                return ShowGroupState(self.r, self.userId, chatids[idx].decode('ascii'))

        return MainPageState(self.r, self.userId)
