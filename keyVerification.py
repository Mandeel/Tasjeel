# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 13:43:20 2024

@author: Thulfiqar
"""

import random
import re

def verify(key):
    
    key = key.lower()
    score = 0
    check_digit = key
    check_digit_count = 0
    chunks = key.split('-')
    

    for chunk in chunks:
        if len(chunk) != 4:
            return False
        for char in chunk:
            if len(re.findall(check_digit[0], key)) != 3:
                return False
            score += ord(char)
            
    print(chunks)
    print(score)
    print(check_digit_count)
    if score == 1612 and len(re.findall(check_digit[0], key)) == 3:
        return True
    return False
    
    
    
if verify('1154-1FXX-8BZ5-HJ3B-2P7Q'):
    print('valid')

else:
    print('wrong key')