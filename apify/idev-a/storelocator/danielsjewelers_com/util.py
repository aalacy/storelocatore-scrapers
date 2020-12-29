class Util:
    def parseHour(self, val):
        res = ""
        if int(val.split(":")[0]) > 12:
            res += str(int(val.split(":")[0]) - 12)
            res += ":" + val.split(":")[1] + " PM"
        else:
            res += val + " AM"
        return res

    def _valid(self, val):
        if val:
            return val.strip()
        else:
            return "<MISSING>"
