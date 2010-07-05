
from django.core.files.uploadedfile import UploadedFile

class _ExistingFile(UploadedFile):
    ''' Utility class for importing existing files to FileField's. '''
    # from http://stackoverflow.com/questions/1300033/avoid-copying-when-adding-a-large-file-to-filefield

    def __init__(self, path, *args, **kwargs):
        self.path = path
        super(_ExistingFile, self).__init__(*args, **kwargs)

    def temporary_file_path(self):
        return self.path

    def close(self):
        pass

    def __len__(self):
        return 0