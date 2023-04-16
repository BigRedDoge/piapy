import random
import subprocess
from itertools import cycle
from platform import system
from time import sleep

# Change the piactl path if executing on Windows
piapath = "piactl"
if system() == 'Windows':
    piapath = "C:\Program Files\Private Internet Access"


class PiaVpn:
    def __init__(self):
        pass

    @staticmethod
    def regions():
        """
        get VPN servers available
        :return:
        """
        cmd = ["cd", piapath, "&&", ".\\piactl", "get", "regions"]
        process = subprocess.run(
            cmd, shell=True, capture_output=True
        )

        regions = [e.strip('\r') for e in process.stdout.decode("utf-8").split("\n")]
        regions.remove("auto")
        regions.remove("")

        return regions

    @staticmethod
    def region():
        cmd = ["cd", piapath, "&&", ".\\piactl", "get", "region"]
        process = subprocess.run(cmd, shell=True, capture_output=True)
        
        return process.stdout.decode("utf-8").replace("\n", "").strip('\r')

    def set_region(self, server=None):

        regions = self.regions()
        if server is None or server.lower() == "auto":
            server = "auto"
        elif server.lower() == "random":
            server = random.choice(regions)
        elif server not in regions:
            raise ConnectionError("Server must be one of: {}".format(regions))

        cmd = [piapath, "set", "region", server]
        process = subprocess.run(cmd, shell=True, capture_output=True)

        return server

    @staticmethod
    def status():
        cmd = ["cd", piapath, "&&", ".\\piactl", "get", "connectionstate"]

        process = subprocess.run(
            cmd, shell=True, capture_output=True
        )

        return process.stdout.decode("utf-8").replace("\n", "").strip('\r')

    @staticmethod
    def ip():
        cmd = ["cd", piapath, "&&", ".\\piactl", "get", "vpnip"]
        process = subprocess.run(cmd, shell=True, capture_output=True)

        return process.stdout.decode("utf-8").replace("\n", "").strip('\r')

    def connect(self, timeout=20, verbose=False):
        """

        :param timeout: int
        :param verbose: bool
        :return:
        """
        if not isinstance(timeout, int) and not isinstance(verbose, bool):
            raise SystemError(
                'Args have some problems, check them. "timeout" must be integer and "verbose" must be boolean.'
            )

        cmd = ["cd", piapath, "&&", ".\\piactl", "connect"]
        process = subprocess.run(cmd, shell=True, capture_output=True)

        wait_animation = self._wait_iterator()
        elapsed_time = 0.0
        while self.status().lower() != "connected":
            if int(elapsed_time) == timeout:
                self.disconnect()
                raise ConnectionError(
                    "\nConnectionError: Unable to connect to server. Check your internet connection."
                )
            if verbose:
                print("\rVPN connecting [{}]".format(next(wait_animation)), end="")
            sleep_time = 0.2
            sleep(sleep_time)
            elapsed_time += sleep_time
        region = self.region()

        if verbose:
            print('\rVPN connected to: "{}"'.format(region))

        return region

    @staticmethod
    def _wait_iterator():
        return cycle("|/-\\")

    @staticmethod
    def disconnect():
        cmd = ["cd", piapath, "&&", ".\\piactl", "disconnect"]
        process = subprocess.run(cmd, shell=True, capture_output=True)

        return True

    @staticmethod
    def reset_settings():
        cmd = ["cd", piapath, "&&", ".\\piactl", "resetsettings"]
        process = subprocess.run(cmd, shell=True, capture_output=True)

        return True

    @staticmethod
    def set_debug_logging(value=True):

        if not isinstance(value, bool):
            raise SystemError('Arg "value" must be a boolean.')

        cmd = ["cd", piapath, "&&", ".\\piactl", "set", "debuglogging", str(value).lower()]
        process = subprocess.run(cmd, shell=True, capture_output=True)

        return True
