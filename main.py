from astrbot.api.all import *
import re
import os
import random

def get_random_image(folder_path,start_str):#eg. startswith("laugh_")
    # 筛选出符合条件的文件列表
    valid_extensions = ('.jpg', '.png')
    images = [f for f in os.listdir(folder_path) if f.startswith(start_str) and f.endswith(valid_extensions)]
    
    if not images:
        return "No matching images found."
    
    # 随机选择一个图片文件
    chosen_image = random.choice(images)
    
    return chosen_image

def match(inpt):
    matches = re.findall(r'$[\w\u4e00-\u9fff]+$', inpt)
    if matches == '[怒]':
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"images","anger")
        file = get_random_image(path,"anger_")
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"images","anger",file)
        return file_path
    elif matches == '[笑]':
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"images","laugh")
        file = get_random_image(path,"laugh_")
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"images","laugh",file)
        return file_path
    elif matches == '[悲]':
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"images","sad")
        file = get_random_image(path,"sad_")
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"images","sad",file)
        return file_path
    elif matches == '[哭]':
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"images","cry")
        file = get_random_image(path,"cry_")
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"images","cry",file)
        return file_path
    elif matches == '[惊]':
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"images","shock")
        file = get_random_image(path,"shock_")
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"images","shock",file)
        return file_path
    else:
        return None
    

@register("astrbot_plugin_better_facebread", "xiewoc", "使llm在返回消息时能发送表情包", "0.0.1", "repo url")
class astrbot_plugin_better_facebread(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.on_llm_request(priority=1)
    async def on_llm_req(self, event: AstrMessageEvent, req: ProviderRequest): # 请注意有三个参数
        print(req) # 打印请求的文本
        req.system_prompt += "请在文本末尾加入[怒][笑][悲][哭][惊]其中之一以表达情感，如果没有可以不加。"

    @filter.on_llm_response()
    async def on_llm_resp(self, event: AstrMessageEvent, resp: LLMResponse): # 请注意有三个参数
        print(resp)
        resp = re.sub(r'\[\u4e00-\u9fff]', '', resp)
        print(resp)

    @event_message_type(EventMessageType.ALL) # 注册一个过滤器，参见下文。
    async def on_message(self, event: AstrMessageEvent):
        print(event.message_obj.raw_message) # 平台下发的原始消息在这里
        print(event.message_obj.message) # AstrBot 解析出来的消息链内容

    @filter.on_decorating_result(priority=1)
    async def on_decorating_result(self, event: AstrMessageEvent):
        result = event.get_result()
        chain = result.chain
        print(chain) # 打印消息链
        chain.append(Imange.fromFileSystem())
