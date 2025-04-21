#!/usr/bin/env python3
"""
Launcher script for the Financial News & Sentiment Analysis application.
This script runs both the backend agent and Streamlit frontend concurrently.
"""

import subprocess
import os
import sys
import webbrowser
import time
import signal
import atexit

# Determine the project root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(ROOT_DIR, "venv", "bin", "python")

# Global process references for cleanup
processes = []

def cleanup():
    """Kill all child processes when the script terminates."""
    for process in processes:
        try:
            if process.poll() is None:  # If process is still running
                print(f"Terminating process: {process.args}")
                process.terminate()
        except Exception as e:
            print(f"Error terminating process: {e}")

# Register cleanup function to run on script exit
atexit.register(cleanup)

# Also catch keyboard interrupts
def signal_handler(sig, frame):
    print("\nCtrl+C detected. Shutting down all processes...")
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def run_backend():
    """Run the backend agent."""
    print("Starting the backend agent...")
    
    backend_process = subprocess.Popen(
        [VENV_PYTHON, "-m", "src.main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,  # Line buffered
    )
    processes.append(backend_process)
    
    # Start a thread to continuously read and print output
    def print_output():
        for line in backend_process.stdout:
            print(f"[BACKEND] {line.strip()}")
    
    from threading import Thread
    output_thread = Thread(target=print_output, daemon=True)
    output_thread.start()
    
    return backend_process

def run_frontend():
    """Run the Streamlit frontend."""
    print("Starting the Streamlit frontend...")
    
    streamlit_process = subprocess.Popen(
        [VENV_PYTHON, "-m", "streamlit", "run", os.path.join("src", "streamlit_app.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,  # Line buffered
    )
    processes.append(streamlit_process)
    
    # Start a thread to continuously read and print output
    def print_output():
        for line in streamlit_process.stdout:
            print(f"[FRONTEND] {line.strip()}")
            # Look for the line that contains the local URL
            if "Local URL: " in line:
                url = line.split("Local URL: ")[1].strip()
                print(f"\n🔗 Access the dashboard at: {url}\n")
                # Open browser automatically after a short delay
                time.sleep(2)
                webbrowser.open(url)
    
    from threading import Thread
    output_thread = Thread(target=print_output, daemon=True)
    output_thread.start()
    
    return streamlit_process

def main():
    """Main function to run both backend and frontend."""
    print("\n=== Financial News & Sentiment Analysis Application ===\n")
    
    # Check for required files
    if not os.path.exists(os.path.join(ROOT_DIR, "config", ".env")):
        print("⚠️ Warning: config/.env file not found! The application may not work correctly.")
        print("Please make sure you have configured all the required API keys (NEWS_API_KEY, LLM_API_KEY, etc.)")
    
    # Start backend process
    backend_process = run_backend()
    
    # Give the backend a moment to initialize
    time.sleep(3)
    
    # Start frontend process
    frontend_process = run_frontend()
    
    print("\n✅ Both backend and frontend are now running!")
    print("Press Ctrl+C to stop both processes and exit.")
    
    # Keep the main thread alive
    try:
        # Monitor child processes and exit if any of them fails
        while True:
            if backend_process.poll() is not None:
                print("⚠️ Backend process has terminated. Shutting down...")
                break
            if frontend_process.poll() is not None:
                print("⚠️ Frontend process has terminated. Shutting down...")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        cleanup()

if __name__ == "__main__":
    main() 