import asyncio, logging, socket, threading, time
import nest_asyncio
from ble_serial.bluetooth.ble_interface import BLE_interface

nest_asyncio.apply()  # Enable nested event loops

ble = None
loop = asyncio.get_event_loop()


def receive_callback(value: bytes):
    print("Received:", value)


async def command_sender(ble: BLE_interface, command):
    print("Sending...")
    ble.queue_send(f"{command}\r\n".encode())
    print('Sent!')


async def setup_ble():
    global ble
    # None uses default/autodetection, insert values if needed
    ADAPTER = "hci0"
    SERVICE_UUID = None
    WRITE_UUID = None
    READ_UUID = None
    DEVICE = "D8:3A:DD:57:35:AA"

    ble = BLE_interface(ADAPTER, SERVICE_UUID)
    ble.set_receiver(receive_callback)

    try:
        await ble.connect(DEVICE, "public", 10.0)
        await ble.setup_chars(WRITE_UUID, READ_UUID, "rw")
        # await command_sender(ble, 'toggle')

    except Exception as e:
        print('Error', e)


async def send_loop(ble):
    await ble.send_loop()

def start_server():
    global loop
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('localhost', 8089))
    serversocket.listen(5)  # become a server socket, maximum 5 connections
    print('Socket started')

    while True:
        connection, address = serversocket.accept()
        buf = connection.recv(64)

        if len(buf) > 0:
            print(buf.decode())  # prints received message
            if buf.decode() == "Go!":
                print('maybe..')
                asyncio.run_coroutine_threadsafe(command_sender(ble, 'toggle'), loop)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    setup_thread = threading.Thread(target=loop.run_until_complete, args=(setup_ble(),))
    setup_thread.start()

    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    send_loop_thread = threading.Thread(target=loop.run_until_complete, args=(send_loop(ble),))
    send_loop_thread.start()

    while ble is None:
        time.sleep(1)  # wait for ble to be initialized

    try:
        setup_thread.join()  # Wait for the BLE setup to complete
        server_thread.join()  # Wait for the server to complete
        send_loop_thread.join() # Wait for the send loop to complete
    finally:
        ble.disconnect()