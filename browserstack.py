import requests
import simplejson

class ImproperlyConfiguredException(Exception): pass
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
    """ Serves the purpose of validation for browser payload """

    def __init__(self, **kwargs):
        """ Takes in OS, browser or device, version, timeout(optional) as keyword arguments """
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
        """ Get the payload required for POST request for creating worker """
        return self.payload

    
class BrowserStack(object):
    """ API Class for browserstack API Calls """
    
    def __init__(self, **kwargs):
        """ 
        Initialisation for api 
        Kwargs must contain auth tuple of ("username", "password")
        """
        
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

    def _process_response(self, req):
        """ This function processes response from an API call and returns the corresponding response based on the request status_code """
        
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
        """ gets api url, appends version number and returns complete url for making api call """
        if type(self.VERSION_NO) == int:
            return self.url+"%s" %(self.VERSION_NO)
        else:
            raise ImproperlyConfiguredException("Version no must be int")

    def get_browser(self, reset=False):
        """ 
        Gets list of available browsers creates corresponding browserobjects
        """
        if (not self.browser_list) or reset:
            r = requests.get(self.get_url() + "/browsers", auth=self.auth)
            blist = self._process_response(r)
            for k, v in blist.items():
                for ele in v:
                    di = ele
                    di.update({'os':k})
                    b = BrowserObject(**di)
                    self.browser_list.append(b)

        return self.browser_list
    
    def create_worker(self, obj1, url):
        """
        Creates worker and returns id. 
        Takes Browser Object and URL to be tested as arguments for the function.
        """
        if obj1 in self.browser_list:
            payload = obj1.payload
        else:
            raise BrowserStackException("Invalid Browser Object")
        payload.update({'url':url})
        r = requests.post(self.get_url() + "/worker", auth=self.auth, params=payload)
        bid = self._process_response(r)
        self.wdict.update({bid['id']:obj1})
        return bid

    def get_active_workers(self):
        """
        Returns dict of active workers from this session. (locally cached)
        Dict contains {id:object}
        """
        return self.wdict
    
    def delete_active_workers(self):
        """
        Delete all active workers across all sessions. 
        """
        wdict = dict([(ele['id'],ele['os']) for ele in self.get_workers()])
        aworkers = self.get_active_workers().keys()
        aworkers += [ele for ele in wdict.keys() if ele not in aworkers]

        return [self.delete_worker(ele) for ele in aworkers]

    def delete_worker(self, id):
        """
        Takes id as input and deletes corresponding worker
        """
        r = requests.delete(self.get_url() + "/worker/%s" %(id), auth=self.auth)
        return self._process_response(r)
        
    def get_worker_status(self, id):
        """
        Gets worker status given a worker id
        """
        r = requests.get(self.get_url() + "/worker/%s" %(id), auth=self.auth)
        return self._process_response(r)

    def get_workers(self):
        """
        Gets all active workers from API call.
        """
        r = requests.get(self.get_url()+ "/workers", auth=self.auth)
        return self._process_response(r)


if __name__ == '__main__':
    
    b1 = BrowserStack(auth=('username','passwd'))
    print b1.get_browser()
    print b1.create_worker(b1.get_browser()[5], url="http://www.google.com")
    print b1.get_active_workers()
    print b1.create_worker(b1.get_browser()[15], url="http://www.browserstack.com")
    print b1.get_active_workers()
    print b1.get_worker_status(b1.get_active_workers().keys()[0])
    print b1.get_workers()
    print b1.delete_active_workers()
    print b1.get_active_workers()
    print b1.get_workers()

