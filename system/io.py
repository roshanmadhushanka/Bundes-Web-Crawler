# -*- coding: utf-8 -*-


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
        except IOError:
            print("IO Error")
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
        except IOError:
            pass
        finally:
            if _file is not None:
                _file.close()





