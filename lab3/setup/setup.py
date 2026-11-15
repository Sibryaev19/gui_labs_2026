import os
import shutil
import subprocess
import sys
import venv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_DIR = os.path.join(BASE_DIR, ".venv")

XCB_PACKAGES = [
    "libxcb-xinerama0",
    "libxcb-cursor0",
    "libxcb-icccm4",
    "libxcb-image0",
    "libxcb-keysyms1",
    "libxcb-randr0",
    "libxcb-render-util0",
    "libxcb-shape0",
    "libxcb-xkb1",
    "libxkbcommon-x11-0",
]


def venv_python():
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def create_venv():
    if not os.path.exists(venv_python()):
        print("Создаю виртуальное окружение .venv ...")
        venv.create(VENV_DIR, with_pip=True)


def install_deps():
    py = venv_python()
    missing = []
    for pkg, mod in [("PyQt5", "PyQt5")]:
        if subprocess.run([py, "-c", f"import {mod}"],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode != 0:
            missing.append(pkg)
    if missing:
        print("Устанавливаю:", ", ".join(missing))
        subprocess.run([py, "-m", "pip", "install", *missing], check=True)


def install_system_deps():
    if os.name != "posix" or sys.platform == "darwin":
        return
    if shutil.which("apt-get") is None:
        print("Не нашёл apt-get. Поставь вручную пакеты для Qt xcb:")
        print("  " + " ".join(XCB_PACKAGES))
        return

    missing = []
    for pkg in XCB_PACKAGES:
        r = subprocess.run(["dpkg-query", "-W", "-f=${Status}", pkg],
                           capture_output=True, text=True)
        if "install ok installed" not in r.stdout:
            missing.append(pkg)

    if not missing:
        return

    print("Не хватает системных библиотек для Qt xcb:", ", ".join(missing))
    print("Запускаю apt-get install (может понадобиться пароль sudo) ...")
    cmd = ["apt-get", "install", "-y", *missing]
    if os.geteuid() != 0:
        if shutil.which("sudo") is None:
            print("Нет sudo. Выполни вручную:")
            print("  sudo apt-get install " + " ".join(missing))
            sys.exit(1)
        cmd = ["sudo", *cmd]
    subprocess.run(cmd, check=True)


def ensure_env():
    env_path = os.path.join(BASE_DIR, ".env")
    example = os.path.join(BASE_DIR, ".env.example")
    if not os.path.exists(env_path) and os.path.exists(example):
        shutil.copyfile(example, env_path)
        print("Создан .env из .env.example")


if __name__ == "__main__":
    ensure_env()
    install_system_deps()
    create_venv()
    install_deps()
    print("Окружение готово")
