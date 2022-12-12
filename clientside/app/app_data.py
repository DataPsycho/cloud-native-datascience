import typing as t


def add_star(text: str) -> str:
    """Add start as mandatory marker in the form Header"""
    return text + "*"


class FormHeaderRepo:
    """Form header repository for all form header."""
    PID = add_star('Select Project Identifier (PID)')
    USER = add_star('Insert Identifier')
    DICT_SECTION = add_star('Select Dictionary Type')
    JOB_STATUS = add_star("Job Status Type")
    UPLOAD_DOCX = add_star("Upload Document")
    SECRET = add_star("Insert Secret")

    @staticmethod
    def add_marker(text: str) -> str:
        """Add * to the any custom field"""
        return text + "*"


class FormUtils:
    """Additional utility function for manipulating form"""
    BLANK = "---"

    @staticmethod
    def get_dummy_pid() -> t.Tuple:
        return '---', 'DummyProject'

    def add_blank(self, dropdown: t.List) -> t.List:
        """Add --- blanc identifier into the list"""
        return [self.BLANK] + dropdown
