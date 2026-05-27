from fastapi import FastAPI
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
import re

app = FastAPI()


# =====================================================
# REQUEST MODEL
# =====================================================

class EmailRequest(BaseModel):
    first_name: str
    last_name: str
    domain: str
    linkedin_url: str | None = None


# =====================================================
# MAIN ENDPOINT
# =====================================================

@app.post("/find-email")
def find_email(data: EmailRequest):
    print("==================================================")
    print("NEW EMAIL REQUEST")
    print(f"Person: {data.first_name} {data.last_name}")
    print(f"Domain: {data.domain}")
    print("==================================================\n")

    email = None
    source = None

    with sync_playwright() as p:

        close_browser = False
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            print("Connected to CDP Chrome session")
            print("Browser ready\n")
        except Exception as e:

            print("Launching headless browser...")
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox"
                ]
            )
            context = browser.new_context(
                viewport={"width": 1400, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                )
            )
            close_browser = True
            print("Browser ready\n")

        # ==========================================
        # TRY 1 — LINKEDIN FINDER
        # ==========================================

        if data.linkedin_url:

            print("[LinkedIn Finder]")
            print("Opening MailMeteor LinkedIn Finder...")

            email = try_linkedin_finder(
                context,
                data.linkedin_url
            )

            if email:
                source = "linkedin"

        # ==========================================
        # TRY 2 — NAME + DOMAIN FINDER
        # ==========================================

        if not email:

            print("[Name+Domain Finder]")
            print("Opening MailMeteor Name+Domain Finder...")

            email = try_name_domain_finder(
                context,
                data.first_name,
                data.last_name,
                data.domain
            )

            if email:
                source = "name_domain"

        if close_browser:
            browser.close()

    # ==========================================
    # FINAL RESPONSE
    # ==========================================

    if email:
        print("FINAL RESULT -> SUCCESS")
        print(f"Source: {source}")
    else:
        print("FINAL RESULT -> FAILED")
    print("==================================================")

    if email:
        return {
            "success": True,
            "email": email,
            "source": source
        }

    return {
        "success": False,
        "email": None,
        "source": None
    }


# =====================================================
# LINKEDIN FINDER
# =====================================================

def try_linkedin_finder(context, linkedin_url):

    page = context.new_page()

    try:

        page.goto(
            "https://mailmeteor.com/tools/linkedin-email-finder",
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(5000)

        # Wait for LinkedIn input
        input_box = page.wait_for_selector(
            'input[placeholder*="LinkedIn"]',
            timeout=30000
        )

        input_box.click()

        page.wait_for_timeout(1000)

        # Clear field
        input_box.press("Control+A")
        input_box.press("Backspace")

        page.wait_for_timeout(500)

        # Human typing
        input_box.type(linkedin_url, delay=80)
        print("LinkedIn URL entered")

        page.wait_for_timeout(1500)

        # Find Email button
        button = page.locator(
            'button:has-text("FIND EMAIL")'
        ).first

        button.click()
        print("Search submitted")
        print("Scanning page for emails...")

        page.wait_for_timeout(15000)

        text_content = page.locator("body").inner_text()

        if "No results found" in text_content:
            print("No results found\n")
            page.close()
            return None

        emails = re.findall(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            text_content
        )
        
        valid_emails = [e for e in emails if not e.lower().endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2'))]

        if valid_emails:

            found_email = valid_emails[0]

            print(f"Email found: {found_email}\n")

            page.close()

            return found_email

        page.close()

        return None

    except Exception as e:

        print(f"LinkedIn finder error: {e}\n")

        page.close()

        return None


# =====================================================
# NAME + DOMAIN FINDER
# =====================================================

def try_name_domain_finder(
    context,
    first_name,
    last_name,
    domain
):

    page = context.new_page()

    try:

        full_name = f"{first_name} {last_name}".strip()

        page.goto(
            "https://mailmeteor.com/tools/email-finder",
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(5000)

        # ======================================
        # NAME FIELD
        # ======================================

        name_input = page.locator('input#fullName').first
        name_input.click(timeout=15000)

        page.wait_for_timeout(500)

        name_input.press("Control+A")
        name_input.press("Backspace")

        page.wait_for_timeout(500)

        name_input.type(full_name, delay=80)
        print("Name entered")

        # ======================================
        # DOMAIN FIELD
        # ======================================

        domain_input = page.locator('input#domain').first
        domain_input.click(timeout=15000)

        page.wait_for_timeout(500)

        domain_input.press("Control+A")
        domain_input.press("Backspace")

        page.wait_for_timeout(500)

        domain_input.type(domain, delay=80)
        print("Domain entered")

        page.wait_for_timeout(1500)

        # ======================================
        # FIND BUTTON
        # ======================================

        button = page.locator(
            'button:has-text("FIND EMAIL")'
        ).first

        button.click()
        print("Search submitted")
        print("Scanning page for emails...")

        page.wait_for_timeout(15000)

        text_content = page.locator("body").inner_text()

        if "No results found" in text_content:
            print("No results found\n")
            page.close()
            return None

        emails = re.findall(
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            text_content
        )
        
        valid_emails = [e for e in emails if not e.lower().endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2'))]

        if valid_emails:

            found_email = valid_emails[0]

            print(f"Email found: {found_email}\n")

            page.close()

            return found_email

        page.close()

        return None

    except Exception as e:

        print(f"Name+domain finder error: {e}\n")

        page.close()

        return None
