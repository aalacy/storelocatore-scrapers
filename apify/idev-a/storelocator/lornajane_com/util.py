class Util:
    def _strip_list(self, val):
        return [_.strip() for _ in val if _.strip()]

    def _valid(self, val):
        if val:
            return val.strip()
        else:
            return "<MISSING>"

    def _valid1(self, val):
        if val:
            return val.strip()
        else:
            return ""

    def _digit(self, val):
        return "".join(i for i in val if i.isdigit())

    def _valid_phone(self, phone):
        _phone = self._valid(self._digit(phone))
        if _phone.startswith("1"):
            _phone = _phone[1:]
        return _phone

    def _check_duplicate_by_loc(self, data, _item):
        is_duplicated = False
        for x, item in enumerate(data):
            if item[11] == _item[11] and item[12] == _item[12]:
                data[x] = _item
                is_duplicated = True
                break

        if not is_duplicated:
            data.append(_item)
