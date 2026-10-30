"""Serves this folder's export/ (clips.json) at http://127.0.0.1:8765 from inside Blender, for studio_import.luau.
Run in Blender:  exec(open(path).read(), {"__file__": path})   Stop: bpy._mp_srv.shutdown()
"""
import bpy, functools, http.server, os, threading

ROOT = os.path.join(os.path.dirname(__file__), "export")
if getattr(bpy, "_mp_srv", None) is None:
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    bpy._mp_srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8765), functools.partial(Quiet, directory=ROOT))
    threading.Thread(target=bpy._mp_srv.serve_forever, daemon=True).start()
