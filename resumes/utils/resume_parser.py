# resumes/utils/resume_parser.py
"""
Robust resume parsing helpers. Designed to be resilient to model output
and file variations, and to keep your DB consistent.

Notes:
- Supports PDF natively via PyMuPDF (fitz).
- Optionally supports DOCX if python-docx is installed.
- Uses strict JSON parsing with a known schema shape.
- Exposes the exact functions your views expect:
  validate_file_extension, validate_file_size, read_upload_file,
  extract_resume_information (kept for compatibility),
  analyze_with_ollama.
"""

import json
import os
from typing import Any, Dict, List
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

import fitz  # PyMuPDF
import requests

# ---- Optional DOCX support (won't crash if missing) ----
try:
    import docx  # type: ignore
    HAS_DOCX = True
except Exception:
    HAS_DOCX = False

# === Allowed inputs ===
VALID_EXTENSIONS = [".pdf", ".docx", ".doc"]
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB


# ---------- Validation ----------

def validate_file_extension(file_object: UploadedFile) -> str:
    """
    Ensure we accept only expected file types, and return normalized extension.
    """
    ext = os.path.splitext(file_object.name)[1].lower()
    if ext not in VALID_EXTENSIONS:
        raise ValidationError(f"Unsupported file extension: {ext}. Allowed: {', '.join(VALID_EXTENSIONS)}")
    # We only parse .docx if python-docx is available; .doc is rejected since it's legacy/binary.
    if ext == ".doc" and not HAS_DOCX:
        raise ValidationError("Legacy .doc not supported on this server. Please upload PDF or DOCX.")
    return ext


def validate_file_size(file_object: UploadedFile) -> bool:
    """Reject very large resumes to protect server memory."""
    if file_object.size > MAX_UPLOAD_SIZE:
        raise ValidationError("File size exceeds the 10MB limit.")
    return True


# ---------- File reading ----------

def _read_pdf(file_object: UploadedFile) -> str:
    """Extract text from PDF using PyMuPDF."""
    text = ""
    # Important: read() consumes the stream; use bytes buffer for fitz
    data = file_object.read()
    with fitz.open(stream=data, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text() or ""
    return text


def _read_docx(file_object: UploadedFile) -> str:
    """Extract text from DOCX using python-docx (if available)."""
    if not HAS_DOCX:
        raise ValidationError("DOCX parsing is not enabled on this server.")
    # python-docx expects a path-like or a file-like object positioned at start
    file_object.seek(0)
    d = docx.Document(file_object)
    return "\n".join([p.text for p in d.paragraphs])


def read_upload_file(file_object: UploadedFile, file_extension: str) -> str:
    """
    Unify file reading. PDFs via PyMuPDF; DOCX via python-docx.
    """
    if file_extension == ".pdf":
        return _read_pdf(file_object)
    if file_extension in (".docx", ".doc"):
        return _read_docx(file_object)
    # Defensive default (should not hit because of validate_file_extension)
    raise ValidationError(f"Cannot parse files with extension: {file_extension}")


# ---------- Model (Ollama) helpers ----------

def _safe_json_loads(s: str) -> Dict[str, Any]:
    """
    Parse model output strictly as JSON. If it isn't valid JSON, raise.
    We also try to strip non-JSON noise (common LLM failure mode).
    """
    s = (s or "").strip()

    # Quick heuristic: find first '{' and last '}' to trim prose
    try:
        first = s.index("{")
        last = s.rindex("}")
        s = s[first:last+1]
    except ValueError:
        # Not even JSON-shaped
        raise ValueError("Model returned non-JSON content.")

    return json.loads(s)


def _coerce_to_schema(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enforce a stable schema so the rest of your pipeline never breaks.
    Missing fields become empty; incorrect types are normalized.
    """
    def as_str(x) -> str:
        return (x or "").strip() if isinstance(x, str) else ""

    def as_list(x) -> List[Any]:
        return x if isinstance(x, list) else []

    # Expected top-level keys
    out = {
        "contact_info": {
            "full_name": "",
            "email": "",
            "phone": "",
            "city": "",
            "state": ""
        },
        "skills": [],
        "experience": [],
        "education": [],
    }

    ci = parsed.get("contact_info") or {}
    out["contact_info"]["full_name"] = as_str(ci.get("full_name"))
    out["contact_info"]["email"] = as_str(ci.get("email"))
    out["contact_info"]["phone"] = as_str(ci.get("phone"))
    out["contact_info"]["city"] = as_str(ci.get("city"))
    out["contact_info"]["state"] = as_str(ci.get("state"))[:2].upper()  # Normalize to 2-letter if present

    # Skills -> list[str]
    out["skills"] = [as_str(s) for s in as_list(parsed.get("skills")) if as_str(s)]

    # Experience -> list[dict]
    exp_list = as_list(parsed.get("experience"))
    exp_out = []
    for e in exp_list:
        if not isinstance(e, dict):
            continue
        exp_out.append({
            "job_title": as_str(e.get("job_title")),
            "company": as_str(e.get("company")),
            "dates": as_str(e.get("dates")),
        })
    out["experience"] = exp_out

    # Education -> list[dict]
    edu_list = as_list(parsed.get("education"))
    edu_out = []
    for ed in edu_list:
        if not isinstance(ed, dict):
            continue
        edu_out.append({
            "school_name": as_str(ed.get("school_name") or ed.get("institution")),
            "degree": as_str(ed.get("degree")),
            "graduation_year": as_str(ed.get("graduation_year") or ed.get("year"))[:4],
        })
    out["education"] = edu_out

    return out


def extract_resume_information(file_content: str) -> Dict[str, Any]:
    """
    Backwards-compatible function name. Uses a strict prompt and returns a dict
    conforming to our schema (even if model output is imperfect).
    """
    # System-style instructions: return JSON only and exact keys.
    prompt = f"""
Extract the following fields from the resume text.
Return ONLY valid JSON in this EXACT structure. No prose.

{{
  "contact_info": {{
    "full_name": "",
    "email": "",
    "phone": "",
    "city": "",
    "state": ""
  }},
  "skills": [],
  "experience": [{{ "job_title": "", "company": "", "dates": "" }}],
  "education": [{{ "school_name": "", "degree": "", "graduation_year": "" }}]
}}

Resume text:
{file_content}
    """.strip()

    # Use the same generator as analyze_with_ollama to avoid two model paths.
    raw = analyze_with_ollama(prompt, model="mistral:latest")
    try:
        parsed = _safe_json_loads(raw)
    except Exception:
        # If model fails, return empty but valid shape so the UI still works.
        return _coerce_to_schema({})

    return _coerce_to_schema(parsed)


def analyze_with_ollama(prompt: str, model: str = "mistral:latest") -> str:
    """
    Call a local Ollama server with a single prompt (non-streaming).
    Returns the raw 'response' field (string). Exceptions bubble up to views.
    """
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    # Ollama's /generate returns {"response": "..."} when stream=False
    return data.get("response", "") or ""
