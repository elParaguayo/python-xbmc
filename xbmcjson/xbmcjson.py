#!/bin/env python

import urllib, urllib2
import json
from StringIO import StringIO
import base64

PLAYER_VIDEO=1

class XBMCTransport(object):
  """Base class for XBMC transport"""
  def execute(self, method, args):
    pass

class XBMCJsonTransport(XBMCTransport):
  """HTTP Json transport"""
  def __init__(self, url, username='xbmc', password='xbmc'):
    self.url=url
    self.username=username
    self.password=password
    self.id = 0

  def execute(self, method, *args, **kwargs):
    header = {
        'Content-Type' : 'application/json',
        'User-Agent' : 'python-xbmc'        
        }
    
    # Use HTTP authentication from 
    # http://forum.xbmc.org/showthread.php?tid=127759&pid=1346728#pid1346728
    if self.password is not None and self.username is not None:
      base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
      header['Authorization'] = 'Basic %s' % (base64string)
    
    # Params are given as a dictionnary
    if len(args) == 1:
      args=args[0]
    # Use kwargs for param=value style
    else:
      args = kwargs
    params={}
    params['jsonrpc']='2.0'
    params['id']=self.id
    self.id +=1
    params['method']=method
    params['params']=args

    values=json.dumps(params)

    data = values
    
    try:
      req = urllib2.Request(self.url, data, header)
      response = urllib2.urlopen(req)
      the_page = response.read()
      if len(the_page) > 0 :
        return json.load(StringIO(the_page))
      else:
        return None # for readability
    # I know it's bad practice not to use exception type here
    # So sue me!
    # This catches all errors eg authentication error, page not found etc etc
    except:
      return None

class XBMC(object):
  """XBMC client"""
  def __init__(self, url, username=None, password=None):
    self.transport = XBMCJsonTransport(url, username, password)
    # Dynamic namespace class instanciation
    for cl in namespaces:
      s = "self.%s = %s(self.transport)"%(cl,cl)
      exec(s)
    def execute(self, *args, **kwargs):
      self.transport.execute(*args, **kwargs)

    self.pong = self.Ping()

  def Ping(self):
    result = self.JSONRPC.Ping()
    if result:
      return result.get("result") == "pong"
    else:
      return False

  def __nonzero__(self):
    return self.pong

class XBMCNamespace(object):
  """Base class for XBMC namespace."""
  def __init__(self, xbmc):
    self.xbmc = xbmc
  def __getattr__(self, name):
    klass= self.__class__.__name__
    method=name
    xbmcmethod = "%s.%s"%(klass, method)
    def hook(*args, **kwargs):
      return self.xbmc.execute(xbmcmethod, *args, **kwargs)
    return hook

# Dynamic namespace class injection
namespaces = ["VideoLibrary", "AudioLibrary", "Application", "Player", "Input", "System", "Playlist", "Addons", "AudioLibrary", "Files", "GUI" , "JSONRPC", "PVR", "xbmc"]
for cl in namespaces:
  s = """class %s(XBMCNamespace):
  \"\"\"XBMC %s namespace. \"\"\"
  pass
  """%(cl,cl)
  exec (s)
