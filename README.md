# Email Signature Generator

A Flask-based web application that generates professional email signature images. Users can create customized email signatures with their name, title, position, department, email, and phone number overlay on a company template image.

## Features

- **Bilingual UI** — English and Spanish supported with instant language switching
- **Template Management** — Admin panel to upload, activate, and delete signature templates
- **Dynamic Generation** — Text is rendered on the template using Pillow with proportional scaling
- **Department/Position mapping** — Dropdowns auto-populate based on configured organizational structure (JSON-driven)
- **Email domain validation** — Restrict access to specific institutional email domains
- **Admin authentication** — Separate admin login for template management
- **High-quality output** — PNG images at 144 DPI

## Tech Stack

- **Backend:** Python / Flask
- **Image Processing:** Pillow (PIL)
- **Frontend:** HTML, CSS, JavaScript
- **Templates:** Jinja2

## Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USER/email-signature-generator.git
cd email-signature-generator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the app
python app.py
```

## Configuration

Edit `.env` with your organization's settings:

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Flask session secret | *(required)* |
| `COMPANY_DOMAIN` | Allowed email domain(s) | `example.com` |
| `PHONE_PREFIX` | Country/area code prefix | `+1` |
| `ADMIN_EMAIL` | Admin login email | `admin@example.com` |
| `ADMIN_PASSWORD` | Admin login password | `change-this-password` |

## Usage

1. **User login** — Enter your institutional email
2. **Fill details** — Select title, department, position, enter name, email and phone
3. **Generate** — Click "Generate Signature" to create the PNG image
4. **Download** — Save the image and set it as your email signature

## Adding Templates

1. Log in as admin (`/adminlogin`)
2. Upload a PNG/JPG template image
3. Set it as the active template
4. The text will automatically scale based on the template dimensions

## Project Structure

```
├── app.py                    # Flask application with i18n
├── requirements.txt          # Python dependencies
├── .env.example              # Environment config template
├── static/
│   ├── css/styles.css        # Styles
│   ├── templates/            # Signature template images
│   ├── output/               # Generated signatures
│   ├── posiciones.json       # Department/position data
│   └── cuentas.json          # Allowed email accounts
├── templates/                # HTML templates (Jinja2)
│   ├── login.html
│   ├── index.html
│   ├── firma.html
│   ├── admin.html
│   ├── adminlogin.html
│   └── acceso_denegado.html
└── *.ttf / *.otf             # Font files
```

## License

MIT
