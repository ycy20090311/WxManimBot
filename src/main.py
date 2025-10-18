import time
import json

from wxbot import Bot
from wxauto import WeChat
from wxauto.msgs import (HumanMessage, FriendTextMessage)
from openai import OpenAI
from os.path import exists
from subprocess import (Popen, PIPE)


timeout: float = 60.0 * 5

bot_name: str = ""
nick_name: str = ""

model: str = ""
base_url: str = ""
api_key: str = ""

system_prompt: str = """
角色:数学和Manim动画专家
任务:根据用户输入的数学问题 返回json对象 {"text":文字回答,"code":manim代码}
要求如下
1.ManimCommunity v0.19.0版本 代码结构应清晰包含必要的导入语句 必须完整可独立运行 场景类名必须始终为Animation 动画逻辑在construct方法中实现 公式必须用MathTex/Tex渲染
2.使用VGroup管理相关对象 使用scale(),next_to,to_edge等方法控制布局避免元素重叠
3.动画步骤间使用wait()添加停顿 使用Write,Create,FadeIn等合适动画效果
4.若画面元素过多 确保保留关键元素 避免公式和图像重叠
5.必须返回json对象 格式{"text":文字回答,"code":manim代码}
6.代码应稳定能运行 不使用任何注释 紧凑简洁
"""


client = OpenAI(
    api_key = api_key,
    base_url = base_url,
)

def call_model(p_prompt: str) -> dict:
    response = client.chat.completions.create(
        model = model,
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": p_prompt}
        ],
        response_format = {
            "type": "json_object" 
        },
        temperature=0.0,
        stream = False
    )
    return json.loads(response.choices[0].message.content)

def call_manim(id: str, code: str) -> None:
    script_path = get_script_path(id)
    with open(script_path, "wb+") as script:
        script.write(code.encode())
    
    process = Popen(["manim", "-ql", script_path, "Animation"], stdout = PIPE, stderr = PIPE)
    out, err = process.communicate(timeout = timeout)

def get_script_path(id: str) -> None:
    return f"scripts/{id}.py"

def get_video_path(id: str) -> None:
    return f"media/videos/{id}/480p15/Animation.mp4"

def is_at_msg(msg: HumanMessage) -> bool:
    try:
        parts = msg.content.split('\u2005', 1)
        return (parts[0] == f"@{bot_name}")
    except:
        return False


class ManimBot(Bot):

    def _callback(self, message, chat):
        try:
            if (isinstance(message, FriendTextMessage) and is_at_msg(message)):
                parts = message.content.split('\u2005', 1)
                user_content = parts[1]
                print(f"{chat.who}: {user_content}")

                reply = call_model(user_content)
                print(f"reply: {reply}")

                call_manim(message.id, reply["code"])

                time.sleep(2)
                video_path = get_video_path(message.id)
                if (exists(video_path)):
                    self.send_file(video_path, chat.who)
                    self.quote(message, reply["text"])

                else:
                    self.quote(message, f"{reply['text']} \n\n call_manim error")


        except:
            self.quote(message, "wxbot.Bot._callback error")


if __name__ == "__main__":
    wx = WeChat()
    bot = ManimBot(wx, nick_name)
    bot.run()