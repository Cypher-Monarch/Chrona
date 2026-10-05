# Buffered PCM audio playback.

from collections import deque

from PySide6.QtCore import QIODevice


class AudioBuffer(QIODevice):
    # Provides synthesized PCM data to Qt audio playback.

    def __init__(self, max_buffer_bytes: int = 2 * 1024 * 1024):
        super().__init__()

        self._chunks: deque[bytes] = deque()
        self._buffer = bytearray()
        self._finished = False
        self._max_buffer_bytes = max_buffer_bytes

    def start(self) -> None:
        # Open the buffer for reading.
        self._finished = False
        self._chunks.clear()
        self._buffer.clear()
        self.open(QIODevice.OpenModeFlag.ReadOnly)

    def append(self, data: bytes) -> None:
        # Append synthesized audio to the playback buffer.
        if not data:
            return

        self._chunks.append(data)
        self.readyRead.emit()

    def finish(self) -> None:
        # Mark the stream as finished.
        self._finished = True
        self.readyRead.emit()

    def readData(self, maxlen: int) -> bytes:
        # Return up to maxlen bytes of PCM data.
        while self._chunks and len(self._buffer) < maxlen:
            self._buffer.extend(self._chunks.popleft())

        if not self._buffer:
            return b""

        data = bytes(self._buffer[:maxlen])
        del self._buffer[:maxlen]

        return data

    def writeData(
        self,
        data: bytes | bytearray | memoryview,
        length: int,
    ) -> int:
        # Writing to the playback buffer is unsupported.
        return -1

    def buffered_bytes(self) -> int:
        # Return the number of PCM bytes waiting for playback.
        return len(self._buffer) + sum(len(chunk) for chunk in self._chunks)

    def bytesAvailable(self) -> int:
        # Return the number of bytes currently available.
        return self.buffered_bytes() + super().bytesAvailable()
