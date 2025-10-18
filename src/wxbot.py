from wxauto import WeChat
from wxauto.wx import Chat
from wxauto.msgs import HumanMessage


class Bot:

    wx: WeChat = None
    nickname: str = None
    
    def __init__(self, p_wx: WeChat, p_nickname: str):
        self.wx = p_wx
        self.nickname = p_nickname

    def quote(self, p_msg: HumanMessage, p_text: str):
        p_msg.quote(p_text)

    def send_file(self, p_path: str, p_who: str):
        self.wx.SendFiles(p_path, p_who)

    def _callback(self, message: HumanMessage, chat: Chat):
        pass

    def run(self):
        self.wx.AddListenChat(nickname = (self.nickname), callback = (self._callback))
        self.wx.KeepRunning()

    

