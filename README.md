# Chrona

[![AUR](https://img.shields.io/aur/version/chrona-bin?color=gold&label=AUR&logo=arch-linux)](https://aur.archlinux.org/packages/chrona-bin) [![GitHub release](https://img.shields.io/github/v/release/Cypher-Monarch/Chrona?color=black&logo=github)](https://github.com/Cypher-Monarch/Chrona/releases) [![License](https://img.shields.io/github/license/Cypher-Monarch/Chrona?color=gold)](LICENSE)

**Chrona — because silence deserves a voice.**

---

> _“If time could speak, it would sound like this.”_

Chrona transforms your words into sound — fast, clean, and beautiful.
Built with **Qt**, powered by **espeak-ng** and **ffmpeg**, it reads `.txt`, `.docx`, and `.pdf` files aloud or saves them as high-quality MP3s.

It’s not just a converter — it’s a voice for your documents.

---

## ✨ Features

- 🎤 Convert **PDF**, **Word**, and **Text** files to speech or MP3
- ⚙️ Built-in **voice rate**, **volume**, and **voice selection** controls
- 💾 Automatically saves MP3s to your `Documents/Chrona` folder
- 🎨 Sleek, minimal **gold-on-black PySide6 GUI**
- 🌐 Update checker for new versions
- 🪶 Offline — no internet required
- 💡 Optional “Speak Only” or “MP3 Only” modes

---

## ⚙️ Requirements

- `ffmpeg`
- `espeak-ng`

_(Installed automatically if you use the AUR package)_

---

## 📦 Installation

### 🐧 Arch-based Distros

```
yay -S chrona-bin
```

### Generic Linux

```
curl -L -o install.sh https://github.com/Cypher-Monarch/Chrona/releases/download/v1.0.0/install.sh
chmod +x install.sh
sudo ./install.sh
```


### 🪟 Windows

Grab the latest installer or ZIP build from [Releases](https://github.com/Cypher-Monarch/Chrona/releases).

---

## 🖥️ Usage

- **Run from terminal:**

  ```
  chrona
  ```

- **Or from your app menu:**
  Search for **Chrona**

Select your document → tweak voice and speed → choose speak, save, or both.

MP3s are automatically saved under:

```
~/Documents/Chrona/
```

---

## 📁 Files & Paths

- **Binary:** `/opt/Chrona/chrona.elf`
- **Icon:** `/opt/Chrona/Chrona.png`
- **Launcher:** `/usr/bin/chrona`
- **Desktop Entry:** `/usr/share/applications/chrona.desktop`

---

## 🧠 Philosophy

> _“Accessibility should be effortless.”_

Chrona was built with simplicity at its core — for creators, teachers, and anyone who needs text to come alive.

Lightweight, offline, elegant.
That’s the Monarch way. 🖤
