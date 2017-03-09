iteration = 0
current_url = ""

def incrementIteration():
    global iteration
    iteration += 1
    return iteration

def setIteration(i):
    global iteration
    iteration = i

def getIteration():
    global iteration
    return iteration

def setCurrentURL(url):
    global current_url
    current_url = url

def getCurrentURL():
    global current_url
    return current_url



