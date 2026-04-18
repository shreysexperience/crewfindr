from flask import Flask, request, redirect
import time, random, math

app = Flask(__name__)

members = []
signals = []

# ---------------------------
# HELPERS
# ---------------------------
def gen_location():
    return 19.07 + random.uniform(-0.005, 0.005), 72.87 + random.uniform(-0.005, 0.005)

def distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def predict_risk(m):
    if not m["last"]:
        return "🟢 Safe"

    delay = time.time() - m["last"]
    coords = [(x["lat"], x["lon"]) for x in members if x["lat"]]

    if not coords:
        return "🟢 Safe"

    center = (
        sum(c[0] for c in coords)/len(coords),
        sum(c[1] for c in coords)/len(coords)
    )

    dist = distance((m["lat"], m["lon"]), center)

    score = dist*10000 + delay + (100 - m["battery"])

    if m["status"] == "Danger":
        return "🔴 Danger"

    if score > 150: return "🔴 High Risk"
    if score > 80: return "🟡 Drifting"
    return "🟢 Safe"

# ---------------------------
# UI
# ---------------------------
def layout(content, active=""):
    return f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif&family=Inter:wght@300;500;700&display=swap" rel="stylesheet">

    <style>
    body {{ margin:0; background:#0a0a0a; color:white; font-family:Inter; }}

    .nav {{
        position:fixed; top:20px; left:50%; transform:translateX(-50%);
        width:90%; max-width:1100px;
        display:flex; justify-content:space-between;
        padding:14px 20px;
        background:rgba(255,255,255,0.08);
        backdrop-filter:blur(30px);
        border-radius:20px;
        border:1px solid rgba(255,255,255,0.2);
    }}

    .logo {{ font-family:"Instrument Serif"; font-size:22px; }}

    .links a {{
        margin-left:16px;
        font-family:"Instrument Serif";
        color:white;
        text-decoration:none;
        opacity:0.5;
    }}

    .active {{ opacity:1 !important; font-weight:700; }}

    .container {{ margin:120px auto; max-width:1100px; padding:20px; }}

    h1 {{ font-family:"Instrument Serif"; font-size:52px; }}

    .card {{
        background:rgba(255,255,255,0.05);
        padding:18px;
        margin-top:14px;
        border-radius:16px;
        border:1px solid rgba(255,255,255,0.1);
    }}

    input, select {{
        width:100%; padding:12px; margin-top:10px;
        background:#111; border:none; color:white;
        border-radius:10px;
    }}

    .btn {{
        margin-top:10px; padding:12px;
        width:100%; background:white; color:black;
        border:none; border-radius:10px;
        cursor:pointer;
    }}

    .danger {{ border-left:4px solid red; }}
    .warn {{ border-left:4px solid orange; }}
    .safe {{ border-left:4px solid green; }}

    </style>

    <script>
    function openMap(url) {{
        if(confirm("Allow location access & open map?")) {{
            window.open(url, "_blank");
        }}
    }}

    function vibrate() {{
        if(navigator.vibrate) navigator.vibrate([200,100,200]);
    }}
    </script>

    </head>

    <body>

    <div class="nav">
        <div class="logo">CrewFindr</div>
        <div class="links">
            <a href="/pack" class="{ 'active' if active=='pack' else '' }">Pack</a>
            <a href="/track" class="{ 'active' if active=='track' else '' }">Track</a>
            <a href="/alerts" class="{ 'active' if active=='alerts' else '' }">Alerts</a>
            <a href="/chat" class="{ 'active' if active=='chat' else '' }">Signals</a>
            <a href="/sos" class="{ 'active' if active=='sos' else '' }">SOS</a>
        </div>
    </div>

    <div class="container">
        {content}
    </div>

    </body>
    </html>
    """

# ---------------------------
# ROUTES
# ---------------------------
@app.route("/")
def home():
    return layout("""
    <h1>CrewFindr</h1>
    <p>AI-powered crowd coordination</p>
    <a href="/pack"><button class="btn">Start</button></a>
    """)

@app.route("/pack", methods=["GET","POST"])
def pack():
    if request.method == "POST":
        members.append({
            "name": request.form["name"],
            "lat": None,
            "lon": None,
            "battery": 100,
            "status": "Safe",
            "last": None
        })
        return redirect("/pack")

    cards = "".join([f"<div class='card'>{m['name']}</div>" for m in members])

    cont = ""
    if len(members) >= 2:
        cont = "<a href='/track'><button class='btn'>Start Tracking</button></a>"

    return layout(f"""
    <h1>Create Pack</h1>
    <form method="POST">
        <input name="name" placeholder="Name">
        <button class="btn">Add</button>
    </form>
    {cards}
    {cont}
    ""","pack")

@app.route("/track")
def track():
    cards = ""

    for m in members:
        if not m["lat"]:
            m["lat"], m["lon"] = gen_location()

        m["lat"], m["lon"] = gen_location()
        m["last"] = time.time()

        risk = predict_risk(m)
        link = f"https://www.google.com/maps?q={m['lat']},{m['lon']}"

        cls = "safe"
        if "Danger" in risk:
            cls = "danger"
        elif "Drifting" in risk:
            cls = "warn"

        cards += f"""
        <div class="card {cls}">
            <h3>{m['name']}</h3>
            <p>{risk}</p>
            <p>🔋 {m['battery']}%</p>
            <button class="btn" onclick="openMap('{link}')">Open Map</button>
        </div>
        """

    return layout(f"<h1>Live Tracking</h1>{cards}","track")

@app.route("/alerts", methods=["GET","POST"])
def alerts():
    if request.method == "POST":
        name = request.form["name"]

        for m in members:
            if m["name"] == name:
                m["battery"] = int(request.form["battery"])
                m["status"] = request.form["status"]

        return redirect("/alerts")

    options = "".join([f"<option>{m['name']}</option>" for m in members])

    cards = ""

    for m in members:
        risk = predict_risk(m)

        cards += f"""
        <div class="card">
            <h3>{m['name']}</h3>
            <p>{risk}</p>
            <p>Status: {m['status']}</p>
            <p>🔋 {m['battery']}%</p>
        </div>
        """

    return layout(f"""
    <h1>Alerts Control Panel</h1>

    <form method="POST">
        <select name="name">{options}</select>
        <input type="number" name="battery" placeholder="Battery %">
        <select name="status">
            <option>Safe</option>
            <option>Careful</option>
            <option>Danger</option>
        </select>
        <button class="btn" onclick="vibrate()">Update</button>
    </form>

    {cards}
    ""","alerts")

@app.route("/chat", methods=["GET","POST"])
def chat():
    if request.method == "POST":
        signals.append({
            "name": request.form["name"],
            "text": request.form["text"],
            "time": time.strftime("%H:%M")
        })
        return redirect("/chat")

    options = "".join([f"<option>{m['name']}</option>" for m in members])

    ui = "".join([f"""
    <div class="card">
        <b>{s['name']}</b> • {s['time']}
        <p>{s['text']}</p>
    </div>
    """ for s in signals[::-1]])

    return layout(f"""
    <h1>Signal Board</h1>

    <form method="POST">
        <select name="name">{options}</select>
        <input name="text" placeholder="Send signal...">
        <button class="btn">Broadcast</button>
    </form>

    {ui}
    ""","chat")

@app.route("/sos")
def sos():
    return layout("""
    <h1>Emergency SOS</h1>
    <button class="btn" onclick="vibrate()">SEND SOS</button>
    ""","sos")

# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)