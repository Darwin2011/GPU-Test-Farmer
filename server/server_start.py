import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

result_content_html = "template/result.html"

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("../" + result_content_html)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers = [(r"/", IndexHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()