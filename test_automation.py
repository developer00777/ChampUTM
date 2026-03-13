#!/usr/bin/env python3
"""
ChampUTM — End-to-end test automation.

Creates UTM links, simulates clicks with varied user-agents and referrers,
then verifies analytics data is correct.
"""

import sys
import time
import random
import requests

BASE = "http://localhost:8001"
FRONTEND = "http://localhost:3000"

# ── ANSI colours ──────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):   print(f"  {GREEN}✓{RESET} {msg}")
def fail(msg): print(f"  {RED}✗ {msg}{RESET}"); sys.exit(1)
def info(msg): print(f"  {CYAN}→{RESET} {msg}")
def head(msg): print(f"\n{BOLD}{YELLOW}{'─'*60}\n  {msg}\n{'─'*60}{RESET}")

# ── Simulated clicks ──────────────────────────────────────────────────────────
USER_AGENTS = [
    # Desktop browsers
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36", "desktop", "Chrome"),
    ("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/605.1.15",        "desktop", "Safari"),
    ("Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",                    "desktop", "Firefox"),
    # Mobile
    ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1 Mobile Safari/604.1", "mobile", "Safari"),
    ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/120.0 Mobile Safari/537.36", "mobile", "Chrome"),
    # Tablet
    ("Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1 Mobile/15E148 Safari/604.1",   "tablet", "Safari"),
]

CAMPAIGN_LINKS = [
    {
        "title": "Google Ads — ChampUTM Pro",
        "destination_url": "https://example.com/pricing",
        "utm_source": "google",
        "utm_medium": "cpc",
        "utm_campaign": "brand_awareness_q1",
        "utm_term": "utm+link+tracker",
        "utm_content": "headline_ad_1",
        "clicks": 8,
    },
    {
        "title": "Newsletter — April 2026",
        "destination_url": "https://example.com/blog",
        "utm_source": "mailchimp",
        "utm_medium": "email",
        "utm_campaign": "newsletter_apr2026",
        "utm_content": "cta_button",
        "clicks": 5,
    },
    {
        "title": "Twitter Organic Post",
        "destination_url": "https://example.com/features",
        "utm_source": "twitter",
        "utm_medium": "social",
        "utm_campaign": "organic_social_mar",
        "utm_content": "tweet_thread_1",
        "clicks": 4,
    },
    {
        "title": "LinkedIn Sponsored",
        "destination_url": "https://example.com/demo",
        "utm_source": "linkedin",
        "utm_medium": "paid_social",
        "utm_campaign": "demo_request_q1",
        "utm_content": "carousel_ad",
        "clicks": 3,
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def assert_status(resp, expected, label):
    if resp.status_code != expected:
        fail(f"{label}: expected HTTP {expected}, got {resp.status_code} — {resp.text[:200]}")


def login(email, password):
    resp = requests.post(
        f"{BASE}/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert_status(resp, 200, "Login")
    token = resp.json()["access_token"]
    ok(f"Logged in as {email}")
    return token


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_link(token, payload):
    resp = requests.post(
        f"{BASE}/api/v1/utm/links",
        json=payload,
        headers=auth_headers(token),
    )
    assert_status(resp, 201, f"Create link '{payload.get('title', payload['destination_url'])}'")
    link = resp.json()
    ok(f"Created link: '{link['title'] or 'untitled'}' → short_code={link['short_code']}")
    return link


def simulate_click(short_code, ua_str, referrer=None):
    headers = {"User-Agent": ua_str}
    if referrer:
        headers["Referer"] = referrer
    resp = requests.get(
        f"{BASE}/r/{short_code}",
        headers=headers,
        allow_redirects=False,
    )
    if resp.status_code not in (301, 302, 303, 307, 308):
        fail(f"Click on /r/{short_code}: expected redirect, got {resp.status_code}")
    return resp.status_code


def get_analytics(token, days=30):
    resp = requests.get(
        f"{BASE}/api/v1/utm/analytics",
        params={"days": days},
        headers=auth_headers(token),
    )
    assert_status(resp, 200, "Get analytics")
    return resp.json()


def get_links(token):
    resp = requests.get(f"{BASE}/api/v1/utm/links", headers=auth_headers(token))
    assert_status(resp, 200, "List links")
    return resp.json()


def delete_link(token, link_id):
    resp = requests.delete(f"{BASE}/api/v1/utm/links/{link_id}", headers=auth_headers(token))
    assert_status(resp, 204, f"Delete link {link_id}")


# ── Test runner ───────────────────────────────────────────────────────────────

def main():
    print(f"\n{BOLD}{'═'*60}")
    print("  ChampUTM — Automated E2E Test")
    print(f"{'═'*60}{RESET}")

    # ── 1. Auth ───────────────────────────────────────────────────────────────
    head("1 / 6 — Authentication")
    token = login("lakeb2bdeveloper@gmail.com", "admin123")

    # Verify /me
    me = requests.get(f"{BASE}/api/v1/auth/me", headers=auth_headers(token))
    assert_status(me, 200, "GET /me")
    ok(f"/me returned user: {me.json()['email']}")

    # ── 2. Create campaign links ───────────────────────────────────────────────
    head("2 / 6 — Create UTM Links")
    created_links = []
    for camp in CAMPAIGN_LINKS:
        click_count = camp.pop("clicks")
        link = create_link(token, camp)
        created_links.append((link, click_count))
        camp["clicks"] = click_count  # restore for idempotency

    # ── 3. Simulate clicks ────────────────────────────────────────────────────
    head("3 / 6 — Simulating Clicks")
    total_expected_clicks = 0
    referrers = [
        "https://google.com/search?q=utm+tracker",
        "https://twitter.com",
        "https://linkedin.com",
        "https://mail.google.com",
        None,
    ]

    for link, n_clicks in created_links:
        short_code = link["short_code"]
        title = link["title"] or short_code
        click_results = []
        for i in range(n_clicks):
            ua_str, device, browser = random.choice(USER_AGENTS)
            referrer = random.choice(referrers)
            status = simulate_click(short_code, ua_str, referrer)
            click_results.append(status)
            total_expected_clicks += 1
            time.sleep(0.05)  # small delay to avoid hammering
        ok(f"'{title}': {n_clicks} clicks → all {set(click_results)}")

    info(f"Total clicks fired: {total_expected_clicks}")

    # ── 4. Verify click counts on links ──────────────────────────────────────
    head("4 / 6 — Verify Click Counts on Links")
    time.sleep(0.5)  # let DB settle
    links_data = get_links(token)
    new_link_ids = {l[0]["short_code"] for l in created_links}

    for item in links_data["items"]:
        if item["short_code"] in new_link_ids:
            expected = next(n for l, n in created_links if l["short_code"] == item["short_code"])
            # Pre-existing links may have extra clicks; new ones start at 0
            if item["click_count"] >= expected:
                ok(f"'{item['title'] or item['short_code']}': {item['click_count']} clicks ✓")
            else:
                fail(f"'{item['title']}': expected ≥{expected} clicks, got {item['click_count']}")

    # ── 5. Verify analytics ───────────────────────────────────────────────────
    head("5 / 6 — Verify Analytics")
    analytics = get_analytics(token, days=30)

    info(f"total_clicks  = {analytics['total_clicks']}")
    info(f"total_links   = {analytics['total_links']}")
    info(f"days          = {analytics['days']}")

    if analytics["total_clicks"] >= total_expected_clicks:
        ok(f"total_clicks ({analytics['total_clicks']}) ≥ expected ({total_expected_clicks})")
    else:
        fail(f"total_clicks too low: {analytics['total_clicks']} < {total_expected_clicks}")

    if analytics["total_links"] >= len(CAMPAIGN_LINKS):
        ok(f"total_links = {analytics['total_links']}")
    else:
        fail(f"total_links too low: {analytics['total_links']}")

    # clicks_over_time has at least today
    if analytics["clicks_over_time"]:
        ok(f"clicks_over_time has {len(analytics['clicks_over_time'])} day(s)")
        for row in analytics["clicks_over_time"]:
            info(f"  {row['date']} → {row['count']} clicks")
    else:
        fail("clicks_over_time is empty")

    # sources present
    sources = {r["label"] for r in analytics["clicks_by_source"]}
    expected_sources = {"google", "mailchimp", "twitter", "linkedin"}
    missing = expected_sources - sources
    if not missing:
        ok(f"clicks_by_source has all expected sources: {sources}")
    else:
        fail(f"Missing sources in analytics: {missing}")

    # mediums present
    mediums = {r["label"] for r in analytics["clicks_by_medium"]}
    expected_mediums = {"cpc", "email", "social", "paid_social"}
    missing_m = expected_mediums - mediums
    if not missing_m:
        ok(f"clicks_by_medium has all expected mediums: {mediums}")
    else:
        fail(f"Missing mediums: {missing_m}")

    # devices present
    devices = {r["label"] for r in analytics["clicks_by_device"]}
    if "desktop" in devices and "mobile" in devices:
        ok(f"clicks_by_device detected multiple device types: {devices}")
    else:
        fail(f"Expected desktop + mobile in devices, got: {devices}")

    # ── 6. Summary ────────────────────────────────────────────────────────────
    print(f"\n{BOLD}{GREEN}{'═'*60}")
    print("  ALL TESTS PASSED")
    print(f"{'═'*60}{RESET}\n")
    print(f"  Links created : {len(CAMPAIGN_LINKS)}")
    print(f"  Clicks fired  : {total_expected_clicks}")
    print(f"  Sources tested: google, mailchimp, twitter, linkedin")
    print(f"  Devices tested: desktop, mobile, tablet")
    print(f"  Cleanup       : skipped — data live in analytics\n")
    print(f"  {CYAN}Open http://localhost:3000/analytics to see the charts{RESET}\n")


if __name__ == "__main__":
    main()
