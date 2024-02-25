from threading import Thread

from flask import Flask, jsonify

app = Flask('')

@app.route('/')
def home():
    return "Hello. I am alive!"

@app.route('/api/status')
def api_status():
    return jsonify({"status": "alive"})

def run():
    app.run(host='0.0.0.0', port=8080)
    print("Discord Bot URL:", "https://DiscordBot.karendomalesa23.repl.co")

def keep_alive():
    t = Thread(target=run)
    t.start()

# Start the Flask application
keep_alive()
