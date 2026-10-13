import os
import io
import json
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
REPORT_DIR = BASE_DIR / "reports"
DATA_DIR = BASE_DIR / "data"
for folder in (UPLOAD_DIR, REPORT_DIR, DATA_DIR):
    folder.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"csv", "xlsx"}
app = Flask(__name__)
app.secret_key = os.environ.get("NOVAFLOW_SECRET_KEY", "change-this-secret-before-deployment")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload limit

HISTORY_FILE = DATA_DIR / "history.json"


def load_history():
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_history(items):
    HISTORY_FILE.write_text(json.dumps(items, indent=2), encoding="utf-8")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def read_dataframe(path):
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".xlsx":
        return pd.read_excel(path)
    raise ValueError("CSV or XLSX files only are supported.")


def analyze_dataframe(df):
    rows, cols = df.shape
    missing_by_column = df.isna().sum()
    duplicate_rows = int(df.duplicated().sum())
    missing_cells = int(missing_by_column.sum())
    column_info = []
    for col in df.columns:
        column_info.append({
            "name": str(col),
            "missing": int(missing_by_column[col]),
            "unique": int(df[col].nunique(dropna=True)),
            "dtype": str(df[col].dtype)
        })
    return {
        "rows": int(rows),
        "columns": int(cols),
        "duplicates": duplicate_rows,
        "missing_cells": missing_cells,
        "column_info": column_info,
        "preview_headers": [str(c) for c in df.columns],
        "preview_rows": df.head(8).fillna("").astype(str).to_dict(orient="records"),
    }


def make_report_text(filename, analysis, date_from, date_to):
    today = datetime.now().strftime("%d-%m-%Y")
    period = f"{date_from} to {date_to}" if date_from and date_to else today
    lines = [
        "NOVAFLOW AI — DATA ANALYSIS REPORT",
        "=" * 38,
        f"Source file: {filename}",
        f"Report period: {period}",
        f"Prepared on: {today}",
        "",
        "SUMMARY",
        f"- Total records: {analysis['rows']}",
        f"- Total columns: {analysis['columns']}",
        f"- Duplicate rows: {analysis['duplicates']}",
        f"- Missing cells: {analysis['missing_cells']}",
        "",
        "COLUMN DETAILS",
    ]
    for col in analysis["column_info"]:
        lines.append(f"- {col['name']}: {col['unique']} unique values, {col['missing']} missing, type {col['dtype']}")
    lines += [
        "",
        "RECOMMENDED REVIEW",
        "- Review duplicate rows before removing them.",
        "- Check missing values in important business fields.",
        "- Confirm findings with an authorized employee before using them for business decisions.",
        "",
        "Note: This report is generated from the uploaded file. It does not independently verify identities or external records."
    ]
    return "\n".join(lines)


@app.route("/", methods=["GET"])
def index():
    history = load_history()[:10]
    return render_template("index.html", history=history)


@app.route("/analyze", methods=["POST"])
def analyze():
    upload = request.files.get("file")
    date_from = request.form.get("date_from", "").strip()
    date_to = request.form.get("date_to", "").strip()

    if not upload or not upload.filename:
        flash("Please choose a CSV or XLSX file.", "error")
        return redirect(url_for("index"))
    if not allowed_file(upload.filename):
        flash("Only .csv and .xlsx files are supported.", "error")
        return redirect(url_for("index"))

    safe_name = secure_filename(upload.filename)
    stored_name = f"{uuid.uuid4().hex}_{safe_name}"
    path = UPLOAD_DIR / stored_name
    upload.save(path)

    try:
        df = read_dataframe(path)
        if df.empty and len(df.columns) == 0:
            raise ValueError("The uploaded file has no readable data.")
        analysis = analyze_dataframe(df)
        report_text = make_report_text(safe_name, analysis, date_from, date_to)
        report_id = uuid.uuid4().hex[:12]
        report_path = REPORT_DIR / f"report_{report_id}.txt"
        report_path.write_text(report_text, encoding="utf-8")

        history = load_history()
        history.insert(0, {
            "id": report_id,
            "filename": safe_name,
            "created": datetime.now().strftime("%d-%m-%Y %H:%M"),
            "rows": analysis["rows"],
            "duplicates": analysis["duplicates"],
            "missing": analysis["missing_cells"],
            "report_file": report_path.name
        })
        save_history(history[:100])
        return render_template(
            "result.html",
            filename=safe_name,
            analysis=analysis,
            report_text=report_text,
            report_id=report_id,
            date_from=date_from,
            date_to=date_to
        )
    except Exception as exc:
        flash(f"Could not analyze this file: {exc}", "error")
        return redirect(url_for("index"))
    finally:
        # Keep uploaded files only for the current prototype session.
        # For a production service, configure an explicit retention policy.
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


@app.route("/download/<report_id>", methods=["GET"])
def download_report(report_id):
    if not report_id.isalnum():
        flash("Invalid report ID.", "error")
        return redirect(url_for("index"))
    path = REPORT_DIR / f"report_{report_id}.txt"
    if not path.exists():
        flash("Report not found. Please run the analysis again.", "error")
        return redirect(url_for("index"))
    return send_file(path, as_attachment=True, download_name=f"NovaFlowAI_Report_{report_id}.txt", mimetype="text/plain")


@app.route("/history", methods=["GET"])
def history():
    return render_template("history.html", history=load_history())


@app.errorhandler(413)
def too_large(_error):
    flash("File is too large. Maximum upload size is 10 MB.", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    # Local development only. Do not use Flask's development server in production.
    app.run(host="127.0.0.1", port=5000, debug=True)
