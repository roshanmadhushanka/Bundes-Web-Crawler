# -*- coding: utf-8 -*-
import string
from pymongo import MongoClient
import pymongo
import config


class FileHandler:
    def __init__(self, file_name):
        self.file_name = file_name

    def read(self):
        '''
        Read from a specific file
        :return:
        '''
        _file = None
        _lines = None
        try:
            _file = open(self.file_name, 'r', encoding='utf-8')
            _lines = _file.readlines()
            _lines = [a.rstrip() for a in _lines if a != '\n']
        except UnicodeDecodeError:
            print("Unsupported text content")
            config.SYSTEM_STATE = "Unsupported text content"
            return
        except IOError:
            pass
        finally:
            if _file is not None:
                _file.close()
        return _lines

    def append(self, content):
        '''
        Append lines to a specific file
        :param content: String
        :return: None
        '''
        _file = None
        try:
            _file = open(self.file_name, 'a', encoding='utf-8')
            if isinstance(content, str):
                _file.write(content + '\n')
            elif isinstance(content, list):
                for line in content:
                    _file.write(line.encode('utf-8') + '\n')
        except IOError:
            print('IO Error')
            return
        finally:
            if _file is not None:
                _file.close()

    def write(self, content):
        '''
        Write contents to a specific file
        :param content: can be a string or list of strings
        :return: None
        '''
        _file = None
        try:
            _file = open(self.file_name, 'w', encoding='utf-8')
            if isinstance(content, str):
                _file.write(content)
            elif isinstance(content, list):
                content = [a + '\n' for a in content]
                _file.writelines(content)
        except IOError as e:
            pass
        finally:
            if _file is not None:
                _file.close()


class MongoHandler():
    def __init__(self):
        # Initialize handler parameters
        self._table_name = 'firm'
        self._host = "localhost"
        self._port = 27017
        self._client = MongoClient(self._host, self._port)
        self._db = self._client[self._table_name]
        self._posts = self._db.posts

    def insertDocument(self, document):
        # Insert document into the database
        self._posts.insert_one(document)

    def getAllDocuments(self):
        # Retrieve all the documents from database
        _cursor = self._posts.find({})
        _document_list = []
        for _document in _cursor:
            _document_list.append(_document)
        return _document_list

    def closeDatabaseClient(self):
        if isinstance(self._client, pymongo.mongo_client.MongoClient):
            self._client.close()

    def deleteAll(self):
        self._posts.delete_many({})









