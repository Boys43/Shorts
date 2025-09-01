import time
import sys

statuses = [
    "Working...",
    "Connecting with the servers...",
    "Gathering data...",
    "Checking clouds...",
    "Finalizing results..."
]

def fake_progress():
    print("\n=== Meme Final Year Project: Weather Predictor 🌦️ ===")
    location = input("Enter your location: ")

    if not location.strip():
        print("⚠️ Please enter a valid location!")
        return

    print(f"\nSearching weather for: {location}\n")

    for i in range(0, 101, 20):
        # Show progress bar
        bar = "█" * (i // 5) + "-" * (20 - (i // 5))
        sys.stdout.write(f"\r[{bar}] {i}%")
        sys.stdout.flush()

        # Print fake status messages
        if i // 20 < len(statuses):
            print(f"\n{statuses[i // 20]}")
        time.sleep(1)

    print("\n\n🌤️ Just look outside!\n")

if __name__ == "__main__":
    fake_progress()
