<p align="center">
  <img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" />
</p>

<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="https://telegra.ph/file/64d61b1f3933fbc18925e-4ba9274225dadacc17.jpg" width="90px" style="border-radius: 50%;" />
      </td>
      <td>
        <img src="https://readme-typing-svg.herokuapp.com?color=00BFFF&width=600&lines=Hey+There,+This+is+LinkShareBot+%F0%9F%A5%80+%E2%9D%97%EF%B8%8F" />
      </td>
    </tr>
  </table>
</div>

<h1 align="center">
  <img src="https://readme-typing-svg.herokuapp.com?color=FF69B4&width=500&lines=Welcome+to+LinkShareBot;Your+Ultimate+Telegram+Link+Sharing+Bot" />
</h1>

<p align="center">
  <a href="https://t.me/Unrated_Coder">
    <img src="https://img.shields.io/badge/Updates-Telegram-blue?style=for-the-badge&logo=telegram"/>
  </a>
</p>

## 🌟 What is LinkShareBot?

**LinkShareBot** is a modern Telegram bot that allows you to share and manage unlimited Telegram channel links with automatic invite link generation and management. 

Powered by **Pyrogram**, it provides a seamless experience for users to join channels through secure, auto-expiring links. The bot includes advanced features like force subscription, bulk link generation, and request link management.

## 🚀 Features

| 🌟 Feature                | 🔎 Description                              |
| ------------------------- | ------------------------------------------- |
| 📺 Unlimited Channels     | Add and manage unlimited Telegram channels  |
| 🔗 Auto Invite Links      | Generate secure, auto-expiring invite links |
| ⏱️ Auto Revoke            | Links automatically revoke after 5 minutes  |
| 📦 Bulk Generation        | Generate links for multiple channels at once |
| 📋 Pagination Support     | Navigate through large channel lists easily |
| 🔄 Request Links          | Support for join request links              |
| 🛡️ Force Subscription     | Require users to join specific channels     |
| 📊 Bot Statistics         | Monitor bot usage and user statistics       |

## 🛠️ Commands

### Channel & Link Management (Owner/Admins)
- <b>`/addch <channel_id>`</b> — Add a channel to the bot (admin only)
- <b>`/delch <channel_id>`</b> — Remove a channel from the bot (admin only)
- <b>`/channels`</b> — Show all connected channels as buttons (paginated)
- <b>`/reqlink`</b> — Show all request links for channels (paginated)
- <b>`/links`</b> — Show all channel links as text (paginated)
- <b>`/bulklink <id1> <id2> ...`</b> — Generate links for multiple channel IDs at once

- <b>`/reqtime`</b> — Set the auto-approve request timer duration.
- <b>`/reqmode`</b> — Toggle auto request approval mode (ON/OFF).
- <b>`/approveon`</b> — Enable auto request approval for a specific channel.
- <b>`/approveoff`</b> — Disable auto request approval for a specific channel.

### Force Subscription (Owner/Admins)
- <b>`/add_fsub <channel_id> <mode>`</b> — Add a channel to FSub list (modes: `normal`, `request`)
- <b>`/fsub`</b> — See all FSub channels
- <b>`/del_fsub <channel_id>`</b> — Remove a channel from FSub list

### Admin Commands
- <b>`/stats`</b> — Show bot stats (owner only)
- <b>`/status`</b> — Show bot status (admins)
- <b>`/broadcast`</b> — Broadcast a message to all users (admins)

## 🔑 Environment Variables

Below are the required environment variables for deployment.

```env
API_ID=              # Required - Get from https://my.telegram.org
API_HASH=            # Required - From https://my.telegram.org
TG_BOT_TOKEN=        # Required - Get from @BotFather
OWNER_ID=            # Required - Your Telegram user ID
ADMINS=              # Optional - Admin user IDs (space separated)
DB_URL=              # Required - MongoDB connection string
DB_NAME=             # Optional - MongoDB database name (default: Links-Share)
DATABASE_CHANNEL=    # Required - Private channel ID for link storage
PORT=                # Optional - Port for web server (default: 8080)
```

## ☁️ Quick Deploy

| Platform                | Deploy Link                                                                                                                                                                                               |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🌍 **Heroku Deploy**    | <a href="http://dashboard.heroku.com/new?template=https://github.com/yourusername/LinkShareBot"><img src="https://img.shields.io/badge/Deploy%20to-Heroku-purple?style=for-the-badge&logo=heroku"/></a> |
| 🌍 **Koyeb Deploy**     | <a href="https://app.koyeb.com/deploy?type=git&repository=github.com/yourusername/LinkShareBot&branch=main&name=linksharebot"><img src="https://www.koyeb.com/static/images/deploy/button.svg" /></a> |
| 🌍 **Render Deploy**    | <a href="https://render.com/deploy?repo=https://github.com/yourusername/LinkShareBot"><img src="https://render.com/images/deploy-to-render-button.svg" /></a> |

### 🔖 Credits

* <b> *Upgraded by <a href="https://t.me/Unrated_Coder">@Unrated_Coder</a> from Telegram* </b>
