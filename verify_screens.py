import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ARTIFACT_DIR = Path(r"C:\Users\PrimePC\.gemini\antigravity\brain\b87a8685-5fa5-46c8-989b-033b2ff2441d")
LOCAL_DIR = Path(r"C:\Users\PrimePC\Desktop\Byte froce\screenshots")
LOCAL_DIR.mkdir(parents=True, exist_ok=True)

def save_shots(page, name):
    p1 = ARTIFACT_DIR / f"{name}.png"
    p2 = LOCAL_DIR / f"{name}.png"
    page.screenshot(path=str(p1), full_page=True)
    page.screenshot(path=str(p2), full_page=True)
    print(f"Captured screenshot: {name}.png")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True
        )
        context = browser.new_context(viewport={"width": 1280, "height": 820})
        page = context.new_page()

        # 1. Screen 1: Login Page
        print("Visiting Login...")
        page.goto("http://127.0.0.1:8000/#login")
        page.wait_for_selector("#form-login")
        time.sleep(1)
        save_shots(page, "01_login_screen")

        # Click quick demo 1
        print("Logging in as Demo 1...")
        page.click("#btn-quick-demo1")
        time.sleep(1.5)

        # 2. Screen 2: Dashboard
        print("Visiting Dashboard...")
        page.wait_for_selector(".readiness-gauge-box")
        time.sleep(1.5)
        save_shots(page, "02_dashboard_screen")

        # 3. Screen 3: Unified Profile
        print("Visiting Profile...")
        page.goto("http://127.0.0.1:8000/#profile")
        page.wait_for_selector(".custom-table")
        time.sleep(1.5)
        save_shots(page, "03_profile_screen")

        # 4. Screen 4: Assessments
        print("Visiting Assessments...")
        page.goto("http://127.0.0.1:8000/#assessments")
        page.wait_for_selector("#btn-submit-assessment")
        time.sleep(1.5)
        save_shots(page, "04_assessments_screen")

        # 5. Screen 5: Skill-Gap Matrix
        print("Visiting Skill Gaps...")
        page.goto("http://127.0.0.1:8000/#skill-gaps")
        page.wait_for_selector("#select-role")
        time.sleep(1.5)
        save_shots(page, "05_skill_gaps_screen")

        # 6. Screen 6: Project Readiness
        print("Visiting Project Readiness...")
        page.goto("http://127.0.0.1:8000/#project-readiness")
        page.wait_for_selector(".stat-card")
        time.sleep(1.5)
        save_shots(page, "06_project_readiness_screen")

        # 7. Screen 7: Interview Readiness
        print("Visiting Interview Readiness...")
        page.goto("http://127.0.0.1:8000/#interview-readiness")
        page.wait_for_selector(".stat-card")
        time.sleep(1.5)
        save_shots(page, "07_interview_readiness_screen")

        # 8. Screen 8: Action Plan
        print("Visiting Action Plan...")
        page.goto("http://127.0.0.1:8000/#action-plan")
        page.wait_for_selector(".action-item-card")
        time.sleep(1.5)
        save_shots(page, "08_action_plan_screen")

        # 9. Screen 9: Privacy Settings
        print("Visiting Privacy Settings...")
        page.goto("http://127.0.0.1:8000/#privacy")
        page.wait_for_selector("#btn-export-data")
        time.sleep(1.5)
        save_shots(page, "09_privacy_screen")

        # 10. Scenario T10: Mobile Responsive Viewport (375x812 iPhone X)
        print("Testing Mobile Narrow Screen (T10)...")
        mobile_context = browser.new_context(viewport={"width": 375, "height": 812})
        m_page = mobile_context.new_page()
        # Set token in local storage
        token = page.evaluate("localStorage.getItem('spa_token')")
        student = page.evaluate("localStorage.getItem('spa_student')")
        m_page.goto("http://127.0.0.1:8000/#dashboard")
        m_page.evaluate(f"localStorage.setItem('spa_token', '{token}'); localStorage.setItem('spa_student', '{student}');")
        m_page.goto("http://127.0.0.1:8000/#dashboard")
        time.sleep(1.5)
        save_shots(m_page, "10_mobile_responsive_t10")

        browser.close()
        print("All screen verifications and captures completed successfully!")

if __name__ == "__main__":
    main()
