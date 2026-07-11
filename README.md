<p align="center">
  <a href="https://github.com/Unrated-Coder/Unrated-LinkShare-Bot" target="_blank">
    <img src="https://imgyx.pages.dev/Qzjvg" width="100%" style="border-radius: 28px; border: 4px solid #00BFFF; box-shadow: 0 8px 30px rgba(0, 191, 255, 0.4); transition: transform 0.3s ease-in-out;" alt="Unrated-LinkShare-Bot Logo" />
  </a>
</p>

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=30&duration=3000&pause=1000&color=00BFFF&width=550&height=50&lines=Hey+There!+Introducing...;LinkShareBot+%F0%9F%A5%80;The+Most+Advanced+Link+Bot%E2%9D%97%EF%B8%8F" alt="Typing SVG" />
</p>

<p align="center">
  <strong>An ultra-high-performance, native Telegram link sharing and channel management engine powered by Pyrogram.</strong>
</p>

<p align="center">
  <a href="https://t.me/Unrated_Coder"><img src="https://img.shields.io/badge/Developer-@Unrated__Coder-orange?style=flat-square&logo=telegram&logoColor=white" /></a>
  <a href="https://t.me/Unrated_Coder"><img src="https://img.shields.io/badge/Updates-Telegram-blue?style=flat-square&logo=telegram&logoColor=white" /></a>
  <img src="https://img.shields.io/badge/Language-Python-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Framework-Pyrogram-9B30FF?style=flat-square&logo=telegram" />
</p>

<hr style="border: 0; height: 1px; background: linear-gradient(to right, rgba(0, 191, 255, 0), rgba(0, 191, 255, 0.75), rgba(0, 191, 255, 0)); margin: 30px 0;" />

## 📌 Table of Contents
- [🌟 Overview](#-overview)
- [⚡ Core Capabilities](#-core-capabilities)
- [🔄 System Workflow](#-system-workflow)
- [🎮 Command Console](#-command-console)
- [⚙️ Environment Configuration](#-environment-configuration)
- [🛠️ Local Installation](#%EF%B8%8F-local-installation)
- [🐳 Docker Deployment](#%EF%B8%8F-docker-deployment)
- [☁️ Instant Deployment](#%EF%B8%8F-instant-deployment)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🌟 Overview

**LinkShareBot** is an enterprise-grade, high-performance Telegram native automation assistant designed to manage, store, and distribute Telegram channel links seamlessly. 

Powered by **Pyrogram**, it secures your community traffic by automatically generating, monitoring, and revoking invite links. It features advanced utilities like Force Subscription gating, bulk generation pipelines, and automated join-request approval engines.

---

## ⚡ Core Capabilities

*   🌐 **Multi-Channel Indexing** — Register, monitor, and manage unlimited Telegram channels dynamically in a single unified database.
*   🔒 **Secure Auto-Invites** — Generate secure, custom single-use invite links on-the-fly to prevent unauthorized link sharing.
*   ⏱️ **Self-Revoking Links** — Enhanced link protection that automatically revokes and invalidates generated links after 5 minutes.
*   📦 **Bulk Generation** — Mass-generate custom invite links for multiple target channel IDs instantly in a single command execution.
*   📋 **Paginated Navigation** — Smooth, lag-free pagination using inline keyboards for effortless navigation through large channel lists.
*   🔄 **Request Queue Manager** — Direct support for Join Request links with automated request monitoring.
*   🛡️ **Force-Subscribe (FSub)** — Gate bot access by strictly requiring users to join your specified channels or request pools first.
*   📊 **Analytics Dashboard** — Live system diagnostics, total active users, and database analytics at your fingertips.

---

## 🔄 System Workflow

```text
┌────────────────┐       ┌──────────────────────┐       ┌─────────────────┐
│  User Joins    │ ───► │  Force Sub Check     │ ───► │ Request Approved│
│  Via Link      │       │  (Database Verified) │       │ (Auto or Timer) │
└────────────────┘       └──────────────────────┘       └─────────────────┘
                                    │                             │
                                    ▼                             ▼
                         ┌──────────────────────┐       ┌─────────────────┐
                         │  Access Restricted   │       │ Invite Revoked  │
                         │  (Prompts Joining)   │       │ (After 5 Mins)  │
                         └──────────────────────┘       └─────────────────┘
```

---

## 🎮 Command Console

<details>
<summary><b>📅 Channel & Link Management (Admins Only)</b></summary>
<br>

*   `/addch <channel_id>` — Registers a new target channel into the central database.
*   `/delch <channel_id>` — Removes a registered channel from the database.
*   `/channels` — Launches the paginated interactive channel list with inline navigation.
*   `/reqlink` — Displays active join-request links for connected channels.
*   `/links` — Outputs all generated active channels as clean list format.
*   `/bulklink <id1> <id2>` — Mass generates invite links for multiple channels instantly.

</details>

<details>
<summary><b>⏱️ Auto-Approval Engine</b></summary>
<br>

*   `/reqtime` — Sets the custom sleep delay before automatically approving join requests.
*   `/reqmode` — Toggles the Auto Request Approval system state [`ON` / `OFF`].
*   `/approveon` — Enables automated request approval for a specific channel.
*   `/approveoff` — Disables automated request approval for a specific channel.

</details>

<details>
<summary><b>🛡️ Force Subscription (FSub) Gate</b></summary>
<br>

*   `/add_fsub <channel_id> <mode>` — Configures a channel for Force-Sub (Modes: `normal`, `request`).
*   `/fsub` — Lists all channels currently active in the FSub gatekeeper.
*   `/del_fsub <channel_id>` — Disables FSub requirement for a channel.

</details>

<details>
<summary><b>📊 System & Admin Utilities (Admins Only)</b></summary>
<br>

*   `/stats` — Queries total active users, database rows, and subscription analytics.
*   `/status` — Queries live server metrics, CPU usage, RAM utilization, and uptime.
*   `/broadcast` — Dispatches a global push notification to all registered bot users.

</details>

---

## ⚙️ Environment Configuration

Setup these variables inside your hosting platform environment configuration:

```env
# --- Core Bot Credentials ---
API_ID=your_api_id
API_HASH=your_api_hash
TG_BOT_TOKEN=your_bot_token

# --- Access Control & Moderation ---
OWNER_ID=your_owner_id
ADMINS=admin_ids_space_separated

# --- Database & Storage ---
DB_URL=your_mongodb_url
DB_NAME=Links-Share
DATABASE_CHANNEL=your_log_channel_id

# --- Web Server Port ---
PORT=8080
```

---

## 🛠️ Local Installation

Follow these steps to deploy a development instance of the bot locally:

### Prerequisites
- Python 3.10 or higher
- MongoDB (running instance)
- Git installed on your system

```bash
# 1. Clone the repository
git clone https://github.com/Unrated-Coder/Unrated-LinkShare-Bot.git
cd Unrated-LinkShare-Bot

# 2. Initialize a Python Virtual Environment
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# 3. Install required library dependencies
pip3 install -r requirements.txt

# 4. Configure environmental keys
cp sample_config.env .env  # Rename and configure values inside .env file

# 5. Start the engine
python3 -m bot
```

---

## 🐳 Docker Deployment

For standardized production hosting, we highly recommend deploying via Docker containerization:

```bash
# Build the Docker image
docker build -t unrated-linkshare-bot .

# Run the container background daemon
docker run -d --name linkshare-bot --env-file .env unrated-linkshare-bot
```

---

## ☁️ Instant Deployment

Deploy your custom instance of **LinkShareBot** directly to top cloud hosting platforms with a single click:

| Hosting Provider | Deploy Triggers |
| :--- | :--- |
| **Heroku** | <a href="https://dashboard.heroku.com/new?template=https://github.com/Unrated-Coder/Unrated-LinkShare-Bot" target="_blank"><img src="https://img.shields.io/badge/Deploy--to--Heroku-7056BF?style=for-the-badge&logo=heroku&logoColor=white"/></a> |
| **Koyeb** | <a href="https://app.koyeb.com/deploy?type=git&repository=github.com/Unrated-Coder/Unrated-LinkShare-Bot&branch=main&name=unrated-linkshare-bot" target="_blank"><img src="https://img.shields.io/badge/Deploy--to--Koyeb-1F2937?style=for-the-badge&logo=koyeb&logoColor=white"/></a> |
| **Render** | <a href="https://render.com/deploy?repo=https://github.com/Unrated-Coder/Unrated-LinkShare-Bot" target="_blank"><img src="https://img.shields.io/badge/Deploy--to--Render-46E3B7?style=for-the-badge&logo=render&logoColor=white"/></a> |

---

## 🤝 Contributing

Contributions make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **highly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<p align="center">
  Developed & maintained with ⚡️ by <a href="https://t.me/Unrated_Coder"><b>@Unrated_Coder</b></a> on Telegram
</p>
