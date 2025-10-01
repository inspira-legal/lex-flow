import io
from contextlib import redirect_stdout
from typing import Callable, TextIO


class OutputCapture:
    """Simple output capture using Python's built-in redirect_stdout.

    Usage:
        with OutputCapture() as capture:
            print("Hello")
            result = capture.get_output()  # "Hello\\n"
    """

    def __init__(self):
        self.buffer = io.StringIO()
        self._redirect_context = None

    def __enter__(self):
        """Start capturing output."""
        self._redirect_context = redirect_stdout(self.buffer)
        self._redirect_context.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop capturing output."""
        if self._redirect_context:
            self._redirect_context.__exit__(exc_type, exc_val, exc_tb)

    def get_output(self) -> str:
        """Get captured output."""
        return self.buffer.getvalue()

    def clear(self):
        """Clear the buffer."""
        self.buffer = io.StringIO()


class TeeOutput:
    """Write to multiple outputs simultaneously (like Unix tee command).

    Usage:
        with open('logfile.txt', 'w') as f:
            tee = TeeOutput(sys.stdout, f)
            engine = Engine(program, output=tee)
    """

    def __init__(self, *outputs: TextIO):
        self.outputs = outputs

    def write(self, text: str) -> int:
        """Write to all outputs."""
        for output in self.outputs:
            output.write(text)
        return len(text)

    def flush(self):
        """Flush all outputs."""
        for output in self.outputs:
            if hasattr(output, "flush"):
                output.flush()


class StreamingOutput:
    """Stream output to a callback function (for WebSockets, SSE, etc).

    Usage:
        async def send_to_websocket(line):
            await websocket.send(line)

        stream = StreamingOutput(send_to_websocket)
        engine = Engine(program, output=stream)
    """

    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        self.buffer = ""

    def write(self, text: str) -> int:
        """Write text and call callback on newlines."""
        self.buffer += text

        # Stream on newlines
        if "\n" in text:
            lines = self.buffer.split("\n")
            for line in lines[:-1]:
                if line:  # Skip empty lines
                    self.callback(line)
            self.buffer = lines[-1]

        return len(text)

    def flush(self):
        """Flush remaining buffer."""
        if self.buffer:
            self.callback(self.buffer)
            self.buffer = ""
