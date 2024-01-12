import slack
import os

# 假设你已经通过OAuth流程获得了访问令牌
access_token = 'xoxb-306132039189-6370099391207-UbcABQXD2gQOvuZv0kynwxJH'

# 使用OAuth访问令牌初始化Slack客户端
client = slack.WebClient(token=access_token)

# 发送消息到特定的频道
response = client.chat_postMessage(
    channel='#jc_bdbot',
    file="D:/files/random_file/JC_Logo_RGB20002000.png",
    text="image test"
)

# 打印结果
print(response)
