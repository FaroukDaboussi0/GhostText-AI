# 👻 GhostText AI – Instant Chat-Friendly AI Writer for Any Language and Website
## 🔍 What is it?
GhostText AI is a browser extension that brings AI rewriting, translation, and tone correction directly into any text field — Gmail, Twitter, Google Docs, chat tools, and more.

It’s like having a personal ghostwriter that rewrites or translates text instantly, without leaving the page.

It operates like an AI "ghostwriter" inside your browser, offering you real-time rewriting and translation at the click of a button.

![Demo of GhostText AI](demo.gif)

## 👥 Who Is This For?
This tool is ideal for:

- 💬 Customer Support Agents – Fix grammar, improve tone, or translate replies instantly.

- 🌍 International Web Creators – Write clean, clear English from mixed-language input.

- ⚡ Remote Professionals & Freelancers – Chat faster and smarter in multilingual environments.


# 🚀 Why Use GhostText Enhancer?
- ✅ Real-Time Editing – Rewrite, translate, or polish your writing inside any website.

- 🔧 Fully Configurable – Choose your tone, language, and rewrite style.

- 🌐 Works Everywhere – Gmail, Notion, LinkedIn, CMS tools, chat platforms…

- 🔁 One-Click Undo – Made a mistake? Roll back in one click.

## 🧰 Setup Instructions
### ✅ Prerequisites
Install Docker on Windows using this official guide:
👉 https://tecadmin.net/installing-docker-on-windows/

Make sure:

- Docker is installed and running

- WSL 2 is properly enabled (usually covered in the Docker guide)

### 🔧 Project Setup (Step-by-Step)
- Open your terminal (Command Prompt / PowerShell)

-   Install Git (if not already installed):

```bash
winget install --id Git.Git -e
Clone the repository:
```
```bash
git clone https://github.com/your-username/ghosttext-enhancer.git
```
Navigate into the project folder:

```bash
cd ghosttext-enhancer
```
Start the backend service using Docker:

```bash
docker-compose up -d
```
### 🧩 Load the Chrome Extension
- Open Google Chrome

- Go to:

```arduino
chrome://extensions/  
```
- Enable Developer mode (toggle at the top right)

- Click “Load unpacked”

- Select the chrome-extension/ folder from the repo

✅ Done! You should now see 3 floating icons (Generate, Undo, Settings) when focusing any editable input field in your browser.

## 📞 Need Help?
Feel free to open an issue or contact the maintainer if you need help setting it up!