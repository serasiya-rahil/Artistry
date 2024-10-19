import os
from datetime import datetime
import inspect

class SimpleDebugger:
    def __init__(self, log_filename="debugger.txt", line_number_filename="line_number.txt", enabled=True):
        self.log_filename = log_filename
        self.line_number_filename = line_number_filename
        self.log_line_number = self._get_last_log_line_number()  
        self.enabled = enabled  

    def _get_last_log_line_number(self):
        """Read the last log line number from the line number file."""
        if os.path.exists(self.line_number_filename):
            with open(self.line_number_filename, 'r') as f:
                try:
                    return int(f.read().strip())
                except ValueError:
                    return 0  
        return 0 

    def _save_log_line_number(self):
        """Save the current log line number to a separate file."""
        with open(self.line_number_filename, 'w') as f:
            f.write(str(self.log_line_number))

    def _log(self, message, state, func_name, line_number):
        if not self.enabled:
            return  

        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Keep milliseconds

        if not isinstance(message, str):
            message = str(message)

        state_width = 5  
        timestamp_width = 23  
        func_line_width = 25  
        message_width = 85

        # Create the header
        header = (
            f"{'-' * self.log_line_width()}"
            f"{'-' * state_width}"
            f"{'-' * timestamp_width}"
            f"{'-' * func_line_width}"
            f"{'-' * message_width}\n"
            f"| {'Log Line'.ljust(self.log_line_width())} | "
            f"{'State'.ljust(state_width)} | "
            f"{'Timestamp'.ljust(timestamp_width)} | "
            f"{'Function Signature'.ljust(func_line_width)} | "
            f"{'Message'} |\n"
            f"+{'-' * self.log_line_width()}"
            f"{'-' * state_width}"
            f"{'-' * timestamp_width}"
            f"{'-' * func_line_width}"
            f"{'-' * message_width}\n"
        )

        # Format the log entry with specified widths
        func_signature = f"{func_name}() Line: {line_number}"  # Full function signature with line number
        log_entry = (f"| {str(self.log_line_number + 1).ljust(self.log_line_width())} | "  # Log line number
                     f"{state.ljust(state_width)} | "
                     f"{timestamp} | "
                     f"{func_signature.ljust(func_line_width)} | "
                     f"{message} |\n"
                     f"+{'-' * self.log_line_width()}"
                     f"{'-' * state_width}"
                     f"{'-' * timestamp_width}"
                     f"{'-' * func_line_width}"
                     f"{'-' * message_width}\n"
        )

        # Write the header and log entry to the file
        with open(self.log_filename, 'a') as f:
            # Write the header only once
            if f.tell() == 0:  # Check if the file is empty
                f.write(header)

            # Increment log line number before writing the log entry
            self.log_line_number += 1
            
            f.write(log_entry)

        # Save the current log line number to a separate file
        self._save_log_line_number()

    def log_line_width(self):
        return len(str(self.log_line_number + 1))  # Dynamic width based on log line number

    def info(self, message):
        """Log an info message."""
        if self.enabled:  # Only log if the debugger is enabled
            frame = inspect.currentframe().f_back
            func_name = frame.f_code.co_name
            line_number = frame.f_lineno
            self._log(message, "INFO", func_name, line_number)

    def warn(self, message):
        """Log a warning message."""
        if self.enabled:  # Only log if the debugger is enabled
            frame = inspect.currentframe().f_back
            func_name = frame.f_code.co_name
            line_number = frame.f_lineno
            self._log(message, "WARNING", func_name, line_number)

    def error(self, message):
        """Log an error message."""
        if self.enabled:  # Only log if the debugger is enabled
            frame = inspect.currentframe().f_back
            func_name = frame.f_code.co_name
            line_number = frame.f_lineno
            self._log(message, "ERROR", func_name, line_number)
