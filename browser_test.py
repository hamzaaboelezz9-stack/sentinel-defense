import os
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

root = Path(__file__).resolve().parents[1]
base = os.environ.get("SENTINEL_TEST_URL", "http://127.0.0.1:8765")
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="/usr/bin/chromium", headless=True, args=["--no-sandbox"]
    )
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base)
    page.get_by_label("Username").fill("administrator")
    page.get_by_label("Password").fill("local-validation-passphrase")
    page.get_by_role("button", name="Sign in", exact=True).click()
    page.get_by_role("button", name="Brute force", exact=True).wait_for()
    assert page.request.post(base + "/api/v1/reset").status == 200
    page.get_by_role("button", name="Brute force", exact=True).click()
    expect(page.locator(".tableWrap tbody tr")).to_have_count(6)
    page.get_by_role("button", name="Investigations", exact=False).first.click()
    page.get_by_label("Incident severity").select_option("critical")
    page.get_by_label("Classification", exact=True).select_option("confirmed")
    page.get_by_label("Analyst findings").fill("Synthetic evidence reviewed.")
    page.get_by_role("button", name="Save investigation").click()
    page.locator("p.timeline").filter(
        has_text="Synthetic evidence reviewed."
    ).wait_for()
    page.get_by_role("button", name="AI Laboratory", exact=False).click()
    page.get_by_role("button", name="Run reproducible evaluation").click()
    page.get_by_text("Confusion matrix [TN, FP; FN, TP]", exact=True).wait_for()
    page.get_by_role("button", name="Response assistant", exact=False).first.click()
    expect(
        page.get_by_text("Repeated authentication failures", exact=False)
    ).to_be_visible()
    page.get_by_role("button", name="Administration", exact=False).first.click()
    page.get_by_role("button", name="Verify evidence integrity").click()
    expect(page.locator("pre")).to_contain_text('"valid": true')
    page.get_by_role("button", name="Reports", exact=False).first.click()
    assert (
        page.request.get(base + "/api/v1/export/pdf?kind=technical")
        .body()
        .startswith(b"%PDF")
    )
    page.get_by_role("button", name="Overview", exact=False).first.click()
    page.screenshot(path=str(root / "docs/overview.png"), full_page=True)
    page.goto(base + "/demo/?demo=1")
    page.evaluate("localStorage.clear()")
    page.route("**/api/v1/**", lambda route: route.abort())
    page.reload()
    page.get_by_role("button", name="Password spray", exact=True).click()
    page.get_by_role("button", name="Investigations", exact=False).first.click()
    page.get_by_text("Incident queue", exact=False).wait_for()
    expect(page.locator(".incident")).to_have_count(2)
    page.reload()
    expect(page.locator(".incident")).to_have_count(2)
    page.get_by_role("button", name="Overview", exact=False).first.click()
    expect(page.locator(".metric strong").first).to_have_text("6")
    page.get_by_role("button", name="AI Laboratory", exact=False).first.click()
    page.get_by_role("button", name="Run reproducible evaluation").click()
    expect(
        page.get_by_text("Confusion matrix [TN, FP; FN, TP]", exact=True)
    ).to_be_visible()
    page.get_by_role("button", name="Engineering demo", exact=False).first.click()
    page.on("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Reset demonstration").click()
    page.get_by_role("button", name="Overview", exact=False).first.click()
    expect(page.locator(".metric strong").first).to_have_text("0")
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_function("document.documentElement.scrollWidth<=innerWidth")
    assert not errors, errors
    browser.close()
    print(
        "PASS: connected login, generation, investigation save, AI evaluation, screenshot; offline generation, persistence, mobile layout; no JS errors."
    )
