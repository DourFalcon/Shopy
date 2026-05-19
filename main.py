from Website import create_app

app = create_app()

if __name__ == '__main__':
    # Open the default web browser shortly after the server starts.
    # When `debug=True` Flask's reloader runs the script twice (parent + child),
    # so guard the opener so it only runs in the reloader child process.
    import webbrowser
    import threading
    import os

    def _open_browser():
        import tempfile, time
        lock_path = os.path.join(tempfile.gettempdir(), 'shopy_browser_opened')
        try:
            # if lock exists and is recent, skip opening (prevents duplicate tabs on reload)
            if os.path.exists(lock_path):
                mtime = os.path.getmtime(lock_path)
                if time.time() - mtime < 10:
                    return
            # create/update the lock file timestamp
            with open(lock_path, 'w') as f:
                f.write(str(os.getpid()))
        except Exception:
            pass
        webbrowser.open_new('http://127.0.0.1:5000')

    # Start the opener only in the reloader child (WERKZEUG_RUN_MAIN == 'true')
    # or when not running in debug mode.
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        threading.Timer(1.0, _open_browser).start()

    app.run(debug=True)