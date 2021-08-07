class School:
    """
    Class representing a school

    @type name: str
    @type GUID: str
    @ivar all_records: all records (SAT, GPA, MAJOR)
    """

    def __init__(self, name: str, GUID: str, all_records):
        self.name = name
        self.GUID = GUID
        self.all_records = all_records
