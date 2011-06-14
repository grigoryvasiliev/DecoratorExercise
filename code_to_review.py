def CreateHash(data):
	import hashlib, uuid
	data = data.encode( "utf-8" )
	return hashlib.md5( data ).hexdigest().upper()

def cache_lock(func):
	def wrapped(*arg, **kwargs):
		import win32event, pywintypes
		mutex_name = CreateHash( arg[0] + arg[1] + func.func_name )		
		hMutex = win32event.CreateMutex(None, pywintypes.FALSE, mutex_name )
		win32event.WaitForSingleObject(hMutex, 30000)
		try:
			return func(*arg, **kwargs)
		finally:
			win32event.ReleaseMutex(hMutex)			
	return wrapped		

def cached(func):
	def wrapped(*arg, **kwargs):
		
		hsh = CreateHash(  arg[0] + arg[1] + func.func_name )
				
		val = AutorizationCache.objects.filter(hash = hsh)
		
		if val.count() and (datetime.now() - val[0].saved).seconds <= settings.AUTHORIZATION_CACHE_AGE:			
		
			return val[0].value
			
		else:
			
			res = func(*arg, **kwargs)
			val.delete()							
			cache = AutorizationCache(hash = hsh, value = res, saved = datetime.now())
			cache.save()
			return res
	
	f = wrapped	
	f.func_name = func.func_name
	return f	

@cache_lock	
@cached
def f(a, b):
	# do some work here and make result value
	return result
