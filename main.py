from astrbot.api.provider import ProviderRequest
from astrbot.api.provider import LLMResponse
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.all import *
from astrbot.api.message_components import *
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
    # 确保使用正确的正则表达式来匹配 [笑] 这样的表情
    matches = matches = re.findall(r'\[(.)]', inpt)
    
    if not matches:
        # 尝试打印输入文本以帮助调试
        print("No matching emotion found in text.")
        return None
    
    emotion = matches[0]  # 获取第一个匹配的表情
    
    emotion_to_folder = {
        '怒': ('anger', 'anger_'),
        '笑': ('laugh', 'laugh_'),
        '悲': ('sad', 'sad_'),
        '哭': ('cry', 'cry_'),
        '惊': ('shock', 'shock_')
    }
    
    if emotion in emotion_to_folder:
        folder, prefix = emotion_to_folder[emotion]
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", folder)
        file = get_random_image(path, prefix)
        file_path = os.path.join(path, file)
        return file_path
    else:
        print(f"Unsupported emotion: {emotion}")
        return None
    

@register("astrbot_plugin_better_facebread", "xiewoc", "使llm在返回消息时能发送表情包", "1.0.1", "repo url")
class astrbot_plugin_better_facebread(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.on_llm_request()
    async def on_llm_req(self, event: AstrMessageEvent, req: ProviderRequest): # 请注意有三个参数
        req.system_prompt += "请在文本末尾加入[怒][笑][悲][哭][惊]其中之一以表达情感，如果没有可以不加"

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent):
        result = event.get_result()
        chain = result.chain
        print(chain)
        texts = []
        for item in chain:
            if isinstance(item, Plain):
                texts.append(item.text.strip())
            elif isinstance(item, str):
                texts.append(item.strip())

        full_text = ' '.join(texts)
        if full_text != '':
            path = match(full_text)
            if path != None:
                chain.append(Image.fromFileSystem(path))
                
    @filter.on_llm_response()#删除[*]
    async def resp(self, event: AstrMessageEvent, response: LLMResponse):
        completion_text = response.completion_text
        cleaned_text = completion_text  
        if r'\[[\u4e00-\u9fa5]\]' in completion_text:
             cleaned_text = re.sub(r'\[[\u4e00-\u9fa5]\]', '', completion_text)
        response.completion_text = cleaned_text
