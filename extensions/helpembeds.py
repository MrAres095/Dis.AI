import discord

helpEmbed1 = discord.Embed(title="Commands List (prefix: '/')", description="\nType '/help 2' for page 2'\nType '/help settings' for help with /settings", colour=discord.Colour.blue())
helpEmbed1.set_thumbnail(url='https://github.com/jacobjude/Dis.AI/blob/master/icon.png?raw=true')
helpEmbed1.add_field(name='```/createchatbot```', inline=False,
                        value='Creates a new chatbot with the given name.\nAll settings are initialized to default.\nUse /enablehere (chatbot name) to enable the chatbot in the current channel')

helpEmbed1.add_field(name='```/enablehere (chatbot name)```', inline=False,
                        value="Enables the specified chatbot in the current channel")

helpEmbed1.add_field(name="```/settings```", inline=False,
                value="Change the settings for a specified chatbot\nType '/help settings' to learn about each setting.")

helpEmbed1.add_field(name="`/deletechatbot`", inline=False,
                value="Delete a chatbot")

helpEmbed1.add_field(name="```/disablehere (chatbot name)```", inline=False,
                     value="Disables the specified chatbot from the current channel.")

helpEmbed1.add_field(name="```/clearmessagehistory (chatbotname) <(optional) number of messages to delete >```", inline=False,
                value="Deletes the last given number of messages from the chatbot's memory. To clear all messages, don't enter any number.")

helpEmbed1.add_field(name="```/includeusernames (chatbot name)```", inline=False,
                     value="Allows the specified chatbot to recognize usernames.")

helpEmbed1.add_field(name="```/removeprefix (chatbot name)```", inline=False,
                     value="Removes the selected prefixes from the specified chatbot\nSee '/help settings' for details on prefixes.")

helpEmbed1.add_field(name="```/listchatbots```", inline=False,
                     value="Lists all created chatbots")

helpEmbed1.add_field(name="```/showenabledhere```", inline=False,
                value="Shows all chatbots that are enabled in the current channel.")

helpEmbed1.add_field(name="```/chatbotinfo (chatbot name)```", inline=False,
                value="Shows all settings for the specified chatbot")

helpEmbed1.add_field(name="```/setdefault (chatbot name)```", inline=False,
                value="Resets all settings for the specified chatbot to default")




helpEmbed2 = discord.Embed(title="/settings help", description="", colour=discord.Colour.blue())
helpEmbed2.set_thumbnail(url='https://github.com/jacobjude/Dis.AI/blob/master/icon.png?raw=true')
helpEmbed2.add_field(name="```Prompt```", inline=False,
                value="Changes the prompt of the selected chatbot. This is the heart of Dis.AI. Great prompting yields great results.")

helpEmbed2.add_field(name="```Insert Message```", inline=False,
                value="Manually inserts the given message into the chatbot's message history. Possible role inputs:\n'user' role simulates a user message\n'assistant' role simulates a chatbot message\n'system' role simulates a system message (like prompt)")

helpEmbed2.add_field(name="```Temperature```", inline=False,
                value="A value between 0 and 2 that modifies 'randomness' of the output. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.\n")

helpEmbed2.add_field(name="```Presence Penalty```", inline=False,
                value="Positive values penalize new tokens based on whether they appear in the text so far, increasing the chatbot's likelihood to talk about new topics. Number between -2 and 2.")

helpEmbed2.add_field(name="```Frequency Penalty```", inline=False,
                value="Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the chatbot's likelihood to repeat the same line verbatim. Number between -2.0 and 2.0.")

helpEmbed2.add_field(name="```Add prefix```", inline=False,
                     value="Adds a prefix to the specified chatbot. If a prefix is added, then the chatbot will only respond to a message if it starts with one of its prefixes. Multiple prefixes can be added. Useful if you only want the chatbot to respond on certain occassoins.")

helpEmbed2.add_field(name="```Max Tokens```", inline=False,
                value="Sets maximum output tokens of the specified chatbot to the given value\nOne token is about 4 characters.")

helpEmbed2.add_field(name="```Message History Length```", inline=False,
                value="The maximum number of messages the chatbot can store in memory. Higher values may use more tokens.\n")

helpEmbed2.add_field(name="```Prompt Reminder Interval```", inline=False,
                value="The interval in which to remind the chatbot of its prompt. Lower this to increase the strength of the prompt. Experiment with this if the strength of the prompt weakens. Set to 0 to disable.")

helpEmbed2.add_field(name="```Top P```", inline=False,
                value="An alternative to temperature. It's generally recommended to alter this or temperature, but not both")

helpEmbed3 = discord.Embed(title="Commands List (page 2)", description="", colour=discord.Colour.blue())
helpEmbed3.set_thumbnail(url='https://github.com/jacobjude/Dis.AI/blob/master/icon.png?raw=true')

helpEmbed3.add_field(name="```/addadminrole```", inline=False,
                value="Specify admin roles. Only admin roles can use Dis.AI commands. If no roles are added, then only the owner of the server can use commands.")

helpEmbed3.add_field(name="```/removeadminrole```", inline=False,
                value="Removes admin role (see above for explanation)")

helpEmbed3.add_field(name="```/addallowedrole```", inline=False,
                value="Adds allowed roles. Chatbots will only respond to a user of they have an allowed role. If no allowed roles are added, then chatbots will respond to all users by default.")

helpEmbed3.add_field(name="```/removeallowedrole (chatbot name)```", inline=False,
                value="Removes allowed role. (See above for explanation)")


help_embeds = [helpEmbed1, helpEmbed2, helpEmbed3]

