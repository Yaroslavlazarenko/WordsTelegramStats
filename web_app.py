#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main web server launcher for WordsTelegramStats.
Runs the FastAPI web dashboard via Uvicorn.
"""

import os
import uvicorn
from src.web.app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Запуск веб-сервера WordsTelegramStats на http://localhost:{port}")
    uvicorn.run("src.web.app:app", host=host, port=port, reload=False)
