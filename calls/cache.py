import hashlib
import os
import json
import time
import random

class tools():
    def sha1(data):
        hashObject = hashlib.sha1(data.encode('utf-8'))
        return hashObject.hexdigest()

class deezer():
    def __init__(self, url=None):
        # Setting up hash
        if not url == None:
            if url.find('https://') == -1:
                url = 'https://api.deezer.com' + url
            else:
                url = url
            
            self.url = url
            self.hash = tools.sha1(url)
            self.cachePath = './cache/deezer/' + self.hash[0:2] + '/'
    
    def exist(self):
        # Gets hash and check if it exists or not
        os.makedirs(self.cachePath, exist_ok=True)
        if os.path.exists(self.cachePath + self.hash):
            return True
        else:
            return False
    
    def get(self, filetype='content'):
        # Gets hash and return cached version
        with open(self.cachePath + self.hash, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())
            
            if filetype == 'content':
                if data['context']['filetype'] == 'json':
                    return data['content']
                elif data['context']['filetype'] == 'bytes':
                    return bytes.fromhex(data['content'])
            elif filetype == 'context':
                return data['context']
            elif filetype == 'all':
                return data
    
    def save(self, data, filetype='json'):
        # Sets the data in a valid form
        if filetype == 'bytes':
            data = data.hex()
        
        if filetype == 'everything':
            content = json.dumps(data, indent=4)
        else:
            context = {
                'filetype': filetype,
                'timeCached': round(time.time()),
                'url': self.url
            }

            # Remember custom context points
            if os.path.exists(self.cachePath + self.hash):
                oldContext = self.get('context')
                for key in oldContext.keys():
                    if not key in context.keys():
                        context[key] = oldContext['old']

            content = json.dumps({
                'content': data,
                'context': context
            }, indent=4)
        
        # Save the given data into the cache
        with open(self.cachePath + self.hash, 'w', encoding='utf-8') as file:
            file.write(content)
            
    def setValue(self, name, value):
        # Sets a value inside the context of the cache
        data = self.get(filetype='all')
        data['context'][name] = value
        self.save(data, filetype='everything')
            
    def returnAllCaches():
        # Returns all caches from the database
        list = []
        for outPath in os.listdir('./cache/deezer/'):
            for file in os.listdir('./cache/deezer/' + outPath):
                filePath = './cache/deezer/' + outPath + '/' + file
                
                with open(filePath, 'r', encoding='utf-8') as file:
                    data = json.loads(file.read())['context']
                    list.append({'url': data['url'], 'filetype': data['filetype']})

        random.shuffle(list)

        return list

class youtube():
    def returnPathToSaveAudio(id, filetype):
        # Returns a valid path to write a audio file to
        hash = tools.sha1(id)
        path = f'./cache/audio/{hash[0:2]}/'
        filePath = f'{path}{hash}.{filetype}'
        
        os.makedirs(path, exist_ok=True)
        return filePath, os.path.exists(filePath)