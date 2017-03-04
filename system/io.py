class FileHandler:
    def __init__(self, file_name):
        self.file_name = file_name

    def read(self):
        _file = None
        _lines = None
        try:
            _file = open(self.file_name, 'r')
            _lines = _file.readlines()
            _lines = [a.rstrip() for a in _lines if a != '\n']
        except IOError:
            pass
        finally:
            if _file is not None:
                _file.close()
        return _lines

    def append(self, line):
        _file = None
        if isinstance(line, str):
            try:
                _file = open(self.file_name, 'a')
                _file.write(line + '\n')
            except IOError:
                pass
            finally:
                if _file is not None:
                    _file.close()

    def write(self, content):
        _file = None
        try:
            _file = open(self.file_name)
            if isinstance(content, str):
                _file.write(content)
            elif isinstance(content, list):
                _file.writelines(content)
        except IOError:
            pass
        finally:
            if _file is not None:
                _file.close()


