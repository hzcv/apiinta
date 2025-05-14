import time
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired
from getpass import getpass

# ---------------- CONFIG ----------------
OWNER_USERNAMES = ["owner_username1", "owner_username2"]  # Replace with real usernames
REPLY_DELAY = 2  # seconds
REPLY_TEXT = "OYY MSG MAT KAR"

# ---------------- MAIN BOT ----------------
cl = Client()
owner_ids = []

def ask_credentials():
    username = input("Enter your Instagram username: ")
    password = getpass("Enter your Instagram password: ")
    return username, password

def handle_challenge(username):
    print("[*] Login triggered a challenge. Trying to send code to email...")
    try:
        cl.challenge_resolve(auto=True)
        code = input("[?] Enter the security code sent to your email: ").strip()
        cl.challenge_send_security_code(code)
    except Exception as e:
        print("[-] Failed to resolve challenge:", e)
        exit()

def login_flow():
    username, password = ask_credentials()
    try:
        cl.login(username, password)
    except ChallengeRequired:
        handle_challenge(username)
    except Exception as e:
        print("[-] Login failed:", e)
        exit()
    
    print(f"[+] Logged in as {username}")
    return cl.user_id_from_username(username)

def resolve_owner_ids():
    for uname in OWNER_USERNAMES:
        try:
            uid = cl.user_id_from_username(uname)
            owner_ids.append(uid)
        except:
            print(f"[-] Failed to get user ID for owner '{uname}'")

def monitor_groups(self_id):
    print("[✓] Monitoring group chats...")
    replied_message_ids = {}

    while True:
        threads = cl.direct_threads()
        for thread in threads:
            if len(thread.users) <= 1:
                continue  # Skip if not a group

            thread_id = thread.id
            messages = cl.direct_messages(thread_id, amount=10)
            messages.reverse()

            for msg in messages:
                sender_id = msg.user_id
                msg_id = msg.id

                if sender_id in owner_ids or sender_id == self_id:
                    continue

                if msg_id in replied_message_ids.get(thread_id, []):
                    continue

                # Track that we replied to this message
                replied_message_ids.setdefault(thread_id, []).append(msg_id)

                sender_username = cl.user_info(sender_id).username
                reply = f"@{sender_username} {REPLY_TEXT}"

                cl.direct_send(reply, thread_ids=[thread_id])
                print(f"[✓] Replied to @{sender_username} in thread {thread_id}")
                time.sleep(REPLY_DELAY)

        time.sleep(5)

# ---------------- START ----------------
if __name__ == "__main__":
    self_user_id = login_flow()
    resolve_owner_ids()
    monitor_groups(self_user_id)
