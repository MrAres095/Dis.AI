import discord

helpEmbed1 = discord.Embed(title="Commands List (prefix: 'ai.')", description="Page 1/2 (General Settings")
helpEmbed1.add_field(name='ai.newchat name (ai.nc)', inline=False,
                        value='Creates a new chatbot with the given name. All settings are initialized to default. Use ai.channeladd [chatbot name] to add the created bot to a channel.\n\n\n\n')
helpEmbed1.add_field(name='ai.deletechat [chatbot name] (ai.dc)', inline=False,
                        value="Deletes the specified chatbot")
helpEmbed1.add_field(name="ai.channeladd [chatbot name]", inline=False,
                value="Allows the specified chatbot to read messages and respond in the current channel\n")
helpEmbed1.add_field(name="ai.channelremove [chatbot name]", inline=False,
                     value="Removes the specified chatbot from the channel.")
helpEmbed1.add_field(name="ai.prompt [chatbot name] [prompt]", inline=False,
                value="Sets the prompt of the specified chatbot\n")
helpEmbed1.add_field(name="ai.listbots", inline=False,
                     value="Lists all saved chatbots.")
helpEmbed1.add_field(name="ai.botinfo [chatbot name] (ai.bi)", inline=False,
                     value="Shows all of the settings of the specified chatbot")
helpEmbed1.add_field(name="ai.setdefault [chatbot name]", inline=False,
                     value="Resets the settings of the specified chatbot to default")
helpEmbed1.add_field(name="ai.clearmessagehistory [chatbot name] [number of messages to delete] (ai.cmh)", inline=False,
                value="Deletes the last given number of messages from the chatbot's memory. To clear all messages, don't enter any number.")
helpEmbed1.add_field(name="Type 'ai.help 2' for page 2 (Output Generation Settings)", value="")

helpEmbed2 = discord.Embed(title="Commands List (prefix: '.ai')", description="Page 2/3 (Output Generation Settings)")
helpEmbed2.add_field(name="ai.maxtokens [chatbot name] [value] (ai.mtk)", inline=False,
                value="Sets maximum output tokens of the specified chatbot to the given value\n")
helpEmbed2.add_field(name='ai.temperature [chatbot name] [value] (ai.temp)', inline=False,
                value="A value between 0 and 2 that modifies 'randomness' of the output. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.\n")
helpEmbed2.add_field(name="ai.presencepenalty [chatbot name] [value] (ai.pp)", inline=False,
                value="Positive values penalize new tokens based on whether they appear in the text so far, increasing the chatbot's likelihood to talk about new topics. Number between -2 and 2.")
helpEmbed2.add_field(name="ai.frequencypenalty [chatbot name] [value] (ai.fp)", inline=False,
                value="Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the chatbot's likelihood to repeat the same line verbatim. Number between -2.0 and 2.0.")
helpEmbed2.add_field(name="ai.top_p", inline=False,
                value="An alternative to temperature. It's generally recommended to alter this or temperature, but not both")
helpEmbed2.add_field(name="ai.maxmessagehistorylength (ai.mmhl)", inline=False,
                value="The maximum number of messages the chatbot can store in memory. Higher values may use more tokens.\n")
helpEmbed2.add_field(name="ai.promptreminderinterval (ai.pri)", inline=False,
                value="The interval in which to remind the chatbot of its prompt. Lower this to increase the strength of the prompt.")
helpEmbed2.add_field(name="ai.includeusernames [chatbot name] [true/false] (ai.iu)", inline=False,
                value="Allows the chatbot to recognize usernames.")
helpEmbed2.add_field(name="Type 'ai.help 3' for page 3 (Misc Settings)", value="")


helpEmbed3 = discord.Embed(title="Commands List (prefix: '.ai')", description="Page 3/3 (Misc Settings)")
helpEmbed3.add_field(name="ai.addadminrole [@role]", inline=False,
                     value="Specify admin roles. Only admin roles can use Dis.AI commands. If no roles are added, then only the owner of the server can use 'ai.' commands.")
helpEmbed3.add_field(name="ai.removeadminrole [@role]", inline=False,
                     value="Remove admin roles. These removed roles will no longer be able to use 'ai.' commands.")
helpEmbed3.add_field(name="ai.addallowedrole [@role]", inline=False,
                     value="Adds allowed roles. Chatbots will only respond to a user of they have an allowed role. If no allowed roles are added, then chatbots will respond to all users by default.")
helpEmbed3.add_field(name="ai.removeallowedrole [@role]", inline=False,
                     value="Removes allowed role. (See above for explanation)")
helpEmbed3.add_field(name="ai.addprefix [chatbot name] [prefix]", inline=False,
                     value="Adds a prefix to the specified chatbot. If a prefix is added, then the chatbot will only respond to a message if it starts with a prefix. Multiple prefixes can be added.")
helpEmbed3.add_field(name="ai.removeprefix [chatbot name] [prefix]", inline=False,
                     value="Removes the given prefix from the given chatbot's prefix list. Leave [prefix] blank to remove all prefixes.")
helpEmbed3.add_field(name="ai.insertmessage [chatbot name] [role] [message]", inline=False,
                     value="Manually inserts the given message into the chatbot's message history. Possible role inputs:\n'user' role simulates a user message\n'assistant' role simulates a chatbot message\n'system' role simulates a system message (like prompt)")

help_embeds = [helpEmbed1, helpEmbed2, helpEmbed3]

