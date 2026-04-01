from flask import Flask, render_template, request, send_file
import pickle
import numpy as np
from fpdf import FPDF

app = Flask(__name__)

# 🔥 LOAD MODEL
model = pickle.load(open("disaster_model.pkl","rb"))

print("Model loaded successfully")


@app.route("/")
def home():
    return render_template("index.html")


# 🔥 NEW ROUTES (ADD केले)
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/simulation")
def simulation():
    return render_template("simulation.html")


# 🚀 PREDICTION
@app.route("/prediction", methods=["GET","POST"])
def prediction():

    result = None
    risk = None
    recommendation = ""   # ⭐ add

    if request.method == "POST":

        population = float(request.form["population"])
        district = float(request.form["district"])
        disaster_type = float(request.form["disaster_type"])
        rainfall = float(request.form["rainfall"])
        damage = float(request.form["damage"])

        features = np.array([[population, district, disaster_type, rainfall, damage]])

        pred = model.predict(features)[0]

        result = {
            "shelters": int(pred[0]),
            "food": int(pred[1]),
            "rescue": int(pred[2]),
            "deaths": int(pred[3])
        }

        total = result["shelters"] + result["food"] + result["rescue"]

        if total > 150:
            risk = "High"
            recommendation = "🚨 Immediate evacuation required"

        elif total > 80:
            risk = "Medium"
            recommendation = "⚠ Prepare resources"

        else:
            risk = "Low"
            recommendation = "✅ Situation normal"

        # ⭐ SAVE RESULT FOR PDF
        app.config["result"] = result
        app.config["risk"] = risk

    return render_template("prediction.html",
                           prediction=result,
                           risk=risk,
                           recommendation=recommendation)


# 📄 PDF DOWNLOAD
@app.route("/download_report")
def download_report():

    result = app.config.get("result")
    risk = app.config.get("risk")

    if not result:
        return "First do prediction!"

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=16)
    pdf.cell(200,10,"AI Disaster Prediction Report",ln=True,align='C')

    pdf.ln(10)
    pdf.set_font("Arial", size=12)

    pdf.cell(200,10,f"Shelters Needed : {result['shelters']}",ln=True)
    pdf.cell(200,10,f"Food Packets : {result['food']}",ln=True)
    pdf.cell(200,10,f"Rescue Teams : {result['rescue']}",ln=True)
    pdf.cell(200,10,f"Casualties : {result['deaths']}",ln=True)
    pdf.cell(200,10,f"Risk Level : {risk}",ln=True)

    file_name = "report.pdf"
    pdf.output(file_name)

    return send_file(file_name, as_attachment=True)


print("Starting Flask server...")
app.run(debug=True)