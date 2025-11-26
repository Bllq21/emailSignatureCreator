from flask import Flask, request, send_file, render_template, redirect, url_for, flash, session, make_response, jsonify
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
import os
from functools import wraps
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")

COMPANY_DOMAIN = os.getenv("COMPANY_DOMAIN", "example.com")
PHONE_PREFIX = os.getenv("PHONE_PREFIX", "+1")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

TEMPLATE_DIR = "static/templates"
OUTPUT_DIR = "static/output"
ACTIVE_TEMPLATE_FILE = "static/active_template.txt"
DEFAULT_TEMPLATE = "static/templates/default_template.png"

os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

TRANSLATIONS = {
    "en": {
        "app_title": "Email Signature Generator",
        "login_title": "Email Signature Generator",
        "login_subtitle": "Enter your institutional email to continue",
        "email_label": "Email:",
        "email_placeholder": f"user@{COMPANY_DOMAIN}",
        "login_btn": "Sign In",
        "name_label": "First Name:",
        "name_placeholder": "Enter your first name",
        "lastname_label": "Last Name:",
        "lastname_placeholder": "Enter your last name",
        "title_label": "Title:",
        "area_label": "Department:",
        "area_placeholder": "Select a department",
        "position_label": "Position:",
        "position_placeholder": "Select a position",
        "phone_label": "Phone:",
        "phone_placeholder": "Enter phone number",
        "generate_btn": "Generate Signature",
        "add_option": "Add",
        "signature_title": "Generated Signature",
        "download_btn": "Download Signature",
        "logout_btn": "Logout",
        "instructions_title": "Instructions",
        "admin_panel": "Admin Panel",
        "admin_login": "Admin Login",
        "admin_email_label": "Email:",
        "admin_email_placeholder": "admin@company.com",
        "admin_password_label": "Password:",
        "admin_password_placeholder": "Password",
        "admin_login_btn": "Sign In",
        "upload_template": "Upload New Template",
        "template_file": "Template File:",
        "upload_btn": "Upload Template",
        "existing_templates": "Existing Templates",
        "set_active": "Set as Active",
        "active": "Active",
        "delete": "Delete",
        "access_denied_title": "Access Denied",
        "access_denied_msg": "You do not have permission to access this page. Please log in first.",
        "go_home": "Go to Home Page",
        "invalid_email": "Invalid email. Your email must belong to the organization.",
        "invalid_credentials": "Invalid credentials. Please try again.",
        "no_template": "No active template found. Please upload a template.",
        "template_uploaded": "Template uploaded successfully.",
        "template_deleted": "Template deleted successfully.",
        "template_not_found": "Template not found.",
        "invalid_format": "Invalid file format. Only PNG/JPG accepted.",
        "language": "Language",
        "new_signature": "New Signature",
        "admin_link": "Admin Panel",
    },
    "es": {
        "app_title": "Generador de Firma de Correo",
        "login_title": "Generador de Firma de Correo",
        "login_subtitle": "Introduce tu correo institucional para continuar",
        "email_label": "Correo Electrónico:",
        "email_placeholder": f"usuario@{COMPANY_DOMAIN}",
        "login_btn": "Iniciar Sesión",
        "name_label": "Nombre:",
        "name_placeholder": "Ingresa tu nombre",
        "lastname_label": "Apellido:",
        "lastname_placeholder": "Ingresa tu apellido",
        "title_label": "Título:",
        "area_label": "Área:",
        "area_placeholder": "Selecciona un área",
        "position_label": "Posición:",
        "position_placeholder": "Selecciona una posición",
        "phone_label": "Teléfono:",
        "phone_placeholder": "Ingresa el número",
        "generate_btn": "Generar Firma",
        "add_option": "Agregar",
        "signature_title": "Firma Generada",
        "download_btn": "Descargar Firma",
        "logout_btn": "Salir",
        "instructions_title": "Instrucciones",
        "admin_panel": "Panel de Administración",
        "admin_login": "Inicio de Sesión Administrativo",
        "admin_email_label": "Correo Electrónico:",
        "admin_email_placeholder": "admin@empresa.com",
        "admin_password_label": "Contraseña:",
        "admin_password_placeholder": "Contraseña",
        "admin_login_btn": "Iniciar Sesión",
        "upload_template": "Subir Nueva Plantilla",
        "template_file": "Archivo de Plantilla:",
        "upload_btn": "Subir Plantilla",
        "existing_templates": "Plantillas Existentes",
        "set_active": "Establecer como Activo",
        "active": "Activo",
        "delete": "Eliminar",
        "access_denied_title": "Acceso Denegado",
        "access_denied_msg": "No tienes permiso para acceder a esta página. Por favor, inicia sesión primero.",
        "go_home": "Ir a la página de inicio",
        "invalid_email": "Correo inválido. Tu correo debe pertenecer a la organización.",
        "invalid_credentials": "Credenciales inválidas. Por favor, inténtalo de nuevo.",
        "no_template": "No se encontró una plantilla activa. Por favor, sube una plantilla.",
        "template_uploaded": "Plantilla subida con éxito.",
        "template_deleted": "Plantilla eliminada con éxito.",
        "template_not_found": "La plantilla no existe.",
        "invalid_format": "Formato de archivo no válido. Solo se aceptan PNG/JPG.",
        "language": "Idioma",
        "new_signature": "Nueva Firma",
        "admin_link": "Panel de Administración",
    },
}

TITLES = {
    "en": ["Mr.", "Ms.", "Mrs.", "Dr.", "Prof.", "Eng.", "Lic.", "Arq."],
    "es": ["Sr.", "Sra.", "Srta.", "Dr.", "Dra.", "Ing.", "Lic.", "Arq.", "Abg.", "Msc."],
}

def get_text(key, lang="en"):
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

def get_lang():
    lang = request.args.get("lang", session.get("lang", "en"))
    if lang not in ("en", "es"):
        lang = "en"
    session["lang"] = lang
    return lang

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("acceso_denegado", lang=get_lang()))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in") or session.get("user_type") != "admin":
            return redirect(url_for("acceso_denegado", lang=get_lang()))
        return f(*args, **kwargs)
    return decorated_function

def get_active_template():
    if os.path.exists(ACTIVE_TEMPLATE_FILE):
        with open(ACTIVE_TEMPLATE_FILE, "r") as file:
            template_name = file.read().strip()
            template_path = os.path.join(TEMPLATE_DIR, template_name)
            if os.path.exists(template_path):
                return template_path
    default_template_path = os.path.join(TEMPLATE_DIR, "default_template.png")
    if os.path.exists(default_template_path):
        return default_template_path
    return None

def load_allowed_emails():
    try:
        with open("static/cuentas.json", "r") as file:
            data = json.load(file)
        return [entry["email"] for entry in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@app.route("/lang/<lang>")
def switch_lang(lang):
    if lang in ("en", "es"):
        session["lang"] = lang
    referrer = request.referrer or ""
    if "/generate" in referrer:
        return redirect(url_for("index", lang=lang))
    return redirect(referrer or url_for("home", lang=lang))

@app.route("/")
def home():
    lang = get_lang()
    return render_template("login.html", t=TRANSLATIONS[lang], lang=lang, titles=TITLES[lang])

@app.route("/login", methods=["POST"])
def login():
    lang = get_lang()
    email = request.form.get("email", "")
    allowed_domains = COMPANY_DOMAIN.split(",")
    if email and any(email.endswith(f"@{d.strip()}") for d in allowed_domains):
        allowed_emails = load_allowed_emails()
        if email in allowed_emails:
            session["logged_in"] = True
            session["email"] = email
            session["user_type"] = "admin" if email == ADMIN_EMAIL else "normal"
            return redirect(url_for("index", lang=lang))
        else:
            flash(get_text("invalid_email", lang))
    else:
        flash(get_text("invalid_email", lang))
    return redirect(url_for("home", lang=lang))

@app.route("/acceso_denegado")
def acceso_denegado():
    lang = get_lang()
    return render_template("acceso_denegado.html", t=TRANSLATIONS[lang], lang=lang)

@app.route("/index")
@login_required
def index():
    lang = get_lang()
    user_email = session.get("email", "")
    return render_template("index.html", t=TRANSLATIONS[lang], lang=lang,
                           email=user_email, titles=TITLES[lang],
                           phone_prefix=PHONE_PREFIX)

@app.route("/generate", methods=["POST"])
def generate_signature():
    lang = get_lang()
    data = request.form
    name = data.get("name", "").title()
    lastname = data.get("lastname", "").title()
    title = data.get("title", "")
    position = data.get("position", "")
    phone = data.get("phone", "")
    email = data.get("email", "")
    area = data.get("area", "")

    if phone and not any(phone.startswith(p) for p in ["+", "00"]):
        phone = f"{PHONE_PREFIX} {phone}"

    active_template_path = get_active_template()
    if not active_template_path or not os.path.exists(active_template_path):
        flash(get_text("no_template", lang))
        return redirect(url_for("index", lang=lang))

    template = Image.open(active_template_path).convert("RGBA")
    draw = ImageDraw.Draw(template)
    template_width, template_height = template.size
    reference_width = 10938
    reference_height = 3644
    scale_x = template_width / reference_width
    scale_y = template_height / reference_height
    min_scale = max(scale_x, scale_y, 0.5)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(BASE_DIR, "Pluto-Regular.otf")
    if not os.path.exists(font_path):
        font_path = os.path.join(BASE_DIR, "Ubuntu-Regular.ttf")

    font_large_size = max(int(95 * min_scale), 30)
    font_medium_size = max(int(65 * min_scale), 20)
    font_large = ImageFont.truetype(font_path, font_large_size)
    font_medium = ImageFont.truetype(font_path, font_medium_size)

    phone_icon_path = "phone_icon.png"
    email_icon_path = "email_icon.png"

    y_position = max(int(200 * min_scale), 50)
    padding = max(int(35 * min_scale), 15)
    x_start = max(int(1530 * min_scale), 300)
    icon_offset_x = max(int(15 * min_scale), 5)
    icon_offset_y = max(int(5 * min_scale), 2)

    if title or name or lastname:
        text = f"{title} {name} {lastname}".strip()
        draw.text((x_start, y_position), text, fill="#FFA500", font=font_large)
        text_height = font_large.getmask(text).getbbox()[3]
        y_position += text_height + padding

    if position:
        draw.text((x_start, y_position), position, fill="#000000", font=font_medium)
        text_height = font_medium.getmask(position).getbbox()[3]
        y_position += text_height + padding + max(int(20 * min_scale), 5)

    if area:
        draw.text((x_start, y_position), area, fill="#000000", font=font_medium)
        text_height = font_medium.getmask(area).getbbox()[3]
        y_position += text_height + padding + max(int(40 * min_scale), 10)

    email_x_offset = max(int(100 * min_scale), 20)
    phone_x_offset = max(int(100 * min_scale), 20)

    if email:
        icon_size = max(int(65 * min_scale), 20)
        text_height = font_medium.getmask(email).getbbox()[3] if email else 0
        if os.path.exists(email_icon_path):
            email_icon = Image.open(email_icon_path).resize((icon_size, icon_size))
            icon_x_position = (x_start - (icon_size + icon_offset_x)) + email_x_offset
            icon_y_position = y_position + (text_height // 2 - icon_size // 2) + icon_offset_y
            template.paste(email_icon, (icon_x_position, icon_y_position), email_icon)
        draw.text((x_start + email_x_offset, y_position), email, fill="#000000", font=font_medium)
        y_position += max(icon_size, text_height) + padding + max(int(40 * min_scale), 10)

    if phone:
        icon_size = max(int(65 * min_scale), 20)
        text_height = font_medium.getmask(phone).getbbox()[3] if phone else 0
        if os.path.exists(phone_icon_path):
            phone_icon = Image.open(phone_icon_path).resize((icon_size, icon_size))
            icon_x_position = (x_start - (icon_size + icon_offset_x)) + phone_x_offset
            icon_y_position = y_position + (text_height // 2 - icon_size // 2) + icon_offset_y
            template.paste(phone_icon, (icon_x_position, icon_y_position), phone_icon)
        draw.text((x_start + phone_x_offset, y_position), phone, fill="#000000", font=font_medium)
        y_position += max(icon_size, text_height) + padding + max(int(40 * min_scale), 10)

    output_filename = f"{name}_{lastname}_firma.png"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    template.save(output_path, format="PNG", dpi=(144, 144))

    image_url = url_for("static", filename=f"output/{output_filename}")
    return render_template("firma.html", t=TRANSLATIONS[lang], lang=lang, image_url=image_url)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():
    lang = get_lang()
    if request.method == "POST":
        if "template" in request.files:
            file = request.files["template"]
            if allowed_file(file.filename):
                file_path = os.path.join(TEMPLATE_DIR, file.filename)
                file.save(file_path)
                flash(get_text("template_uploaded", lang))
            else:
                flash(get_text("invalid_format", lang))
        return redirect(url_for("admin", lang=lang))

    templates = os.listdir(TEMPLATE_DIR)
    thumbnails = [url_for("static", filename=f"templates/{t}") for t in templates]
    active_template = os.path.basename(get_active_template()) if get_active_template() else ""

    return render_template("admin.html", t=TRANSLATIONS[lang], lang=lang,
                           templates=templates, thumbnails=thumbnails,
                           active_template=active_template, zip=zip)

@app.route("/delete_template", methods=["POST"])
@admin_required
def delete_template():
    lang = get_lang()
    template_name = request.form.get("template_name", "")
    file_path = os.path.join(TEMPLATE_DIR, template_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(get_text("template_deleted", lang))
    else:
        flash(get_text("template_not_found", lang))
    return redirect(url_for("admin", lang=lang))

@app.route("/set-template/<template_name>", methods=["POST"])
@admin_required
def set_template(template_name):
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    if not os.path.exists(template_path):
        return "Template not found", 404
    with open(ACTIVE_TEMPLATE_FILE, "w") as file:
        file.write(template_name)
    return redirect(url_for("admin", lang=get_lang()))

@app.route("/adminlogin", methods=["GET", "POST"])
def adminlogin():
    lang = get_lang()
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            session["user_type"] = "admin"
            return redirect(url_for("admin", lang=lang))
        else:
            flash(get_text("invalid_credentials", lang))
    return render_template("adminlogin.html", t=TRANSLATIONS[lang], lang=lang)

@app.route("/logout")
def logout():
    lang = get_lang()
    session.clear()
    return redirect(url_for("home", lang=lang))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
