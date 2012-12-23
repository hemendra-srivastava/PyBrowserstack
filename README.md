Usage:

    from browserstack import BrowserStack, BrowserObject
    
    b1 = BrowserStack(auth=("username", "passwd"))
    blist = b1.get_browser()
    wid = b1.create_worker(blist[5], url="http://www.google.com/")  # Takes browserobject as input
    
    bobj = BrowserObject(os="mac", browser="", version="", timeout=300) # Creates new browserobject Class exists for validation
    wdict = b1.get_active_workers() # Returns dict of {id:browserobject} for workers created this session
    
    b1.delete_worker(id) # Deletes worker with id
    b1.get_worker_status(id) # Gets status of worker with id
    
    b1.get_workers() # Gets list of all active workers including those activated in previous sessions
    
    b1.delete_active_workers() # Deletes all active workers including those created in previous sessions
    
    
    # Given a browserobject bobj
    bobj.get_payload() # Prints the attributes for the browser object that will be passed to the create_worker function