class Query:
    # Three types of queries:
    #   - CREATE
    #   - INSERT
    #   - SELECT

    base: str

    def __init__(self, base: str = "SELECT"):
        if base.upper() not in ('CREATE', 'SELECT', 'INSERT'):
            msg = "Expected base to be one of CREATE, SELECT, or INSERT. "
            msg += f"Was: {base}"
            raise ValueError(msg)
        self.base = base.upper()

    def __str_create__(self):
        query = self.base + \
            " TABLE "

    def __str__(self):
        if self.base == 'CREATE':
            return self.__str_create__()
        if self.base == 'INSERT':
            return self.__str_insert__()
        if self.base == 'SELECT':
            return self.__str_select__()
