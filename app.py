import random
import string
import jinja2
import cherrypy
import redis
import json
from jinja2 import Environment, PackageLoader, select_autoescape
from util_preprocess import PreProcess
import logging
import os 

logger = logging.getLogger(__name__)

class SearchStock(object):
    def __init__(self):
      self.env = Environment(
                loader=PackageLoader('app', 'templates'),
                autoescape=select_autoescape(['html', 'xml'])
                )
      self.conn_redis()
    
    def conn_redis(self):
      self.client = redis.Redis()

    @cherrypy.expose
    def index(self):
        return self.env.get_template('index.html').render({"title":"BhavCopySearch"})

    @cherrypy.expose
    def generate(self, length=8):
        return ''.join(random.sample(string.hexdigits, int(length)))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def fetch(self, name="*", limit=None):
      name = name.upper()
      print(name)
      name.lstrip()
      name.rstrip()
      li = []
      for i, item in enumerate(self.client.hscan_iter("stock_codes", match=name)):
        if limit is not  None and i >= int(limit):
          break
        li.append([item[0].decode('UTF-8'), json.loads(item[1])])
      return li

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def keys(self):
      print("Fetching keys")
      li = self.client.hkeys('stock_codes')
      li = [name.decode('UTF-8') for name in li]
      return li

    @cherrypy.expose
    def reload(self):
      pp = PreProcess()
      pp.run()
      raise cherrypy.HTTPRedirect('/keys')

if __name__ == '__main__':
  conf = {
        '/': {
          'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__))
        },
       '/static': {
         "tools.staticdir.on": True,
         "tools.staticdir.dir": "./static"
       }
      }

  cherrypy.quickstart(SearchStock(), config=conf)
