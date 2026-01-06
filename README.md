# online-chess-flask
A real-time multiplayer chess web application built with Python Flask, Socket.IO, and Chess.js. Features hybrid move validation and secure tunneling via Ngrok

Key Features
 - **Real-time Multiplayer:** Instant move updates across clients using WebSocket technology (Flask-Socket.IO).
 - **Hybrid Move Validation:** Dual-layer validation system using `Chess.js` (Frontend) for responsiveness and `python-chess` (Backend) for security and anti-cheat.
 - **Secure Tunneling:** Designed to work with **Ngrok** to expose the local server to the internet securely.

Tech Stack
 - Python, Flask, Flask-Socket.IO, python-chess, Chess.js, HTML/CSS, JavaScript, Ngrok

How to Run
1.  Clone the repository
    ```bash
    git clone [https://github.com/LittleCat1041/online-chess-flask.git](https://github.com/LittleCat1041/online-chess-flask.git)
    cd online-chess-flask
    ```
2.  Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
3.  Start the server
    ```bash
    python app.py
    ```
4.  Access the game
   
    Local: Open `http://localhost:5000`
    
    Online: Run `ngrok http 5000` and share the generated URL with a friend.
    
Screenshot

<img width="1097" height="773" alt="image" src="https://github.com/user-attachments/assets/ea6f4f73-c1a0-4554-aa45-63054e8da497" />
