import threading
import time

class instance():
    def __init__(self, function, maxThreads=10):
        self.activeThreads = []
        for threadId in range(maxThreads):
            thread = threading.Thread(target=self.handler, args=(threadId, function, ))
            self.activeThreads.append({'status': 'waiting', 'data': None, 'alive': True, 'handlerThread': thread})
            thread.start()
            
    def handler(self, threadId, target):
        while True:
            if not self.activeThreads[threadId]['alive'] and self.activeThreads[threadId]['data'] ==  None:
                break
            elif not self.activeThreads[threadId]['data'] == None:
                self.activeThreads[threadId]['status'] = 'working'
                
                data = self.activeThreads[threadId]['data']
                target(*data['args'], **data['kwargs'])

                self.activeThreads[threadId]['status'] = 'waiting'
                self.activeThreads[threadId]['data'] = None
            else:
                time.sleep(0.25)
            
    def run(self, *args, **kwargs):
        try:
            keep = True
            while keep:
                didSomething = False
                for activeThread in self.activeThreads:
                    if activeThread['data'] == None and activeThread['alive'] and activeThread['status'] == 'waiting':
                        activeThread['data'] = {'args': args, 'kwargs': kwargs}
                        keep = False
                        didSomething = True
                        break
                
                if not didSomething:
                    time.sleep(0.25)
        except KeyboardInterrupt:
            print('easyThreader unexpected stopping!')
            self.stop()
            exit()

    def stop(self):
        for activeThread in self.activeThreads:
            activeThread['alive'] = False
            
        for activeThread in self.activeThreads:
            activeThread['handlerThread'].join()
