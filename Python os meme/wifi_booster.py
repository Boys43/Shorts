import math
import random
import time
import threading
import tkinter as tk
from tkinter import ttk

# ----------------------------
# Config
# ----------------------------
APP_TITLE = "WiFi Speed Booster"
DARK_BG = "#0d1117"
PANEL_BG = "#111318"
ACCENT = "#00ffcc"
TEXT = "#e6edf3"
MUTED = "#94a3b8"
WARNING = "#ffcc00"
DANGER = "#ff5c5c"

FAKE_STEPS = [
    "Initializing RF optimizer…",
    "Probing router QoS tables…",
    "Re-indexing DNS cache…",
    "Aligning virtual antennas (±0.7°)…",
    "Enabling packet turbo-mode…",
    "Defragmenting Wi-Fi spectrum…",
    "Negotiating with upstream ISP…",
    "Recalibrating MTU and MSS…",
    "Compacting TCP congestion window…",
    "Rewriting NAT hairpin rules…",
    "Resolving captive portal ghosts…",
    "Flushing phantom ARP entries…",
    "Synchronizing with nearby satellites…",
    "Enabling MU-MIMO hyper-threading…",
    "Tuning beamforming coefficients…",
    "Warming up 5GHz ion thrusters…",
    "Stabilizing jitter and bufferbloat…",
    "Rewiring electrons for extra speed…",
    "Finalizing boost sequence…",
]

# ----------------------------
# Gauge helpers
# ----------------------------
def polar_to_xy(cx, cy, r, angle_deg):
    a = math.radians(angle_deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)

class Speedometer:
    """
    A simple half-circle gauge:
    -180° (left) -> 0 Mbps
     -0° (right) -> max Mbps
    We’ll actually use -210° to +30° for a sportier look.
    """
    def __init__(self, canvas, x, y, radius, max_value=500):
        self.c = canvas
        self.cx, self.cy = x, y
        self.r = radius
        self.max = max_value
        self.arc = None
        self.ticks = []
        self.needle = None
        self.value_text = None
        self._draw_static()

    def _draw_static(self):
        # Dial background
        self.c.create_oval(self.cx - self.r, self.cy - self.r,
                           self.cx + self.r, self.cy + self.r,
                           outline="#222831", width=10, fill="#0b0f14")

        # Range arc (decorative outer)
        self.c.create_arc(self.cx - self.r - 8, self.cy - self.r - 8,
                          self.cx + self.r + 8, self.cy + self.r + 8,
                          start=210, extent=240, style=tk.ARC,
                          outline=ACCENT, width=3)

        # Ticks
        for i in range(0, 6):  # 0,100,200,300,400,500
            v = i * (self.max // 5)
            ang = self.value_to_angle(v)
            x1, y1 = polar_to_xy(self.cx, self.cy, self.r - 15, ang)
            x2, y2 = polar_to_xy(self.cx, self.cy, self.r - 35, ang)
            self.c.create_line(x1, y1, x2, y2, fill="#2a3340", width=3)
            # Labels
            lx, ly = polar_to_xy(self.cx, self.cy, self.r - 55, ang)
            self.c.create_text(lx, ly, text=str(v), fill=MUTED, font=("Segoe UI", 10, "bold"))

        # Hub
        self.c.create_oval(self.cx - 8, self.cy - 8, self.cx + 8, self.cy + 8,
                           fill="#1f2937", outline="#2a3340")

        # Needle (initialize pointing left)
        self.needle = self.c.create_line(self.cx, self.cy,
                                         self.cx - (self.r - 45), self.cy,
                                         fill=DANGER, width=4)

        # Value text
        self.value_text = self.c.create_text(self.cx, self.cy + self.r // 2,
                                             text="0 Mbps", fill=TEXT,
                                             font=("Segoe UI", 18, "bold"))

        self.c.create_text(self.cx, self.cy + self.r // 2 + 28,
                           text="Link Quality: Idle", fill=MUTED,
                           font=("Segoe UI", 10))

    def value_to_angle(self, value):
        # Map 0..max -> -210..+30 degrees
        value = max(0, min(self.max, value))
        return -210 + (240 * (value / self.max))

    def set_value(self, value):
        ang = self.value_to_angle(value)
        tip_x, tip_y = polar_to_xy(self.cx, self.cy, self.r - 45, ang)
        # Redraw needle
        self.c.coords(self.needle, self.cx, self.cy, tip_x, tip_y)
        # Update text
        self.c.itemconfigure(self.value_text, text=f"{int(value)} Mbps")


# ----------------------------
# App
# ----------------------------
class BoosterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.configure(bg=DARK_BG)
        self.resizable(False, False)

        # Window size & center
        w, h = 720, 520
        self.geometry(f"{w}x{h}")
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

        # Title
        title = tk.Label(self, text="WiFi Speed Booster", fg=ACCENT, bg=DARK_BG,
                         font=("Segoe UI Semibold", 22))
        title.pack(pady=(16, 6))

        # Gauge canvas
        self.canvas = tk.Canvas(self, width=680, height=280, bg=DARK_BG, highlightthickness=0)
        self.canvas.pack()
        self.gauge = Speedometer(self.canvas, x=340, y=160, radius=130, max_value=500)

        # Logs
        log_frame = tk.Frame(self, bg=PANEL_BG, highlightbackground="#1f2937", highlightthickness=1)
        log_frame.pack(fill="both", expand=False, padx=18, pady=(8, 8))
        lbl = tk.Label(log_frame, text="Boost Logs", bg=PANEL_BG, fg=MUTED, font=("Segoe UI", 10, "bold"))
        lbl.pack(anchor="w", padx=10, pady=(8, 0))

        self.log_text = tk.Text(log_frame, height=8, bg=PANEL_BG, fg=TEXT, bd=0,
                                font=("Consolas", 10), wrap="none")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=8)
        self.log_text.config(state="disabled")

        # Bottom controls
        ctrl = tk.Frame(self, bg=DARK_BG)
        ctrl.pack(fill="x", padx=18, pady=(0, 12))

        self.progress = ttk.Progressbar(ctrl, length=420, mode="determinate", maximum=100)
        self.progress.pack(side="left", padx=(0, 10))
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("TProgressbar", troughcolor="#0b0f14", bordercolor="#0b0f14",
                             background=ACCENT, lightcolor=ACCENT, darkcolor=ACCENT)

        self.start_btn = tk.Button(ctrl, text="Boost My Internet", bg=ACCENT, fg="#00120f",
                                   font=("Segoe UI Semibold", 11), bd=0, relief="flat",
                                   activebackground="#00d9b0", padx=16, pady=8,
                                   command=self.start_boost)
        self.start_btn.pack(side="left")

        self.final_label = tk.Label(self, text="", bg=DARK_BG, fg=WARNING,
                                    font=("Segoe UI", 12, "bold"))
        self.final_label.pack(pady=(4, 0))

        self.running = False

    # Thread-safe logger
    def log(self, line):
        self.log_text.config(state="normal")
        self.log_text.insert("end", time.strftime("[%H:%M:%S] ") + line + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def start_boost(self):
        if self.running:
            return
        self.running = True
        self.start_btn.config(state="disabled")
        self.progress["value"] = 0
        self.final_label.config(text="")
        self.clear_logs()
        # kick off worker thread so UI stays responsive
        threading.Thread(target=self._boost_sequence, daemon=True).start()

    def clear_logs(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    # The main fake sequence
    def _boost_sequence(self):
        self.log("Starting boost engine…")
        current_speed = 0.0

        # Phase 1: ramp with jitter
        for i, step in enumerate(FAKE_STEPS):
            # Random progress + random delays
            target = min(100, self.progress["value"] + random.randint(5, 9))
            delay_ms = random.randint(200, 700)

            # Animate gauge toward a temporary target speed
            # Let the speed breathe: sometimes dip a little before rising
            burst = max(5, random.randint(-10, 60))
            temp_target_speed = max(0, min(500, current_speed + burst))

            self._animate_speed(current_speed, temp_target_speed, duration_ms=delay_ms)
            current_speed = temp_target_speed

            # Update progress & log line
            self._set_progress(target)
            self.log(step)

            # Sprinkle micro-logs to feel “busy”
            for _ in range(random.randint(1, 3)):
                micro = self._random_micro_log()
                self.log("… " + micro)
                time.sleep(random.uniform(0.06, 0.18))

            time.sleep(random.uniform(0.08, 0.18))

        # Phase 2: dramatic final push
        self.log("Engaging overdrive…")
        final_target = random.randint(380, 500)
        self._animate_speed(current_speed, final_target, duration_ms=1400)
        self._set_progress(100)

        # Hold a moment
        time.sleep(0.6)

        # Big reveal (meme)
        self._show_final("✅ Boost Complete: Step closer to your router for maximum speed 📶😂")
        self.running = False
        self.start_btn.config(state="normal")

    def _random_micro_log(self):
        verbs = [
            "hashing", "seeding", "pinning", "debouncing", "bucketing",
            "vectorizing", "preheating", "hydrating", "muxing", "demuxing",
            "handshaking", "profiling", "indexing", "defusing latency",
        ]
        objs = [
            "packets", "PHY layer", "SNR curve", "retry queue",
            "ACK frames", "RTT histogram", "beamforming map",
            "CTS/RTS window", "channel graph", "L2 buffers",
        ]
        return f"{random.choice(verbs)} {random.choice(objs)}…"

    def _set_progress(self, value):
        v = max(0, min(100, int(value)))
        self.progress.after(0, lambda: self.progress.config(value=v))

    def _animate_speed(self, start, end, duration_ms=600):
        steps = max(8, int(duration_ms / 16))
        for i in range(1, steps + 1):
            # ease-out cubic
            t = i / steps
            eased = 1 - pow(1 - t, 3)
            val = start + (end - start) * eased
            self._set_speed(val)
            time.sleep(duration_ms / steps / 1000.0)

    def _set_speed(self, value):
        v = max(0.0, min(500.0, float(value)))
        self.canvas.after(0, lambda: self.gauge.set_value(v))

    def _show_final(self, text):
        self.final_label.after(0, lambda: self.final_label.config(text=text))


if __name__ == "__main__":
    app = BoosterApp()
    app.mainloop()
