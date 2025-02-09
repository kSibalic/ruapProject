from flask import Flask, render_template, request, jsonify
import urllib.request
import json
import os
import ssl

def allowSelfSignedHttps(allowed):
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True)

app = Flask(__name__)

API_URL = 'http://060fd6ad-695f-4ef8-a9b2-24f8243c2f3d.eastus2.azurecontainer.io/score'
API_KEY = 'aMv3SZnrX4pkyuwhigofZ3mRG2dvhS2B'  # Unesi svoj API ključ ovdje

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = {
            "Inputs": {
                "input1": [
                    {
                        "Brand": request.form.get("brand"),
                        "Processor": request.form.get("processor"),
                        "RAM_GB": int(request.form.get("ram")),
                        "Storage": request.form.get("storage"),
                        "GPU": request.form.get("gpu"),
                        "Screen_Size_inch": float(request.form.get("screen_size")),
                        "Resolution": request.form.get("resolution"),
                        "Battery_Life_hours": float(request.form.get("battery_life")),
                        "Weight_kg": float(request.form.get("weight")),
                        "Operating_System": request.form.get("os"),
                        "Price_$": None
                    }
                ]
            }
        }

        body = str.encode(json.dumps(data))
        headers = {'Content-Type': 'application/json', 'Authorization': ('Bearer ' + API_KEY)}
        req = urllib.request.Request(API_URL, body, headers)

        try:
            response = urllib.request.urlopen(req)
            result = response.read().decode()
            return jsonify({"message": "Data sent successfully", "response": result})
        except urllib.error.HTTPError as error:
            return jsonify({"error": str(error), "details": error.read().decode("utf8", 'ignore')})

    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)