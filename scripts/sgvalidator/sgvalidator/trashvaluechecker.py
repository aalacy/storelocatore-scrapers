class TrashValueChecker:
    """
    Checks for trash values in the data, like "null" or HTML tags, both when they're
    standalone and also when they're mixed with other data, e.g. "Bob's Burgers null"
    """
    BAD_TOKENS = ["null", "<", ">"]

    @staticmethod
    def findTrashValues(row):
        res = {}
        for key, value, in row.items():
            badTokensInValue = list(filter(lambda x: x in value, TrashValueChecker.BAD_TOKENS))
            if len(badTokensInValue) > 0:
                res[key] = value
        if len(res.keys()) == 0:
            return None
        else:
            return res
