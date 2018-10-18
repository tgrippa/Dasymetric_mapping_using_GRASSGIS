#!/usr/bin/env python

import random, string

def random_string(N,user_prefix=None):
    '''
    Function generating a random string of size N. 
	Usefull to generate random name of temporary layers.
    '''
    prefix=random.choice(string.ascii_uppercase + string.ascii_lowercase)
    suffix=''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))
    if user_prefix:    
        return str(user_prefix)+prefix+suffix
    else:
        return prefix+suffix