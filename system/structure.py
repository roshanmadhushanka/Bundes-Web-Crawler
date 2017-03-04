class ProcessQueue:
    def __init__(self, items=None):
        self.queue = []
        if isinstance(items, list):
            self.queue = items

    def enqueue(self, item):
        if isinstance(item, str):
            self.queue.append(item)
        elif isinstance(item, list):
            self.queue.extend(item)

    def dequeue(self):
        item = None
        if len(self.queue) > 0:
            item = self.queue.pop(0)
        return item

    def getItems(self):
        return self.queue


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

        company = self.queue.keys()[0]
        lst = self.queue[company]
        data = {'company': company, 'link': lst[0][0]}

        if len(self.queue[company]) == 1:
            self.queue.pop(company)
        else:
            self.queue[company] = self.queue[company][1:]
        return data


