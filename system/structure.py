class ProcessQueue:
    def __init__(self, items=None):
        self.queue = []
        self.size = None
        if isinstance(items, list):
            self.queue = items

    def enqueue(self, item):
        if isinstance(item, str):
            self.queue.append(item)
        elif isinstance(item, list):
            self.queue.extend(item)

    def dequeue(self):
        _item = None
        if len(self.queue) > 0:
            _item = self.queue.pop(0)
        return _item

    def getItems(self):
        return self.queue

    def getSize(self):
        if self.size is None:
            self.size = len(self.queue)
        return self.size


class LinkQueue:
    def __init__(self):
        self.queue = {}

    def enqueue(self, company, link):
        if self.queue.has_key(company):
            self.queue[company].append(link)
        else:
            self.queue[company] = [link]

    def dequeue(self):
        if len(self.queue.keys()) < 0:
            return None

        _company = self.queue.keys()[0]
        _lst = self.queue[_company]
        _data = {'company': _company, 'link': _lst[0][0]}

        if len(self.queue[_company]) == 1:
            self.queue.pop(_company)
        else:
            self.queue[_company] = self.queue[_company][1:]
        return _data


class NextQueue:
    def __init__(self, items):
        self._queue = None
        if isinstance(items, list):
            self._queue = items

    def getNext(self, count):
        result = []
        if count >= len(self._queue):
            result = self
            self._queue = self._queue[:count]
        else:
            result = self._queue
            self._queue = []
        return result



