from __future__ import print_function
import bokeh.server
import bokeh.server.start
if __name__ == "__main__":
    try:
        bokeh.server.run()
    except KeyboardInterrupt:
        bokeh.server.start.stop()
        print("Shutting down bokeh-server ...")
