class Validator:
    '''Helper class to create validations '''

    def __init__(self) -> None:
        self.is_valid = False
        self.validated_link = None
        self.plain_link = None

    def validate_link(self, url: str):
        '''validate urls'''
        if url.startswith('blob'):
            self.validated_link = url
            self.is_valid = True
        return self.validated_link

    @property
    def get_plain_link(self):
        blob_link = self.validated_link
        plain_link = blob_link.replace('blob:', '')
        return plain_link


def validate_b64_string(b64_string: str) -> str:
    _, string = b64_string.split(',')
    return string
