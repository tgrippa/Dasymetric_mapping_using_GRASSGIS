import random, string

def random_string(N):
    '''
    Function generating a random string of size N. 
	Usefull to generate random name of temporary layers.
    '''
    prefix=random.choice(string.ascii_uppercase + string.ascii_lowercase)
    suffix=''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))
    return prefix+suffix