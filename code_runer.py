import os
import subprocess
import sys
import io
import contextlib
import asyncio


async def execute_code(code: str) -> str:
    try:
        # ایجاد یک بافر برای خروجی
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exec(code, {'__name__': '__main__', '__builtins__': __builtins__, 'asyncio': asyncio})
        output = buffer.getvalue()
        return output if output else "کدی اجرا نشد یا خروجی ندارد."
    except Exception as e:
        return f"خطا: {str(e)}"


