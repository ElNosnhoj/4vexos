from typing import Callable
import paramiko
import asyncio
import threading


class SSHClient(paramiko.SSHClient):
    def __init__(self, host, **kwargs):
        self.host = host
        self.user = kwargs.get("user", "admin")
        self.pswd = kwargs.get("pswd", "password")
        self.__hostname = ''
        self.connected = False
        self._lock = threading.Lock()
        super().__init__()
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        with self._lock:
            try:
                super().connect(self.host, username=self.user, password=self.pswd, timeout=0.5)
                self.connected = True
            except:
                print(f"connect to {self.host} failed due to timeout")

    def close(self):
        with self._lock:
            try:
                super().close()
            except:
                pass
            self.connected = False

    def exec_command(self, command):
        with self._lock:
            try:
                return super().exec_command(command)
            except Exception as e:
                print(f"[exec_command] Error running command '{command}': {e}")
                return None, None, None

    def safe_exec_command(self, command: str):
        """ Ensures connect/disconnect, runs command, returns (stdin, stdout, stderr). """
        was_connected = self.connected
        if not was_connected:
            self.connect()
        result = self.exec_command(command)
        if not was_connected:
            self.close()
        return result

    def get_hostname(self):
        if self.__hostname:  return self.__hostname

        # check if connected. if not, connect and disconnect.
        isConnected = self.connected
        if (not isConnected): self.connect()
        stdin, stdout, stderr = self.exec_command("hostname")
        self.__hostname = stdout.read().decode().strip()
        if (not isConnected): self.close()
        return self.__hostname

    hostname = property(get_hostname)
        
        

    # def stream(self, command: str, onLine: Callable[[str], None]):
    #     transport = self.get_transport()
    #     channel = transport.open_session()
    #     channel.exec_command(command)

    # return channel?


if __name__ == "__main__":
    client = SSHClient("192.168.4.35", user="root", pswd="handsome")
    print(client.get_hostname())

