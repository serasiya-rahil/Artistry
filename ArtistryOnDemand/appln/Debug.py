import os
import inspect
from datetime import datetime

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

        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        if not isinstance(message, str):
            message = str(message)

        state_width = 5  
        timestamp_width = 23  
        func_line_width = 30
        message_width = 85

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

        func_signature = f"{func_name}() Line: {line_number}" 
        log_entry = (f"| {str(self.log_line_number + 1).ljust(self.log_line_width())} | " 
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

        with open(self.log_filename, 'a') as f:
            if f.tell() == 0: 
                f.write(header)

            self.log_line_number += 1
            
            f.write(log_entry)

        self._save_log_line_number()

    def log_line_width(self):
        return len(str(self.log_line_number + 1)) 

    def info(self, message):
        """Log an info message."""
        if self.enabled:  
            frame = inspect.currentframe().f_back
            func_name = frame.f_code.co_name
            line_number = frame.f_lineno
            self._log(message, "INFO", func_name, line_number)

    def warn(self, message):
        """Log a warning message."""
        if self.enabled:  
            frame = inspect.currentframe().f_back
            func_name = frame.f_code.co_name
            line_number = frame.f_lineno
            self._log(message, "WARNING", func_name, line_number)

    def error(self, message):
        """Log an error message."""
        if self.enabled: 
            frame = inspect.currentframe().f_back
            func_name = frame.f_code.co_name
            line_number = frame.f_lineno
            self._log(message, "ERROR", func_name, line_number)
