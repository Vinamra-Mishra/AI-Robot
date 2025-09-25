
import time
import sys
import os
from collections import deque

def follow_file(filepath):
    """A generator that yields new lines from a file."""
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        return

    # First, print the last N lines of the file
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            last_lines = deque(f, 20)
        for line in last_lines:
            print(line, end='')
    except Exception as e:
        print(f"Error reading initial log content: {e}")

    # Now, seek to the end and tail for new lines
    with open(filepath, "r", encoding="utf-8") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python log_viewer.py <path_to_log_file>")
        sys.exit(1)

    file_to_watch = sys.argv[1]
    
    print(f"--- Tailing log file: {os.path.basename(file_to_watch)} (showing last 20 lines) ---")
    print("" if os.path.getsize(file_to_watch) > 0 else "--- Log file is currently empty ---")
    print("--- Press Ctrl+C to exit ---")

    try:
        for line in follow_file(file_to_watch):
            print(line, end='')
    except KeyboardInterrupt:
        print("\n--- Log viewer stopped ---")
    except Exception as e:
        print(f"An error occurred: {e}")

