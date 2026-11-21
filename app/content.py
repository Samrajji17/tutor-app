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
    ("Classes 6 to 12", "From middle-school foundations to higher-secondary preparation."),
    ("In person and online", "Classes in Vengadamangalam, or live online from anywhere."),
    ("Easy to reach", "Ask a question on WhatsApp or send the admission form any time."),
]

CLASS_BANDS = [
    ("6 to 8", "Foundation years", "Building number sense, confidence and the habit of showing working."),
    ("9 and 10", "Secondary school", "Algebra, geometry and the problem-solving that board exams reward."),
    ("11 and 12", "Higher secondary", "Deeper concepts and steady preparation for the final exams."),
]

# sample: True -> shows a "Sample" tag. Rewrite these in the teacher's own words.
METHODOLOGY = [
    ("Understand the idea", "Each topic starts from why it works, not only how to do it."),
    ("Practise with guidance", "Worked examples first, then problems the student tries independently."),
    ("Correct and revisit", "Mistakes are explained and revisited until the method is clear."),
    ("Prepare for tests", "Regular revision and exam-style questions close each unit."),
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
    ("Which classes and subjects are taught?", "Mathematics for classes 6 to 12."),
    ("Are classes online or in person?", "Both. Choose offline in Vengadamangalam or online when you apply."),
    ("How do I apply?", "Fill in the admission form. You will get a reference number, and the teacher will contact you on the mobile number you give."),
    ("What about fees and batch timings?", "These are shared directly by the teacher. Ask on WhatsApp or mention it in the form."),
    ("Is my child's information safe?", "Applications are visible only to the teacher and are never shown publicly."),
]

ABOUT = {
    "bio": "[Sample. Write a short introduction in the first person or third person: who Jancy T is, what she enjoys about teaching mathematics, and who she teaches.]",
    "experience": "[Add years of experience and where she has taught.]",
    "philosophy": "[Sample. Write her teaching philosophy in two or three sentences.]",
    "achievements": [],  # e.g. ["Rank holder, University of ..."]. Add only real achievements.
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
        "classes": "6th to 12th",
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
