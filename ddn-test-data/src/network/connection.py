"""
Network Connection Module for DDN Storage Systems
Handles network connections with retry logic and timeout handling
"""
import time
import socket
from typing import Optional, Dict, Any


class ConnectionError(Exception):
    """Custom exception for connection errors"""
    pass


class TimeoutError(Exception):
    """Custom exception for timeout errors"""
    pass


class NetworkConnection:
    """
    Manages network connections to DDN storage nodes
    Provides retry logic and failover support
    """

    def __init__(self, host: str, port: int, timeout: int = 30):
        """
        Initialize network connection

        Args:
            host: Hostname or IP address
            port: Port number
            timeout: Connection timeout in seconds (default: 30)
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.retry_count = 0
        self.max_retries = 3

    def connect(self) -> bool:
        """
        Establish connection to storage node

        Returns:
            True if connection successful, False otherwise

        Raises:
            ConnectionError: If connection fails after retries
        """
        while self.retry_count < self.max_retries:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(self.timeout)
                self.socket.connect((self.host, self.port))
                self.connected = True
                self.retry_count = 0
                return True

            except socket.timeout:
                self.retry_count += 1
                if self.retry_count >= self.max_retries:
                    raise ConnectionError(f"Connection timeout after {self.max_retries} retries")
                time.sleep(1)

            except Exception as e:
                self.retry_count += 1
                if self.retry_count >= self.max_retries:
                    raise ConnectionError(f"Connection failed: {str(e)}")
                time.sleep(1)

        return False

    def execute_operation(self, operation: str = "read", data: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Execute network operation with timeout handling

        THIS IS A COMMON ERROR POINT - LINE 87
        Operations may timeout if:
        - Network latency is high
        - Storage backend is slow to respond
        - Connection is lost mid-operation

        Args:
            operation: Operation type ('read', 'write', 'delete')
            data: Optional data for write operations

        Returns:
            Dictionary with operation result

        Raises:
            TimeoutError: If operation exceeds timeout (LINE 87 - COMMON ERROR)
            ConnectionError: If connection is lost
        """
        if not self.connected:
            raise ConnectionError("Not connected to storage node")

        start_time = time.time()

        try:
            # Simulate operation execution
            # In real implementation, this would send commands to storage backend
            time.sleep(0.1)

            # Check if operation exceeded timeout
            elapsed = time.time() - start_time
            if elapsed > self.timeout:
                # LINE 87 - THIS IS WHERE TIMEOUT ERRORS COMMONLY OCCUR
                raise TimeoutError(f'Operation timed out after {self.timeout}s')

            return {
                "status": "success",
                "operation": operation,
                "elapsed_time": elapsed,
                "data_size": len(data) if data else 0
            }

        except socket.timeout:
            raise TimeoutError(f'Operation timed out after {self.timeout}s')

        except Exception as e:
            raise ConnectionError(f"Operation failed: {str(e)}")

    def check_network_partition(self) -> bool:
        """
        Check for network partition scenarios

        Network partitions occur when nodes can't communicate due to:
        - Network switch failures
        - Firewall misconfigurations
        - Cable disconnections

        Returns:
            True if network partition detected, False otherwise

        Raises:
            ConnectionError: If partition detected (LINE 62)
        """
        try:
            # Attempt to ping the node
            response = self.socket.recv(1024) if self.socket else None

            if response is None:
                # LINE 62 - NETWORK PARTITION ERROR
                raise ConnectionError('Network partition detected')

            return False

        except Exception:
            # LINE 62 - NETWORK PARTITION ERROR
            raise ConnectionError('Network partition detected')

    def send_data(self, data: bytes) -> int:
        """
        Send data over the connection

        Args:
            data: Bytes to send

        Returns:
            Number of bytes sent

        Raises:
            ConnectionError: If send fails
        """
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected")

        try:
            return self.socket.send(data)
        except Exception as e:
            raise ConnectionError(f"Send failed: {str(e)}")

    def receive_data(self, buffer_size: int = 4096) -> bytes:
        """
        Receive data from the connection

        Args:
            buffer_size: Maximum bytes to receive

        Returns:
            Received data

        Raises:
            ConnectionError: If receive fails
            TimeoutError: If receive times out
        """
        if not self.connected or not self.socket:
            raise ConnectionError("Not connected")

        try:
            data = self.socket.recv(buffer_size)
            if not data:
                raise ConnectionError("Connection closed by remote host")
            return data

        except socket.timeout:
            raise TimeoutError(f"Receive timeout after {self.timeout}s")

        except Exception as e:
            raise ConnectionError(f"Receive failed: {str(e)}")

    def close(self):
        """Close the connection"""
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            finally:
                self.socket = None
                self.connected = False

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def __del__(self):
        """Destructor"""
        self.close()
