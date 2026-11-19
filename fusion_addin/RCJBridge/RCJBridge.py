"""RCJBridge.py — Add-in entry point.

run(context)  called by Fusion when the Add-in starts.
stop(context) called by Fusion when the Add-in stops.
"""

import json
import traceback

import adsk.core
import adsk.fusion

from . import dispatcher, server

EVENT_ID = "RCJBridge_exec"
_app = None
_handlers = []


class _ExecHandler(adsk.core.CustomEventHandler):
    def notify(self, args):
        try:
            job_id = json.loads(args.additionalInfo)["job_id"]
            dispatcher.run_job(job_id)   # runs on the Fusion main thread
        except Exception:
            _app.log("RCJBridge exec error:\n" + traceback.format_exc())


def run(context):
    global _app
    try:
        _app = adsk.core.Application.get()
        event = _app.registerCustomEvent(EVENT_ID)
        handler = _ExecHandler()
        event.add(handler)
        _handlers.append(handler)

        def on_enqueue(job_id):              # called from HTTP thread
            _app.fireCustomEvent(EVENT_ID, json.dumps({"job_id": job_id}))

        server.start(on_enqueue)
        _app.log("RCJBridge: server active on port 8765")
    except Exception:
        _app.userInterface.messageBox(
            "RCJBridge failed to start:\n" + traceback.format_exc()
        )


def stop(context):
    try:
        server.stop()
        _app.unregisterCustomEvent(EVENT_ID)
        _handlers.clear()
    except Exception:
        _app.log("RCJBridge stop error:\n" + traceback.format_exc())
