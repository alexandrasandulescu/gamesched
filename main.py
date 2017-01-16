#!/usr/bin/env python3
from Server import Server

def main():
    print("[Main] Scheduler starting ...")
    server = Server(65530)
    server.mainloop()

if __name__ == "__main__":
    # execute only if run as a script
    main()
