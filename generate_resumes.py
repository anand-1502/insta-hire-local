import os
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

roles = [
    "Waiter", "Chef", "Bartender", "Hostess", "Dishwasher", "Line Cook",
    "Sous Chef", "Pastry Chef", "Restaurant Manager", "Barista",
    "Busser", "Food Runner", "Catering Staff", "Sommelier", "Kitchen Porter"
]

skills_by_role = {
    "Waiter": ["POS systems", "cocktails", "wine service", "customer service"],
    "Chef": ["menu planning", "Italian cuisine", "French cuisine", "kitchen management"],
    "Bartender": ["craft cocktails", "beer knowledge", "wine knowledge", "mixology"],
    "Hostess": ["customer service", "seating management", "bilingual English/Spanish", "phone etiquette"],
    "Dishwasher": ["kitchen cleaning", "equipment handling", "sanitation"],
    "Line Cook": ["grill", "sauté", "prep work", "timing"],
    "Sous Chef": ["kitchen supervision", "inventory", "training staff"],
    "Pastry Chef": ["pastries", "cakes", "bread", "desserts"],
    "Restaurant Manager": ["team management", "scheduling", "ordering supplies", "customer conflict resolution"],
    "Barista": ["espresso drinks", "latte art", "customer service", "cash handling"],
    "Busser": ["table cleaning", "support wait staff", "refill drinks"],
    "Food Runner": ["plate delivery", "speed", "team coordination"],
    "Catering Staff": ["event setup", "banquets", "large-scale service"],
    "Sommelier": ["wine pairing", "wine cellar management", "fine dining"],
    "Kitchen Porter": ["stocking", "cleaning", "prep support"]
}

names_first = ["John", "Jane", "Mike", "Sara", "Alex", "Emily", "Chris", "Laura", "David", "Sophia"]
names_last = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Lopez", "Wilson", "Taylor"]

os.makedirs("data/resumes", exist_ok=True)

for i in range(50):
    # Random candidate details
    first = random.choice(names_first)
    last = random.choice(names_last)
    name = f"{first} {last} {i}"
    role = random.choice(roles)
    years_exp = random.randint(1, 10)
    skills = random.sample(skills_by_role[role], k=min(3, len(skills_by_role[role])))

    # Resume content
    resume_text = (
        f"Resume - {name}\n\n"
        f"Role: {role}\n"
        f"Experience: {years_exp} years\n"
        f"Key Skills: {', '.join(skills)}\n\n"
        f"{first} has worked in various restaurants and gained valuable experience in "
        f"{', '.join(skills)}. Looking for opportunities to contribute as a {role}."
    )

    # Save as PDF
    file_path = f"data/resumes/{name.replace(' ', '_')}.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    text_object = c.beginText(72, 720)
    text_object.setFont("Helvetica", 11)
    for line in resume_text.split("\n"):
        text_object.textLine(line)
    c.drawText(text_object)
    c.save()

    print(f"Created {file_path}")
