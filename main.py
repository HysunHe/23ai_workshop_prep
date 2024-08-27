""" 
Description: 
 - Workshop demo application.

History:
 - 2024/08/27 by Hysun (hysun.he@oracle.com): Initial version
"""

import os
import uvicorn
import rest_controller
from threading import Thread
from dotenv import load_dotenv

load_dotenv("app.env")


def run():
    """Run the WSGI server"""
    host = os.environ.get("SERVER_HOST")
    port = int(os.environ.get("SERVER_LISTEN_PORT"))
    print(f"# WSGI server listening at {host}:{port}")

    data_init_thread = Thread(target=rest_controller.init, args=(), daemon=True)
    data_init_thread.start()

    uvicorn.run(rest_controller.app(), host=host, port=port)


if __name__ == "__main__":
    run()
