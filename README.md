📌 About

This project automates repetitive GUI tasks by scanning the screen for target images and clicking on them with calculated coordinates. It was built to solve a real problem: manual clicking is tiring, imprecise, and error-prone over long sessions — especially when the user is holding the mouse button while the script needs to take over.

Key challenge solved: when the user holds the left mouse button, the script's clicks conflict with the ongoing press. The solution blocks all system input (mouse + keyboard) via the Windows BlockInput API during critical actions, then restores the previous state.

    ⚠️ This is a GUI automation / computer vision exercise. It does not encourage violating any platform's terms of service.

✨ Features

    🖼️ Template matching with adjustable confidence and region-of-interest

    🖱️ Smart clicking — click point derived from the matched image's bounding box

    🔒 Input blocking via native Windows API (BlockInput) to prevent mouse/keyboard interference

    🎯 Hold-state detection & restore — detects if the user is holding the mouse and restores it after the action

    ⌨️ Global hotkeys (F6/F7/F8) with transition detection (no key repeat)

    🔀 Two operation modes — whitelist (accept known good) and blacklist (reject known bad)

    🎨 Color-aware matching — optionally compares in RGB instead of grayscale when color is the distinguishing factor

    🌐 Browser automation via Playwright for canvas-based pages

    💧 Color picker utility — grab RGB/HEX of any pixel with a click

🏗️ Architecture
File	Role
autoulti_esc.py	Core engine: image recognition, clicking, hotkeys, input blocking
autocor.py	Color picker utility (click to get RGB/HEX)
autoore.py	Playwright-based browser/canvas automation
autoultimatumESC.bat	Windows launcher with virtualenv activation
🚀 Getting Started
Requirements
bash

pip install -r requirements.txt

Main dependencies:
text

pyautogui==0.9.54
pynput==1.8.1
opencv-python==4.12.0.88
pillow==12.0.0
playwright        # optional, only for autoore.py

    opencv-python is required by PyAutoGUI for confidence-based matching.

Run

Windows (recommended):
bash

autoultimatumESC.bat

Manual:
bash

python autoulti_esc.py

Hotkeys
Key	Action
F8	Start / Pause
F7	Toggle mode (Normal ↔ Grueling)
F6	Exit
🧠 How It Works
1. Finding an image on screen
python

def encontrar(nome_arquivo_imagem, confianca=0.90, region=None, cinza=True):
    regiao = pyautogui.locateOnScreen(
        nome_arquivo_imagem,
        confidence=confianca,
        region=region,
        grayscale=cinza
    )
    return regiao is not None

    confidence — how strict the match must be

    region — restrict search area for speed

    grayscale — faster, but use False when color matters (e.g. only the selected option is colored)

2. Clicking safely
python

def encontrar_e_clicar(nome_arquivo_imagem, ...):
    regiao = pyautogui.locateOnScreen(...)
    if regiao:
        x, y, w, h = regiao
        preparar_interacao()          # block inputs, release hold, press ESC
        pyautogui.moveTo(x, y, duration=0.1)
        pyautogui.click(x, y)
        finalizar_interacao()         # move away, click, ESC, unblock, restore hold

3. Handling mouse-hold conflicts
python

def preparar_interacao():
    ESTAVA_EM_HOLD = mouse_em_hold()
    if not ESTAVA_EM_HOLD:
        return
    bloquear_entradas(True)        # BlockInput(True) — mouse AND keyboard
    pyautogui.mouseUp(button='left')
    pyautogui.press('esc')

python

def finalizar_interacao():
    bloquear_entradas(False)       # unblock
    pyautogui.moveTo(3500, 750)
    pyautogui.click()
    pyautogui.press('esc')
    if ESTAVA_EM_HOLD:
        pyautogui.mouseDown(button='left')  # restore hold

4. Operation modes
Mode	Strategy	Logic
Normal	Whitelist	Click the first known-good image found
Grueling	Blacklist	Accept anything except forbidden images

In Grueling mode, color comparison is used (cinza=False) because only the auto-selected option stays colored — the rest are desaturated. Grayscale would produce false positives.
🛠️ Tech Stack
Tech	Purpose
PyAutoGUI	Screen capture, image location, mouse control
Pynput	Global mouse listener (color picker)
OpenCV	Backend for confidence-based template matching
Playwright	Browser/canvas automation
ctypes + windll	BlockInput from Windows user32.dll
threading	Hotkey listener on separate thread
glob / os	Dynamic image directory scanning
🛡️ Safety & Robustness

    Input blocking prevents accidental mouse movement during actions

    Hold-state detection avoids conflicts with the user's ongoing click

    ImageNotFoundException handled everywhere

    Clean shutdown via threading.Event

    Blacklist images are excluded from the whitelist search set

    🔮 Possible Extensions

    OCR (Tesseract) for dynamic text recognition

    OpenCV multi-scale / rotation-invariant matching

    Web dashboard for configuring regions and images

    Structured JSON logging for post-run analysis

    Standalone .exe via PyInstaller

📄 License

MIT — use at your own risk. This is an educational automation project.
🙌 Acknowledgements

Built as a hands-on exercise in GUI automation, computer vision, and native Windows API integration.
