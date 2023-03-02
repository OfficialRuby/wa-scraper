class Validator:
    '''Helper class to create validations '''

    def __init__(self) -> None:
        self.is_valid = False

    def validate_link(self, url: str):
        '''validate urls'''
        if url.startswith('blob'):
            self.validated_link = url
            self.is_valid = True
        return self.is_valid
