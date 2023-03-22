async def send_msg(channel, msg):
    max_msgs = (len(msg) // 2000) + 1
    if max_msgs > 1:
        for i in range(max_msgs):
            await channel.send(msg[i*1990:(i+1)*1990] + f" ({i + 1}/{max_msgs})")
    else:
        await channel.send(str(msg))