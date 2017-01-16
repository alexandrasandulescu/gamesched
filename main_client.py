#!/usr/bin/env python3
from Client import Client

def main():
    print("[Main] Client starting ...")
    client = Client("127.0.0.1",  65530)
    client.start()

if __name__ == "__main__":
    main()
