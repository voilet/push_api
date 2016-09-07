#!/usr/bin/env python
 
import logging
 
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define, options
from tornado.process import Subprocess
 
define("port", default=7777, help="Run server on a specific port", type=int)
 
html_template = """
<!DOCTYPE html>
<html>
<head>
  <title>tornado WebSocket example</title>
  <link href="//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.1/css/bootstrap-combined.no-icons.min.css" rel="stylesheet">
  <script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
</head>
<body>
  <div class="container">
    <h1>tornado WebSocket example</h1>
    <hr>
      WebSocket status : <span id="message"></span>
    <hr>
    <pre>
      <div id="content">
      </div>
    </pre>
  </div>
  <script>
    var ws = new WebSocket('ws://localhost:7777/tail');
    var $message = $('#message');
    var $content = $('#content');
    ws.onopen = function(){
      $message.attr("class", 'label label-success');
      $message.text('open');
    };
    ws.onmessage = function(ev){
      $message.attr("class", 'label label-info');
      $message.hide();
      $message.fadeIn("fast");
      $message.text('received message');
      $content.append(ev.data);
    };
    ws.onclose = function(ev){
      $message.attr("class", 'label label-important');
      $message.text('closed');
    };
    ws.onerror = function(ev){
      $message.attr("class", 'label label-warning');
      $message.text('error occurred');
    };
  </script>
</body>
</html>
"""
 
 
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(html_template)
 
 
class LogStreamer(tornado.websocket.WebSocketHandler):
    def open(self):
        filename = "/tmp/simple_foobar.log"
        self.proc = Subprocess(["tail", "-f", filename, "-n", "0"],
                               stdout=Subprocess.STREAM,
                               bufsize=1)
        self.proc.set_exit_callback(self._close)
        self.proc.stdout.read_until("\n", self.write_line)
 
    def _close(self, *args, **kwargs):
        self.close()
 
    def on_close(self, *args, **kwargs):
        logging.info("trying to kill process")
        self.proc.proc.terminate()
        self.proc.proc.wait()
 
    def write_line(self, data):
        logging.info("Returning to client: %s" % data.strip())
        self.write_message(data.strip() + "<br/>")
        self.proc.stdout.read_until("\n", self.write_line)
 
 
application = tornado.web.Application([
    (r"/", IndexHandler),
    (r"/tail", LogStreamer),
])
 
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    tornado.options.parse_command_line()
    http_server.listen(options.port)
    logging.info("TornadoLog started. Point your browser to http://localhost:%d/tail" %
                 options.port)
    tornado.ioloop.IOLoop.instance().start()