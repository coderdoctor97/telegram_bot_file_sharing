# Sharing PDFs Via Standalone HTML - Complete Manual

---

## 1. Project Overview & Core Logic

This project establishes a **secure, serverless, and copyright-safe** file-sharing mechanism. It completely bypasses traditional cloud storage link-sharing by utilizing Telegram as a hidden backend database.

### The Working Pipeline

1. **The Vault**: Files are securely hosted in a Private Telegram Channel.
2. **The Frontend**: A lightweight, static HTML file displays a list of available files using an embedded JSON database.
3. **The Bridge (Deep Linking)**: Users click a "Download" button on the webpage, which redirects them to a Telegram Bot via a deep link containing a unique hidden token (e.g., `t.me/YourBot?start=NEET_PG_Pathology_01`).
4. **The Backend (Bot)**: The Python bot intercepts the `/start` command, extracts the token, looks up the corresponding Message ID in its internal dictionary, and silently copies the file from the Private Channel directly to the user's chat.

---

## 2. Step-by-Step Implementation Guide

### Phase A: Setting Up "The Vault" (Manual Setup)

This is the hidden storage where the actual files live.

1. Open Telegram and create a **Private Channel** (e.g., "My Study Vault").
2. Upload your PDFs or ZIP files directly into this channel.
3. Forward each uploaded file to a bot like `@getidsbot` or use a Telegram client that shows Message IDs to find the exact **Message ID** for each file.
  *Example:* The "Pathology Notes" PDF is uploaded and gets Message ID `105`.

### Phase B: Generating Encoded Tokens (Data Mapping)

Create a unique, non-descriptive token for each file to prevent users from guessing file names or accessing unauthorized files.

- **File 1:** Final Year Surgery Question Bank -> Token: `MBBS_Final_Surgery` -> Message ID: `106`
- **File 2:** Pathology Notes -> Token: `NEET_PG_Pathology` -> Message ID: `105`

### Phase C: Developing the Frontend Skeleton (HTML/JS)

The user interface must be a static, self-contained HTML file.

1. **The JSON Database**: Embed a JSON array directly into the HTML file containing the display titles and the secret tokens.

```json
const fileDatabase = [
  {"title": "Pathology Complete Notes", "token": "NEET_PG_Pathology"},
  {"title": "Surgery Question Bank", "token": "MBBS_Final_Surgery"}
];
```

```python
FILE_MAP = {
    "NEET_PG_Pathology": 105,
    "MBBS_Final_Surgery": 106
}

CHANNEL_ID = "-100XXXXXXXXXX" # Your private channel's ID
```

---

## 3. Hosting & Deployment Suggestions

Which specific hosting platform are you planning to use to keep this bot running 24/7? Options include:

- Render
- PythonAnywhere
- Heroku
- Railway
- Other VPS/Cloud options

---

### The Working Pipeline![image.png](assets/a5b1fb6c-3308-4bb1-8219-b0bf5f8c8b4b.png)

&nbsp;