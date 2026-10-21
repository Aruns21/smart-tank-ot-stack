"""
Read the tank tags from Ignition's OPC-UA server and watch them change.

    python opcua_bridge.py                 # table of current values, then live changes
    python opcua_bridge.py --pulse start   # also press the START button via OPC-UA
    python opcua_bridge.py --pulse stop    # same for STOP / RESET

Credentials are typed at the prompt every run. Nothing is stored.
"""
import argparse
import asyncio
import getpass
import logging
import socket
from datetime import datetime
from pathlib import Path

from asyncua import Client
from asyncua.crypto.cert_gen import setup_self_signed_certificate
from cryptography.x509.oid import ExtendedKeyUsageOID

URL = "opc.tcp://localhost:62541"
APP_URI = "urn:smart-tank-ot-stack:opcua-bridge"
CERT_DIR = Path(__file__).parent / "certs"
PROVIDER = "default"
TAGS = [
    "StartButton", "StopButton", "LevelHighSensor", "LevelLowSensor",
    "InletValve", "Heater", "DrainValve",
]


async def find_child(parent, name):
    for child in await parent.get_children():
        if (await child.read_browse_name()).Name == name:
            return child
    raise RuntimeError(f"'{name}' not found under {parent}")


class ChangePrinter:
    def __init__(self, names):
        self.names = names

    def datachange_notification(self, node, value, data):
        stamp = datetime.now().strftime("%H:%M:%S")
        print(f"{stamp}  {self.names[node.nodeid]:<16} -> {value}", flush=True)

    def status_change_notification(self, status):
        print(f"subscription status changed: {status}", flush=True)


async def pulse(node, seconds=0.5):
    await node.write_value(True)
    await asyncio.sleep(seconds)
    await node.write_value(False)


async def make_client(user, password):
    # Ignition only accepts encrypted connections, so the client needs its own
    # certificate. It is created once and Ignition must be told to trust it.
    CERT_DIR.mkdir(exist_ok=True)
    key, cert = CERT_DIR / "client_key.pem", CERT_DIR / "client_cert.der"
    await setup_self_signed_certificate(
        key, cert, APP_URI, socket.gethostname(),
        [ExtendedKeyUsageOID.CLIENT_AUTH], {"commonName": "opcua-bridge"},
    )
    client = Client(URL, timeout=10)
    client.application_uri = APP_URI
    await client.set_security_string(f"Basic256Sha256,SignAndEncrypt,{cert},{key}")
    client.set_user(user)
    client.set_password(password)
    return client


async def main(pulse_tag):
    user = input("Ignition username: ")
    password = getpass.getpass("Ignition password: ")
    client = await make_client(user, password)

    async with client:
        providers = await find_child(client.nodes.objects, "Tag Providers")
        provider = await find_child(providers, PROVIDER)
        nodes = {name: await find_child(provider, name) for name in TAGS}

        print(f"\n{'tag':<16} {'value':<7} quality")
        for name, node in nodes.items():
            dv = await node.read_data_value()
            print(f"{name:<16} {str(dv.Value.Value):<7} {dv.StatusCode.name}")

        if pulse_tag:
            await pulse(nodes[pulse_tag])

        names = {node.nodeid: name for name, node in nodes.items()}
        subscription = await client.create_subscription(200, ChangePrinter(names))
        await subscription.subscribe_data_change(list(nodes.values()))

        print("\nWatching for changes. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pulse", choices=["start", "stop"])
    parser.add_argument("--debug", action="store_true", help="log OPC-UA subscription traffic")
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.WARNING)
        logging.getLogger("asyncua.common.subscription").setLevel(logging.DEBUG)
        logging.getLogger("asyncua.client.ua_client").setLevel(logging.INFO)
    tag = {"start": "StartButton", "stop": "StopButton"}.get(args.pulse)
    try:
        asyncio.run(main(tag))
    except KeyboardInterrupt:
        print("\nstopped")
