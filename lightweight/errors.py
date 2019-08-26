class NoSourcePath(Exception):
    def __init__(self):
        super().__init__('Content does not contain a valid `source_path`')