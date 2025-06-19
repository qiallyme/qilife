import argparse
from common.utils import setup_logger

# Set up root logger
logger = setup_logger("unified-app", "logs/app.log")

def main():
    parser = argparse.ArgumentParser(prog="unified-app")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("monitor", help="Start QiFileFlow monitor")
    sub.add_parser("capture", help="Run QiLifeFeed capture (email/calendar/tasks)")
    sub.add_parser("digest", help="Generate daily digest")
    sub.add_parser("qinote", help="Transform Life Feed into QiNote nodes")

    args = parser.parse_args()
    cmd = args.command

    if cmd == "monitor":
        from qifileflow.monitor import start_monitor
        start_monitor()
    elif cmd == "capture":
        from qilifefeed.capture import run_capture
        run_capture()
    elif cmd == "digest":
        from qilifefeed.digest import generate_daily_digest
        generate_daily_digest()
    elif cmd == "qinote":
        from qinote.transform import run_qinote
        run_qinote()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
