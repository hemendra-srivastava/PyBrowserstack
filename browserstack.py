import requests
import simplejson

uname = "hemendra26@gmail.com"
passwd = "browserstack"


class ImproperlyConfiguredException(Exception):
    pass

class BrowserStackException(Exception): pass
class AuthException(BrowserStackException): pass
class ForbiddenException(BrowserStackException): pass

class HttpException(BrowserStackException):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return "Received status code: " + repr(self.code)

class BrowserStackError(BrowserStackException):
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return self.message + repr(self.errors)

class BrowserObject(object):

    def __init__(self, **kwargs):
        kw = ['os', 'browser', 'device', 'version', 'timeout']
        self.payload = {}
        if kwargs.get('os'):
            self.payload['os'] = kwargs.get('os')
        else:
            raise NotImplementedError("OS field is required")
        
        if kwargs.get('browser'):
            self.payload['browser'] = kwargs.get('browser')
        elif kwargs.get('device'):
            self.payload['device'] = kwargs.get('device')
        else:
            raise NotImplementedError("One of, Browser OR Device, fields are required")
        if kwargs.get('version'):
            self.payload['version'] = kwargs.get('version')
        else:
            raise NotImplementedError("Version field is required")

        if type(kwargs.get('timeout')) == int:
            self.payload['timeout'] = kwargs.get('timeout') 
        else:
            self.payload['timeout'] = 300

    def __repr__(self):
        return "; ".join(["%s : %s" %(k,v) for k,v in self.payload.items()])
            
    def __str__(self):
        return "; ".join(["%s : %s" %(k,v) for k,v in self.payload.items()])

    def get_payload(self):
        return self.payload

    
class BrowserStack(object):
    
    def __init__(self, *args, **kwargs):
        self.VERSION_NO = kwargs.get('VERSION_NO') or 2
        self.url = "http://api.browserstack.com/"
        self.browser_list = []
        self.wdict = {}
        if kwargs.get('auth'):
            if not (len(kwargs.get('auth')) == 2):
                raise ImproperlyConfiguredException("Auth is a tuple of ('username', 'passwd')")
            self.auth = kwargs.get('auth')
        else:
            raise ImproperlyConfiguredException("Please define an auth=('username', 'passwd') tuple in object constructor")

    def _process_request(self, req):
        if req.status_code == 401:
            raise AuthException("Authentication Failure")
        elif req.status_code == 403:
            raise ForbiddenException("Your user is not allowed to access this resource")
        elif req.status_code == 200:
            return simplejson.loads(req.content)
        elif req.status_code == 422:
            raise BrowserStackError(**simplejson.loads(req.content))
        else:
            raise HttpException(req.status_code)
    
    def get_url(self):
        if type(self.VERSION_NO) == int:
            return self.url+"%s" %(self.VERSION_NO)
        else:
            raise ImproperlyConfiguredException("Version no must be int")

    def get_browser(self):
        if not self.browser_list:
            r = requests.get(self.get_url() + "/browsers", auth=self.auth)
            blist = self._process_request(r)
            for k, v in blist.items():
                for ele in v:
                    di = ele
                    di.update({'os':k})
                    b = BrowserObject(**di)
                    self.browser_list.append(b)

        return self.browser_list
    
    def create_worker(self, obj1, url):
        if obj1 in self.browser_list:
            payload = obj1.payload
        else:
            raise BrowserStackException("Invalid Browser Object")
        payload.update({'url':url})
        r = requests.post(self.get_url() + "/worker", auth=self.auth, params=payload)
        bid = self._process_request(r)
        self.wdict.update({bid['id']:obj1})
        return bid

    def get_active_workers(self):
        return self.wdict

    def delete_active_workers(self):
        wdict = dict([(ele['id'],ele['os']) for ele in self.get_workers()])
        aworkers = self.get_active_workers().keys()
        aworkers += [ele for ele in wdict.keys() if ele not in aworkers]

        return [self.delete_worker(ele) for ele in aworkers]

    def delete_worker(self, id):
        r = requests.delete(self.get_url() + "/worker/%s" %(id), auth=self.auth)
        return self._process_request(r)
        
    def get_worker_status(self, id):
        r = requests.get(self.get_url() + "/worker/%s" %(id), auth=self.auth)
        return self._process_request(r)

    def get_workers(self):
        r = requests.get(self.get_url()+ "/workers", auth=self.auth)
        return self._process_request(r)

b1 = BrowserStack(auth=('hemendra26@gmail.com','browserstack123'))
print b1.get_browser()
print b1.create_worker(b1.get_browser()[5], url="http://www.bcradio.in")
print b1.get_active_workers()
print b1.create_worker(b1.get_browser()[15], url="http://www.browserstack.com")
print b1.get_active_workers()
print b1.get_worker_status(b1.get_active_workers().keys()[0])
print b1.get_workers()
print b1.delete_active_workers()
print b1.get_active_workers()
print b1.get_workers()



        
# blist = get_browser()
# print blist
# print 
# print "Creating worker"
# print 

# kw = {}
# kw['os']="mac"
# kw.update(blist["mac"][0])
# kw['url'] = 'http://www.browserstack.com'

# w = create_worker(**kw)
# id = w['id']
# print w

# wlist = get_workers()
# id = wlist[0]['id']
# print get_worker_status(id)

# print delete_worker(id)

# print get_workers()

# print get_worker_status(id)


