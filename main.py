import os
import subprocess
import threading
import time
import psutil
import logging
import platform
from colorama import Fore, Style, init

init(autoreset=True)

AEGISUM_CLI = "aegisum-cli.exe"
MINING_DELAY = 2
LOG_FILE = "miner.log"
running = False

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

def clear_terminal():
    os.system("cls" if platform.system() == "Windows" else "clear")

def get_wallet_address():
    try:
        result = subprocess.check_output([AEGISUM_CLI, "getnewaddress"], text=True).strip()
        return result
    except subprocess.CalledProcessError as e:
        logging.error(f"Error getting wallet address: {e}")
        print("ERROR: Failed to retrieve wallet address. Check Aegisum CLI.")
        return None

def check_balance():
    try:
        result = subprocess.check_output([AEGISUM_CLI, "getbalance"], text=True).strip()
        print(f"Balance: {result} AEG")
        logging.info(f"Checked balance: {result} AEG")
        input("Press Enter to continue...")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to check balance: {e}")
        logging.error(f"Error checking balance: {e}")

def show_status():
    try:
        result = subprocess.check_output([AEGISUM_CLI, "getmininginfo"], text=True)
        print("---- MINING STATUS ----")
        print(result)
        logging.info("Checked mining status")
        input("Press Enter to continue...")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to retrieve mining status: {e}")
        logging.error(f"Error retrieving mining status: {e}")

def monitor_resources():
    while running:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage("/").percent
        clear_terminal()
        print("MINING STATUS - Aegisum Chain")
        print(f"CPU Usage: {cpu_usage}%")
        print(f"RAM Usage: {ram_usage}%")
        print(f"Disk Usage: {disk_usage}%")
        print("Press CTRL+C to stop mining.")
        logging.info(f"CPU: {cpu_usage}%, RAM: {ram_usage}%, Disk: {disk_usage}%")
        time.sleep(5)

def mine():
    global running
    wallet_address = get_wallet_address()
    if not wallet_address:
        print("ERROR: Mining aborted due to wallet issue.")
        return

    print(f"Mining started... Reward Address: {wallet_address}")
    logging.info(f"Mining started with wallet: {wallet_address}")
    running = True

    monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
    monitor_thread.start()

    try:
        while running:
            try:
                subprocess.run([AEGISUM_CLI, "generatetoaddress", "1", wallet_address], check=True)
                print("Block mined successfully!")
                logging.info("Block mined successfully")
                time.sleep(MINING_DELAY)
            except subprocess.CalledProcessError as e:
                print(f"ERROR: Mining failed: {e}")
                logging.error(f"Mining error: {e}")
                print("Retrying in 5 seconds...")
                time.sleep(5)
    except KeyboardInterrupt:
        stop_mining()

def stop_mining():
    global running
    running = False
    print("Mining stopped.")
    logging.info("Mining stopped")
    time.sleep(2)

def view_logs():
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
        with open(LOG_FILE, "r") as log_file:
            print("\n--- Mining Log ---")
            print(log_file.read())
        input("Press Enter to continue...")
    else:
        print("No logs found or log file is empty.")
        input("Press Enter to continue...")

def menu():
    while True:
        clear_terminal()
        print("\nAegisum Mining Control Panel")
        print("1. Start Mining")
        print("2. Stop Mining")
        print("3. Check Wallet Balance")
        print("4. Show Mining Status")
        print("5. View Logs")
        print("6. Exit")
        
        choice = input("Select an option: ")

        if choice == "1":
            if not running:
                threading.Thread(target=mine, daemon=True).start()
            else:
                print("Mining is already running!")
        elif choice == "2":
            stop_mining()
        elif choice == "3":
            check_balance()
        elif choice == "4":
            show_status()
        elif choice == "5":
            view_logs()
        elif choice == "6":
            stop_mining()
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    menu()
