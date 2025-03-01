# MCDR_chat_with_ai
DeepSeek API恢复正常后，便尝试编写一个MCDR插件，使MC服务器能够接入DeepSeek
使用了openai库，所以只需要对源码稍加改动即可适配GPT系列ai。如果你使用的是DeepSeek API，只需要在源码中填入你的API KEY即可
将插件放入 `plugins` 文件夹下加载插件即可
使用方法：
主命令 `!!dsp`
- `help`查看帮助
- `history`查看历史对话
- `clear`清空历史对话
- `<message>`如果不是前面三条指令，那么便会向AI发送信息

代码写的比较粗糙，还请大佬轻点喷
