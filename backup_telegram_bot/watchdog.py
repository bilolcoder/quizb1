import os
import sys
import time
import subprocess
import logging
from pathlib import Path

# Loyihaning asosiy papkasi
BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "bot.log"
WATCHDOG_PID_FILE = BASE_DIR / "watchdog.pid"
BOT_PID_FILE = BASE_DIR / "bot.pid"
STOP_SIGNAL_FILE = BASE_DIR / "stop.signal"

# Python interpreter yo'llari
PYTHON_EXE = sys.executable
if "pythonw.exe" in PYTHON_EXE.lower():
    py_std = Path(PYTHON_EXE).parent / "python.exe"
    if py_std.exists():
        PYTHON_EXE = str(py_std)

PYTHONW_EXE = str(Path(PYTHON_EXE).parent / "pythonw.exe")
if not Path(PYTHONW_EXE).exists():
    PYTHONW_EXE = PYTHON_EXE

# Windows konsolida UTF-8 ni to'g'ri ko'rsatish
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [WATCHDOG] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8")
        ]
    )
    return logging.getLogger("watchdog")


def is_pid_alive(pid: int, expected_name: str = "python") -> bool:
    """PID li jarayon mavjud, tirik va aynan Python jarayoni ekanligini tekshiradi."""
    if pid <= 0:
        return False
    try:
        import psutil
        if psutil.pid_exists(pid):
            p = psutil.Process(pid)
            if p.is_running() and p.status() != psutil.STATUS_ZOMBIE:
                p_name = p.name().lower()
                return expected_name.lower() in p_name
    except Exception:
        pass

    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000, False, pid)
        if handle:
            kernel32.CloseHandle(handle)
            return True
    except Exception:
        pass
    return False


def get_pid_from_file(file_path: Path) -> int:
    if file_path.exists():
        try:
            return int(file_path.read_text(encoding="utf-8").strip())
        except Exception:
            pass
    return 0


def cleanup_pids():
    for f in [WATCHDOG_PID_FILE, BOT_PID_FILE, STOP_SIGNAL_FILE]:
        try:
            if f.exists():
                f.unlink()
        except Exception:
            pass


def setup_windows_autostart():
    """Windows Startup papkasiga avtomatik ishga tushish faylini joylaydi."""
    appdata = os.getenv("APPDATA")
    if not appdata:
        return False

    startup_dir = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    if not startup_dir.exists():
        return False

    startup_vbs = startup_dir / "QuizBot_Startup.vbs"
    vbs_content = (
        'Set WshShell = CreateObject("WScript.Shell")\n'
        f'WshShell.CurrentDirectory = "{BASE_DIR}"\n'
        f'WshShell.Run "{PYTHONW_EXE} watchdog.py --daemon", 0, False\n'
    )
    try:
        startup_vbs.write_text(vbs_content, encoding="utf-8")
        return str(startup_vbs)
    except Exception as e:
        print(f"[OGOHLANTIRISH] Startup faylini yaratishda xatolik: {e}")
        return False


def cmd_start():
    """Botni fonda (background) ishga tushiradi."""
    wpid = get_pid_from_file(WATCHDOG_PID_FILE)
    if is_pid_alive(wpid):
        print(f"[OGOHLANTIRISH] Bot allaqachon fonda ishlamoqda! (Watchdog PID: {wpid})")
        print("Bot holatini tekshirish uchun: status_bot.bat")
        return

    # Eskirgan PID va signal fayllarini tozalash
    cleanup_pids()

    # Windows Startup avto-startni sozlash
    autostart_path = setup_windows_autostart()

    # Fonda to'liq mustaqil (detached) jarayon sifatida ishga tushirish
    flags = 0x00000008 | 0x00000200 | 0x08000000  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW
    proc = subprocess.Popen(
        [PYTHONW_EXE, str(BASE_DIR / "watchdog.py"), "--daemon"],
        cwd=str(BASE_DIR),
        creationflags=flags,
        close_fds=True
    )

    # Watchdog va Bot to'liq ishga tushishini 3 soniya kutish
    time.sleep(3)
    new_wpid = get_pid_from_file(WATCHDOG_PID_FILE)
    new_bpid = get_pid_from_file(BOT_PID_FILE)

    print("=" * 60)
    print("      IQTISODIY TAHLIL — TELEGRAM BOT ISHGA TUSHIRILDI")
    print("=" * 60)
    print("[MUVAFFAQIYAT] Bot fonda (background) 24/7 rejimida ishga tushdi.")
    if new_wpid:
        print(f"  * Watchdog nazoratchi PID: {new_wpid}")
    if new_bpid:
        print(f"  * Telegram Bot PID:         {new_bpid}")
    print("[MUVAFFAQIYAT] Oyna ochilmaydi. Terminalni bemalol yopishingiz mumkin.")
    print("[MUVAFFAQIYAT] Bot xatolik sabab to'xtasa, avtomatik qayta ishga tushadi.")
    if autostart_path:
        print("[MUVAFFAQIYAT] Kompyuter yoqilganda avtomatik ishga tushish sozlandi:")
        print(f"               {autostart_path}")
    print("=" * 60)


def cmd_stop():
    """Botni va uning nazoratchisini to'liq to'xtatadi."""
    print("=" * 60)
    print("      IQTISODIY TAHLIL — TELEGRAM BOTNI TO'XTATISH")
    print("=" * 60)

    try:
        STOP_SIGNAL_FILE.write_text("stop", encoding="utf-8")
    except Exception:
        pass

    wpid = get_pid_from_file(WATCHDOG_PID_FILE)
    bpid = get_pid_from_file(BOT_PID_FILE)

    stopped_any = False

    # 1. Bot jarayonini to'xtatish
    if bpid and is_pid_alive(bpid):
        print(f"[*] Bot jarayoni (PID: {bpid}) to'xtatilmoqda...")
        try:
            import psutil
            p = psutil.Process(bpid)
            p.terminate()
            try:
                p.wait(timeout=3)
            except psutil.TimeoutExpired:
                p.kill()
            stopped_any = True
        except Exception:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(bpid)], capture_output=True)
            stopped_any = True

    # 2. Watchdog jarayonini to'xtatish
    if wpid and is_pid_alive(wpid):
        print(f"[*] Watchdog nazoratchisi (PID: {wpid}) to'xtatilmoqda...")
        try:
            import psutil
            p = psutil.Process(wpid)
            p.terminate()
            try:
                p.wait(timeout=3)
            except psutil.TimeoutExpired:
                p.kill()
            stopped_any = True
        except Exception:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(wpid)], capture_output=True)
            stopped_any = True

    # 3. Ehtimoliy qolgan bot yoki watchdog jarayonlarini psutil orqali tozalash
    try:
        import psutil
        for p in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmd = " ".join(p.info.get("cmdline") or [])
                if "bot.py" in cmd or ("watchdog.py" in cmd and p.info["pid"] != os.getpid()):
                    p.kill()
                    stopped_any = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception:
        pass

    cleanup_pids()

    print("[MUVAFFAQIYAT] Bot va uning barcha fondagi jarayonlari to'xtatildi!")
    print("=" * 60)


def cmd_status():
    """Botning joriy holati va loglarini ko'rsatadi."""
    print("=" * 60)
    print("      IQTISODIY TAHLIL — BOTNING JORIY HOLATI")
    print("=" * 60)

    wpid = get_pid_from_file(WATCHDOG_PID_FILE)
    bpid = get_pid_from_file(BOT_PID_FILE)

    w_alive = is_pid_alive(wpid)
    b_alive = is_pid_alive(bpid)

    if w_alive and b_alive:
        print("[STATUS] BOT FAOL VA FONDA ISHLAMOQDA! (OK)")
        try:
            import psutil
            wp = psutil.Process(wpid)
            bp = psutil.Process(bpid)
            w_ram = round(wp.memory_info().rss / (1024 * 1024), 2)
            b_ram = round(bp.memory_info().rss / (1024 * 1024), 2)
            started = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(bp.create_time()))
            print(f"  * Watchdog nazoratchisi: PID {wpid} (RAM: {w_ram} MB)")
            print(f"  * Telegram Bot jarayoni: PID {bpid} (RAM: {b_ram} MB)")
            print(f"  * Ishga tushgan vaqti:    {started}")
        except Exception:
            print(f"  * Watchdog PID: {wpid}")
            print(f"  * Bot PID:      {bpid}")
    elif w_alive:
        print(f"[STATUS] Watchdog faol (PID: {wpid}), bot qayta yuklanmoqda...")
    else:
        print("[STATUS] BOT TO'XTATILGAN (Hozirda ishlamayapti)")
        print("Botni ishga tushirish uchun: start_bot.bat faylini bosing.")

    print("\n----------------- SO'NGGI 10 TA LOG QATORI -----------------")
    if LOG_FILE.exists():
        try:
            lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
            for line in lines[-10:]:
                print(line)
        except Exception as e:
            print(f"Log faylini o'qishda xatolik: {e}")
    else:
        print("bot.log fayli hali mavjud emas.")
    print("------------------------------------------------------------\n")


def daemon_loop():
    """Fonda ishlovchi watchdog xizmati."""
    try:
        _run_daemon()
    except Exception as e:
        import traceback
        try:
            (BASE_DIR / "daemon_crash.txt").write_text(traceback.format_exc(), encoding="utf-8")
        except Exception:
            pass


def _run_daemon():
    logger = setup_logger()

    # Boshqa watchdog ishlayotgan bo'lsa chiqish
    old_wpid = get_pid_from_file(WATCHDOG_PID_FILE)
    if old_wpid and old_wpid != os.getpid() and is_pid_alive(old_wpid):
        logger.warning("Boshqa watchdog ishlamoqda. Yangi jarayon to'xtatildi.")
        sys.exit(0)

    # O'z PID ini yozish
    current_pid = os.getpid()
    try:
        WATCHDOG_PID_FILE.write_text(str(current_pid), encoding="utf-8")
    except Exception as e:
        logger.error("watchdog.pid yozishda xatolik: %s", e)

    logger.info("Watchdog nazoratchisi ishga tushirildi (PID: %d).", current_pid)

    restart_count = 0

    while True:
        if STOP_SIGNAL_FILE.exists():
            logger.info("To'xtatish signali topildi. Watchdog yakunlanmoqda.")
            cleanup_pids()
            break

        logger.info("bot.py ishga tushirilmoqda (Urinish: %d)...", restart_count + 1)

        log_out = None
        try:
            log_out = open(LOG_FILE, "a", encoding="utf-8")
            proc = subprocess.Popen(
                [PYTHON_EXE, str(BASE_DIR / "bot.py")],
                cwd=str(BASE_DIR),
                stdout=log_out,
                stderr=subprocess.STDOUT
            )

            BOT_PID_FILE.write_text(str(proc.pid), encoding="utf-8")
            logger.info("Bot jarayoni ishga tushdi (PID: %d).", proc.pid)

            # Bot jarayonini kuzatish
            while proc.poll() is None:
                if STOP_SIGNAL_FILE.exists():
                    logger.info("Foydalanuvchi to'xtatishni talab qildi. Bot (PID: %d) yopilmoqda...", proc.pid)
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    cleanup_pids()
                    if log_out:
                        try:
                            log_out.close()
                        except Exception:
                            pass
                    return
                time.sleep(1)

            exit_code = proc.returncode
            if log_out:
                try:
                    log_out.close()
                except Exception:
                    pass

            restart_count += 1

            if STOP_SIGNAL_FILE.exists():
                logger.info("To'xtatish signali qabul qilindi. Watchdog yakunlanmoqda.")
                cleanup_pids()
                break

            logger.warning(
                "Bot jarayoni to‘xtadi (Chiqish kodi: %s). 5 soniyadan so‘ng qayta ishga tushiriladi...",
                exit_code
            )
            time.sleep(5)

        except Exception as ex:
            if log_out:
                try:
                    log_out.close()
                except Exception:
                    pass
            logger.critical("Bot jarayonini boshqarishda kutilmagan xatolik: %s", ex, exc_info=True)
            time.sleep(5)


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--start", "-start", "start"]:
            cmd_start()
            return
        elif arg in ["--stop", "-stop", "stop"]:
            cmd_stop()
            return
        elif arg in ["--status", "-status", "status"]:
            cmd_status()
            return
        elif arg in ["--daemon", "-daemon", "daemon"]:
            daemon_loop()
            return

    # Argument berilmagan bo'lsa default holatda status ko'rsatish
    cmd_status()


if __name__ == "__main__":
    main()
