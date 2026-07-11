

import os
import sys
import time
import threading
import psutil
from datetime import datetime, timedelta

try:
    import tkinter as tk
    from tkinter import font
except ImportError:
    print("ERROR: tkinter not installed!")
    print("Run: pip install tk")
    sys.exit(1)

# ============================================================================
# CONFIG
# ============================================================================

BLOCKED_APPS = [
    "chrome.exe", "firefox.exe", "msedge.exe", "opera.exe",
    "vlc.exe", "spotify.exe", "steam.exe", "discord.exe",
    "epicgames.exe", "valorant.exe", "youtube.exe", "netflix.exe"
]

USERNAME = os.getenv('USERNAME')
LOCKED_FOLDERS = [
    f"C:\\Users\\{USERNAME}\\Downloads",
    f"C:\\Users\\{USERNAME}\\Videos",
    f"C:\\Users\\{USERNAME}\\Music"
]

# ============================================================================
# LOGGER
# ============================================================================

class Logger:
    def __init__(self):
        os.makedirs("logs", exist_ok=True)
    
    def log(self, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{ts}] {msg}"
        try:
            with open("logs/exam_log.txt", 'a') as f:
                f.write(entry + '\n')
        except:
            pass
        print(entry)

logger = Logger()

# ============================================================================
# TIMER
# ============================================================================

class Timer:
    def __init__(self, minutes):
        self.start = datetime.now()
        self.end = self.start + timedelta(minutes=minutes)
    
    def remaining(self):
        diff = self.end - datetime.now()
        if diff.total_seconds() <= 0:
            return 0, 0
        secs = int(diff.total_seconds())
        return secs // 60, secs % 60
    
    def is_done(self):
        return datetime.now() >= self.end

# ============================================================================
# FOLDER LOCKING
# ============================================================================

class FolderLocker:
    def __init__(self):
        self.locked = {}
    
    def lock_all(self, folders):
        count = 0
        for folder in folders:
            if not os.path.exists(folder):
                continue
            try:
                locked = folder + ".lock"
                os.rename(folder, locked)
                self.locked[folder] = locked
                logger.log(f"LOCKED: {folder}")
                count += 1
            except:
                pass
        return count
    
    def unlock_all(self):
        count = 0
        for original, locked in list(self.locked.items()):
            try:
                if os.path.exists(locked):
                    os.rename(locked, original)
                    logger.log(f"UNLOCKED: {original}")
                    count += 1
            except:
                pass
        self.locked.clear()
        return count

# ============================================================================
# APP MONITOR
# ============================================================================

class Monitor:
    def __init__(self):
        self.running = False
        self.detected = []
    
    def start(self):
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()
    
    def stop(self):
        self.running = False
    
    def _run(self):
        while self.running:
            try:
                for proc in psutil.process_iter(['name']):
                    try:
                        name = proc.name().lower()
                        if name in [a.lower() for a in BLOCKED_APPS]:
                            try:
                                proc.terminate()
                                time.sleep(2)
                                if proc.is_running():
                                    proc.kill()
                                logger.log(f"CLOSED: {name}")
                                if name not in self.detected:
                                    self.detected.append(name)
                            except:
                                pass
                    except:
                        pass
            except:
                pass
            time.sleep(1)

# ============================================================================
# FULLSCREEN LOCKSCREEN
# ============================================================================

class Lockscreen:
    def __init__(self, timer, monitor, locker):
        self.timer = timer
        self.monitor = monitor
        self.locker = locker
        self.root = None
        self.timer_label = None
    
    def create(self):
        """Create and show fullscreen"""
        self.root = tk.Tk()
        
        # Fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        
        # Prevent closing (most important!)
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Dark background
        self.root.config(bg='#000000')
        
        # Main container
        container = tk.Frame(self.root, bg='#000000')
        container.pack(expand=True, fill='both')
        
        # Title
        tk.Label(
            container,
            text="🔒 EXAM MODE ACTIVE",
            font=("Arial", 48, "bold"),
            fg='#FF0000',
            bg='#000000'
        ).pack(pady=40)
        
        # Timer (HUGE)
        self.timer_label = tk.Label(
            container,
            text="00:00",
            font=("Arial", 140, "bold"),
            fg='#00FF00',
            bg='#000000'
        )
        self.timer_label.pack(pady=40)
        
        # Status
        self.status_label = tk.Label(
            container,
            text="Exam in progress...",
            font=("Arial", 20),
            fg='#FFFF00',
            bg='#000000'
        )
        self.status_label.pack(pady=30)
        
        # Warnings
        tk.Label(
            container,
            text=(
                "⚠️  DO NOT CLOSE THIS WINDOW\n"
                "❌ APPS ARE BEING BLOCKED\n"
                "📁 FOLDERS ARE LOCKED\n"
                "⏱️  TIMER CANNOT BE STOPPED"
            ),
            font=("Arial", 14),
            fg='#FFFF00',
            bg='#000000',
            justify='center'
        ).pack(pady=40)
        
        print("✅ Fullscreen created")
        print("✅ Exam starting...\n")
        
        # Update loop
        self._update()
        
        # Run
        self.root.mainloop()
    
    def _update(self):
        """Update timer"""
        if self.root is None:
            return
        
        mins, secs = self.timer.remaining()
        time_str = f"{mins:02d}:{secs:02d}"
        
        try:
            self.timer_label.config(text=time_str)
            
            # Color change
            if mins == 0 and secs < 30:
                self.timer_label.config(fg='#FF0000')
                self.status_label.config(text="⏰ EXAM ENDING SOON!", fg='#FF0000')
            elif mins < 1:
                self.timer_label.config(fg='#FF6600')
            else:
                self.timer_label.config(fg='#00FF00')
            
            self.root.update()
        except:
            pass
        
        # Check if done
        if self.timer.is_done():
            self._close()
            return
        
        # Next update
        try:
            self.root.after(500, self._update)
        except:
            pass
    
    def _close(self):
        """Close fullscreen"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass

# ============================================================================
# MAIN APP
# ============================================================================

class App:
    def menu(self):
        print("\n" + "="*60)
        print("  🔒 EXAM-MODE PC LOCKDOWN")
        print("="*60)
        print("1. 🚀 START EXAM-MODE (Fullscreen)")
        print("2. ❌ Exit")
        print("="*60)
        return input("Enter choice (1-2): ").strip()
    
    def start_exam(self):
        try:
            duration = int(input("\n📝 Enter duration (minutes): "))
            if duration <= 0:
                print("ERROR: Must be positive!")
                return
        except:
            print("ERROR: Invalid!")
            return
        
        print(f"\n⏳ Starting {duration}-minute exam...")
        print("✅ Locking folders...")
        print("✅ Starting app monitor...")
        print("✅ Creating fullscreen...\n")
        
        # Setup
        timer = Timer(duration)
        locker = FolderLocker()
        monitor = Monitor()
        
        # Lock folders
        locked = locker.lock_all(LOCKED_FOLDERS)
        print(f"✅ Locked {locked} folders")
        
        # Start monitoring
        monitor.start()
        print("✅ Monitoring apps")
        
        logger.log(f"EXAM_START: {duration} minutes")
        
        # Fullscreen
        lockscreen = Lockscreen(timer, monitor, locker)
        lockscreen.create()
        
        # After exam
        print("\n" + "="*60)
        print("✅ EXAM COMPLETED!")
        print("="*60)
        
        monitor.stop()
        time.sleep(1)
        
        unlocked = locker.unlock_all()
        print(f"✅ Unlocked {unlocked} folders")
        print("✅ All apps can run again\n")
        
        logger.log(f"EXAM_END: Blocked apps: {len(monitor.detected)}")
    
    def run(self):
        print("="*60)
        print("🔒 EXAM-MODE PC LOCKDOWN")
        print("="*60)
        print("✅ Fullscreen Lockdown")
        print("✅ Cannot Close")
        print("✅ Auto-blocks Apps")
        print("✅ Locks Folders\n")
        
        while True:
            choice = self.menu()
            if choice == '1':
                self.start_exam()
            elif choice == '2':
                print("👋 Goodbye!")
                logger.log("APPLICATION CLOSED")
                break
            else:
                print("❌ Invalid!")

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    try:
        import psutil
    except:
        print("ERROR: psutil not installed!")
        print("Run: pip install psutil")
        sys.exit(1)
    
    try:
        app = App()
        app.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted")
    except Exception as e:
        print(f"ERROR: {e}")
        logger.log(f"ERROR: {e}")
