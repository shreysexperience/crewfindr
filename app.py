from flask import Flask, request, redirect
import datetime

app = Flask(__name__)

groups = {"main": []}
alerts = []

def layout(content, active="pack"):
    return f"""
    <html>
    <head>
    <title>CrewFindr</title>

    <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif&display=swap" rel="stylesheet">

    <style>
    body {{
        margin:0;
        background:#000;
        color:#fff;
        font-family:-apple-system, BlinkMacSystemFont;
    }}

    .container {{
        width:390px;
        margin:auto;
        padding:20px;
        padding-bottom:120px;
    }}

    h1 {{
        font-family:'Instrument Serif';
        font-size:40px;
        letter-spacing:1px;
        margin:0;
    }}

    p {{
        color:#8E8E93;
        margin-top:4px;
    }}

    .card {{
        background:rgba(255,255,255,0.05);
        border-radius:20px;
        padding:18px;
        margin-top:16px;
        border:1px solid rgba(255,255,255,0.08);
    }}

    input, select {{
        width:100%;
        height:50px;
        border:none;
        border-radius:14px;
        background:#111;
        color:white;
        padding:0 14px;
        margin-top:12px;
    }}

    button {{
        width:100%;
        height:50px;
        border:none;
        border-radius:14px;
        margin-top:12px;
        font-family:'Instrument Serif';
        letter-spacing:1px;
        font-weight:600;
        cursor:pointer;
    }}

    .primary {{
        background:white;
        color:black;
    }}

    .danger {{
        background:#FF3B30;
        color:white;
    }}

    .status-safe {{ color:#34C759; }}
    .status-careful {{ color:#FF9F0A; }}
    .status-danger {{ color:#FF3B30; }}

    .nav {{
        position:fixed;
        bottom:20px;
        left:50%;
        transform:translateX(-50%);
        width:360px;
        display:flex;
        background:rgba(255,255,255,0.08);
        backdrop-filter:blur(20px);
        border-radius:24px;
        padding:8px;
    }}

    .nav a {{
        flex:1;
        text-align:center;
        text-decoration:none;
        color:#8E8E93;
        padding:10px;
        font-family:'Instrument Serif';
    }}

    .active {{
        background:rgba(255,255,255,0.15);
        color:white;
        border-radius:12px;
    }}

    .member {{
        display:flex;
        justify-content:space-between;
        align-items:center;
    }}

    .empty {{
        text-align:center;
        margin-top:40px;
        color:#666;
    }}
    </style>

    </head>
    <body>

    <div class="container">
    {content}
    </div>

    <div class="nav">
        <a href="/" class="{ 'active' if active=='pack' else ''}">Pack</a>
        <a href="/alerts" class="{ 'active' if active=='alerts' else ''}">Alerts</a>
        <a href="/group" class="{ 'active' if active=='group' else ''}">Group</a>
        <a href="/sos" class="{ 'active' if active=='sos' else ''}">SOS</a>
    </div>

    </body>
    </html>
    """

# ---------------- PACK DASHBOARD ----------------
@app.route("/", methods=["GET","POST"])
def pack():

    if request.method == "POST":
        name = request.form["name"]
        status = request.form["status"]

        for m in groups["main"]:
            if m["name"] == name:
                m["status"] = status
                m["time"] = datetime.datetime.now().strftime("%H:%M")

                if status == "danger":
                    alerts.append({
                        "name": name,
                        "time": m["time"]
                    })

    content = "<h1>CrewFindr</h1><p>Stay connected with your crew</p>"

    # MEMBERS
    if not groups["main"]:
        content += "<div class='empty'>No members yet → Create group</div>"
    else:
        for m in groups["main"]:
            cls = "status-safe"
            if m["status"] == "careful":
                cls = "status-careful"
            if m["status"] == "danger":
                cls = "status-danger"

            content += f"""
            <div class="card member">
                <div>
                    <b>{m['name']}</b><br>
                    <small>{m['time']}</small>
                </div>
                <div class="{cls}">{m['status']}</div>
            </div>
            """

    # UPDATE STATUS
    content += """
    <div class="card">
    <form method="POST">
        <input name="name" placeholder="Your name">
        <select name="status">
            <option value="safe">Safe</option>
            <option value="careful">Careful</option>
            <option value="danger">Danger</option>
        </select>
        <button class="primary">Update Status</button>
    </form>
    </div>
    """

    return layout(content, "pack")


# ---------------- GROUP ----------------
@app.route("/group", methods=["GET","POST"])
def group():

    if request.method == "POST":
        name = request.form["name"]
        groups["main"].append({
            "name": name,
            "status": "safe",
            "time": datetime.datetime.now().strftime("%H:%M")
        })

    content = """
    <h1>Create Group</h1>
    <p>Add people going with you</p>

    <div class="card">
    <form method="POST">
        <input name="name" placeholder="Member name" required>
        <button class="primary">Add Member</button>
    </form>
    </div>
    """

    for m in groups["main"]:
        content += f"<div class='card'>{m['name']}</div>"

    # CONTINUE BUTTON (FIXED)
    if groups["main"]:
        content += """
        <div class="card">
            <a href="/">
                <button class="primary">Continue to Pack</button>
            </a>
        </div>
        """

    return layout(content, "group")


# ---------------- ALERTS ----------------
@app.route("/alerts")
def alerts_page():

    content = "<h1>Alerts</h1><p>Live danger signals</p>"

    if not alerts:
        content += "<div class='empty'>No alerts yet</div>"
    else:
        for a in alerts[::-1]:
            content += f"""
            <div class="card">
                <b>{a['name']}</b><br>
                <small>{a['time']}</small>
            </div>
            """

    return layout(content, "alerts")


# ---------------- SOS ----------------
@app.route("/sos", methods=["GET","POST"])
def sos():

    if request.method == "POST":
        name = request.form["name"]

        alerts.append({
            "name": name,
            "time": datetime.datetime.now().strftime("%H:%M")
        })

    content = """
    <h1>SOS</h1>
    <p>Send emergency signal</p>

    <div class="card">
    <form method="POST">
        <input name="name" placeholder="Your name" required>
        <button class="danger">Send SOS</button>
    </form>
    </div>

    <div class="card">
        <a href="tel:112">
            <button class="danger">Call Emergency</button>
        </a>
    </div>
    """

    return layout(content, "sos")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)