"""Everything teacher-specific lives here.

Contact details come from environment variables (.env). Text content is edited
directly in this file. Anything flagged ``sample`` is placeholder copy: it shows
a small "Sample" tag on the website until you replace it and remove the flag
(or set SHOW_SAMPLE_TAGS=0).
"""
import os
import re
from functools import lru_cache

PLACEHOLDER = "[Add details]"

# TODO(teacher): replace with real tuition timings, e.g. {"days": "Mon, Wed, Fri", "time": "5:00 pm to 7:00 pm"}
TIMINGS = [
    {"mode": "Offline", "place": "Vengadamangalam", "days": "[Add days]", "time": "[Add timing]"},
    {"mode": "Online", "place": "Live video classes", "days": "[Add days]", "time": "[Add timing]"},
]

HIGHLIGHTS = [
    ("M.Sc. Mathematics", "A postgraduate qualification in the subject she teaches."),
    ("Classes 10 to 12", "From middle-school foundations to higher-secondary preparation."),
    ("In person and online", "Classes in Vengadamangalam, or live online from anywhere."),
    ("Easy to reach", "Ask a question on WhatsApp or send the admission form any time."),
]

CLASS_BANDS = [
    ("10", "Strengthening fundamentals and applications", "Build conceptual clarity.Analytical skills. Examination-oriented problem-solving skills."),
    ("11 & 12", "Advanced concepts and examination preparation", "Master higher-level mathematical concepts. Strengthen application skills. Prepare systematically for examinations"),
]

# sample: True -> shows a "Sample" tag. Rewrite these in the teacher's own words.
METHODOLOGY = [
    ("Conceptual understanding", "Introduce each concept with clear explanations and examples, helping students understand the logic behind mathematical methods."),
    ("Guided practice", "Work through problems step by step before encouraging students to solve similar questions independently."),
    ("Doubt clarification", "Encourage students to ask questions, revisit challenging concepts and learn from their mistakes."),
    ("Revision and assessment", "Use appropriate revision practice, questions and exam-style problems to reinforce learning and assess understanding."),
]

TESTIMONIALS = [
    {
        "quote": "[Sample testimonial. Replace with genuine feedback from a parent or student.]",
        "name": "[Parent or student name]",
        "detail": "[Class]",
        "sample": True,
    }
]

FAQS = [
    ("Which classes and subjects are taught?", "Mathematics for classes 10 to 12."),
    ("Are classes online or in person?", "Both. Choose offline in Vengadamangalam or online when you apply."),
    ("How do I apply?", "Fill in the admission form. You will get a reference number, and the teacher will contact you on the mobile number you give."),
    ("What about fees and batch timings?", "These are shared directly by the teacher. Ask on WhatsApp or mention it in the form."),
    ("Is my child's information safe?", "Applications are visible only to the teacher and are never shown publicly."),
]

ABOUT = {
    "bio": """I am Jancy T, a postgraduate in Mathematics (M.Sc. Mathematics), with a background in school teaching and private tutoring.
            I teaches Mathematics to students of Classes 10, 11 and 12 across CBSE, ICSE and State Board curriculam, in both English and Tamil.
            For me, teaching mathematics is about making sense of what once seemed difficult.
            I focuses on connecting conceptual understanding with examination-oriented practice through structured lessons and customised worksheets, 
            helping students understand the logic behind concepts and apply them with clarity.
            """,
    "experience": "Five years of experience in private tutoring, teaching mathematics to students across multiple curriculums with a focus on school-level learning and examination preparation.",
    "philosophy": "Mathematics is not just hard; the way it is taught matters.",
    "achievements": ["Completed an academic project in Mathematical Education as part of postgraduate studies in Mathematics."],  # e.g. ["Rank holder, University of ..."]. Add only real achievements.
}


def _env(name, default=""):
    return os.environ.get(name, default).strip()


@lru_cache(maxsize=1)
def load_site():
    name = _env("TEACHER_NAME", "Jancy T")
    return {
        "name": name,
        "first_name": name.split()[0],
        "qualification": "M.Sc. Mathematics",
        "classes": "10th to 12th",
        "subjects": ["Mathematics"],
        "location": "Vengadamangalam",
        "address": _env("TEACHER_ADDRESS", "Vengadamangalam"),
        "maps_url": _env("GOOGLE_MAPS_URL"),
        "phone": _env("TEACHER_PHONE", "+91 00000 00000"),
        "phone_tel": "+" + re.sub(r"\D", "", _env("TEACHER_PHONE", "910000000000")),
        "whatsapp": re.sub(r"\D", "", _env("WHATSAPP_NUMBER", "910000000000")),
        "email": _env("TEACHER_EMAIL"),
        "photo": _env("TEACHER_PHOTO", "teacher-placeholder.svg"),
        "og_image": _env("OG_IMAGE"),
        "social": {k: v for k, v in {
            "Instagram": _env("INSTAGRAM_URL"),
            "Facebook": _env("FACEBOOK_URL"),
            "YouTube": _env("YOUTUBE_URL"),
        }.items() if v},
        "show_sample": _env("SHOW_SAMPLE_TAGS", "1") not in {"0", "false", "no"},
        "timings": TIMINGS,
        "highlights": HIGHLIGHTS,
        "class_bands": CLASS_BANDS,
        "methodology": METHODOLOGY,
        "testimonials": TESTIMONIALS,
        "faqs": FAQS,
        "about": ABOUT,
    }
