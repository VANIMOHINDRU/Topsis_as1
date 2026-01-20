from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import os
import shutil
import re
import smtplib
from email.message import EmailMessage
from topsis_logic import run_topsis

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


# ---------------- HOME PAGE ----------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>TOPSIS Web Service</title>
        </head>
        <body>
            <h2>TOPSIS Web Service</h2>
            <form action="/submit" method="post" enctype="multipart/form-data">
                <label>Input File:</label><br>
                <input type="file" name="file" required><br><br>

                <label>Weights:</label><br>
                <input type="text" name="weights" placeholder="1,1,1,1" required><br><br>

                <label>Impacts:</label><br>
                <input type="text" name="impacts" placeholder="+,+,-,+" required><br><br>

                <label>Email ID:</label><br>
                <input type="email" name="email" required><br><br>

                <button type="submit">Submit</button>
            </form>
        </body>
    </html>
    """


# ---------------- FORM SUBMISSION ----------------
@app.post("/submit")
async def submit(
    file: UploadFile = File(...),
    weights: str = Form(...),
    impacts: str = Form(...),
    email: str = Form(...)
):
    # -------- Email validation --------
    if not re.match(EMAIL_REGEX, email):
        return {"error": "Invalid email format"}

    # -------- Save uploaded file --------
    input_path = os.path.join(UPLOAD_DIR, file.filename)
    output_path = os.path.join(UPLOAD_DIR, "result.csv")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # -------- Run TOPSIS --------
    try:
        run_topsis(
            input_file=input_path,
            weights_str=weights,
            impacts_str=impacts,
            output_file=output_path
        )
    except Exception as e:
        return {"error": str(e)}

    # -------- Send Email --------
    try:
        msg = EmailMessage()
        msg["Subject"] = "TOPSIS Result"
        msg["From"] = "vani2711d@gmail.com"
        msg["To"] = email
        msg.set_content("Please find the TOPSIS result attached.")

        with open(output_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="octet-stream",
                filename="result.csv"
            )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("vani2711d@gmail.com", "rpmp ycsp nall kfut")
            server.send_message(msg)

    except Exception as e:
        return {"error": f"Email sending failed: {e}"}

    return {"message": "Result file has been emailed successfully"}
