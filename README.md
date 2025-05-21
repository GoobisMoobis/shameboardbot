# shameboardbot
A bot for the [Cephalo](https://discord.gg/cephalo) discord server's shame board
## Want to deploy the bot for yourself?
There are many different ways to deploy this as a fully-working bot. The way the bot is built is to be used on **[Render](https://render.com)**, and so is some of the python. However, feel free to edit as needed, and use a different service!
**Please read these instructions if you are setting up the bot on your own**
### First, create the bot
**Step 1:** Create an application on the [discord developer portal](https://discord.com/developers/applications)

**Step 2:** Click bot on the left sidebar and add bot

**Step 3:** click reset token. **Copy this and put it somewhere safe. You will never be shown it again. If anyone gets your token your bot is at risk!**

**Step 4:** scroll to privileged gateway intents

**Step 5:** enable message content intent, server members intent, and presence intent.

### How to invite your bot
To invite your bot, use this link: https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&scope=bot&permissions=268446736

replace YOUR_CLIENT_ID with the client ID of your bot, found in OAuth2 -> general and copy the client id

**now it just needs deployed!**
### Steps for Render
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/YOUR_USERNAME/YOUR_REPO_NAME)

^ If this doesnt work, try the steps below
**Step 1:** fork this repository

**Step 2:** go to render and make an account

**Step 3:** go to new -> web service

**Step 4:** connect the forked repo

**Step 5:** select:
- Runtime: Python
- Build command: pip install -r requirements.txt
- Start command: python bot.py

**Step 6:** Choose free plan

**Step 7:** click to create the web service
if you have any questions, DM me on discord, justa_person8888
