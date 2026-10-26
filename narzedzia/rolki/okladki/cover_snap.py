import os, subprocess, time
from playwright.sync_api import sync_playwright
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jobs = [("wow11", "okladka_09_podsumowanie.jpg"), ("wow12", "okladka_10_tarot.jpg")]
with sync_playwright() as p:
    br = p.chromium.launch(args=["--force-device-scale-factor=1", "--no-proxy-server"])
    for k, (folder, name) in enumerate(jobs):
        port = 8795 + k
        srv = subprocess.Popen(["python3", "-m", "http.server", str(port)], cwd=os.path.join(S, folder), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.8)
        try:
            pg = br.new_page(viewport={"width": 1080, "height": 1920}); pg.on("pageerror", lambda e: print("pageerror", e))
            pg.goto(f"http://127.0.0.1:{port}/index.html"); pg.wait_for_function("window.READY===true", timeout=20000)
            pg.evaluate("renderCover()"); pg.screenshot(path=os.path.join(S, "okladki", "final", name), type="jpeg", quality=95)
        finally:
            srv.terminate()
