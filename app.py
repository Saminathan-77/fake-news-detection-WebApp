from flask import Flask, request, jsonify, send_file, Response, render_template
from datetime import datetime
from io import BytesIO
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from google.generativeai import configure, GenerativeModel, GenerationConfig

# Initialize Flask app
app = Flask(__name__)

# Configure Gemini API
configure(api_key="your API KEY")
model = GenerativeModel('gemini-2.0-flash')

# AI classification function
def classify_news(text=None, image_path=None):
    generation_config = GenerationConfig(
        temperature=0.7,
        max_output_tokens=200
    )


    # Define input prompt
    system_prompt = """
You are an AI news classifier designed to determine whether a given news statement is Real or Fake based on available knowledge. The user may be vague, so interpret their query in the most relevant way possible.

Instructions:

Classify the news as either Real or Fake.
If Fake, provide a short factual correction or clarification (1-2 sentences) explaining why it is incorrect.
Keep responses concise and direct (no unnecessary explanations).
Example Output:

Real
Fake: The claim is false because [brief fact].
Additional Guidelines:

If unsure, classify as Fake and provide the best-known factual correction. In case it is an image, seemwhether its AI generated or not. if its AI generated then give fake else real.
Do not generate misleading or unsupported responses. Dont mention any time frames in the response. Here is the user's request:"""

    # Prepare input for Gemini
    if image_path:
        image = Image.open(image_path)
        prompt = [system_prompt, image]
    else:
        prompt = [system_prompt, text]

    # Generate response
    response = model.generate_content(prompt, generation_config=generation_config)
    
    return {"verdict": response.text}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.form.get("text")
    image = request.files.get("image")

    if not text and not image:
        return jsonify({"error": "No input provided"}), 400

    # Save image temporarily if uploaded
    image_path = None
    if image:
        image_path = "temp_image.jpg"
        image.save(image_path)

    # Get AI classification result
    classification = classify_news(text, image_path)

    return jsonify(classification)

@app.route("/generate_report", methods=["POST"])
def generate_report():
    data = request.json
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No news text provided"}), 400

    # Get AI classification
    classification = classify_news(text)
    verdict = classification["verdict"]
    reason = classification["reason"]
    score = classification["score"]

    # Generate PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(100, 750, "News Verification Report")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 730, f"Date: {datetime.now().strftime('%d-%m-%Y')}")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, 700, "Summary")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(100, 680, f"Verdict: {verdict}")
    pdf.drawString(100, 660, f"Credibility Score: {score}/100")
    pdf.drawString(100, 640, f"Reason: {reason}")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(100, 610, "News Content:")
    pdf.setFont("Helvetica", 10)
    y_position = 590
    for line in text.split("\n"):
        pdf.drawString(100, y_position, line[:90])
        y_position -= 15
        if y_position < 50:
            pdf.showPage()
            y_position = 750

    pdf.save()
    buffer.seek(0)

    return Response(buffer, mimetype="application/pdf",
                    headers={"Content-Disposition": "inline; filename=news_report.pdf"})

if __name__ == "__main__":
    app.run(debug=True)
