"""Serves Exports/ (keyframes.json) at http://127.0.0.1:8765 from inside Blender, so Studio can fetch the
clips with studio_import.luau. Run it once per Blender session; bpy.mp_server.shutdown() stops it."""
import functools
import http.server
import os
import threading

import bpy

FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Exports")


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def start(port=8765):
    if getattr(bpy, "mp_server", None) is None:
        os.makedirs(FOLDER, exist_ok=True)
        bpy.mp_server = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(_Quiet, directory=FOLDER))
        threading.Thread(target=bpy.mp_server.serve_forever, daemon=True).start()
    return "http://127.0.0.1:%d/keyframes.json" % port
