import logging
import asyncio
from bleak.exc import BleakError
from ble_serial import platform_uart as UART
from ble_serial.ports.tcp_socket import TCP_Socket
from ble_serial.bluetooth.ble_interface import BLE_interface
from ble_serial.log.fs_log import FS_log, Direction
from ble_serial.log.console_log import setup_logger
from ble_serial import cli

class Main():
    def __init__(self, args: cli.Namespace):
        self.args = args

    def start(self):
        try:
            logging.debug(f'Running: {self.args}')
            asyncio.run(self._run())

        # KeyboardInterrupt causes bluetooth to disconnect, but still a exception would be printed here
        except KeyboardInterrupt as e:
            logging.debug('Exit due to KeyboardInterrupt')

    async def _run(self):
        args = self.args
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(self.excp_handler)
        try:
            if args.tcp_port:
                self.uart = TCP_Socket(args.tcp_host, args.tcp_port, args.mtu)
            else:
                self.uart = UART(args.port, loop, args.mtu)

            self.bt = BLE_interface(args.adapter, args.service_uuid)

            if args.filename:
                self.log = FS_log(args.filename, args.binlog)
                self.bt.set_receiver(self.log.middleware(Direction.BLE_IN, self.uart.queue_write))
                self.uart.set_receiver(self.log.middleware(Direction.BLE_OUT, self.bt.queue_send))
            else:
                self.bt.set_receiver(self.uart.queue_write)
                self.uart.set_receiver(self.bt.queue_send)

            self.uart.start()
            await self.bt.connect(args.device, args.addr_type, args.timeout)
            await self.bt.setup_chars(args.write_uuid, args.read_uuid, args.mode)

            logging.info('Running main loop!')
            main_tasks = {
                asyncio.create_task(self.bt.send_loop()),
                asyncio.create_task(self.uart.run_loop())
            }
            done, pending = await asyncio.wait(main_tasks, return_when=asyncio.FIRST_COMPLETED)
            logging.debug(f'Completed Tasks: {[(t._coro, t.result()) for t in done]}')
            logging.debug(f'Pending Tasks: {[t._coro for t in pending]}')

        except BleakError as e:
            logging.error(f'Bluetooth connection failed: {e}')
        ### KeyboardInterrupts are now received on asyncio.run()
        # except KeyboardInterrupt:
        #     logging.info('Keyboard interrupt received')
        except Exception as e:
            logging.error(f'Unexpected Error: {repr(e)}')
        finally:
            logging.warning('Shutdown initiated')
            if hasattr(self, 'uart'):
                self.uart.remove()
            if hasattr(self, 'bt'):
                await self.bt.disconnect()
            if hasattr(self, 'log'):
                self.log.finish()
            logging.info('Shutdown complete.')


    def excp_handler(self, loop: asyncio.AbstractEventLoop, context):
        # Handles exception from other tasks (inside bleak disconnect, etc)
        # loop.default_exception_handler(context)
        logging.debug(f'Asyncio execption handler called {context["exception"]}')
        self.uart.stop_loop()
        self.bt.stop_loop()

def launch():
    args = cli.parse_args()
    setup_logger(args.verbose)
    Main(args).start()