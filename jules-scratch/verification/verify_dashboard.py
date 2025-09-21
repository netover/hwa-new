import re
from playwright.sync_api import Page, expect

def test_dashboard_and_chat(page: Page):
    """
    Tests that the dashboard loads, receives data, and that the chat is interactive.
    """
    # 1. Arrange: Go to the application's homepage.
    page.goto("http://localhost:8000")

    # 2. Act & Assert: Dashboard Loading
    # Wait for the system status to update from "Conectando..." to "Status: ACTIVE"
    # This confirms the WebSocket connection is working.
    system_status_el = page.locator("#system-status-content")
    expect(system_status_el).to_have_text(re.compile("Status: ACTIVE"), timeout=10000)

    # 3. Act & Assert: Chat Interaction
    chat_input = page.locator("#chat-input")
    send_btn = page.locator("#send-btn")
    chat_window = page.locator("#chat-window")

    # Type a message and send it
    chat_input.fill("Qual o status do job JOB_FINAL_PAYROLL?")
    send_btn.click()

    # Assert that the user's message appeared
    expect(chat_window).to_contain_text("Qual o status do job JOB_FINAL_PAYROLL?")

    # The backend is now fixed. We expect a proper response.
    # The dispatcher should route to the TWS_Monitor, which will use the mock tool.
    expect(chat_window.locator(".bot-message").nth(1)).to_contain_text("jobs_found", timeout=10000)

    # 4. Screenshot: Capture the final state.
    page.screenshot(path="jules-scratch/verification/dashboard_verification_fixed.png")
