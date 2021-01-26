import us

ca_provinces = [
    "alberta",
    "british columbia",
    "manitoba",
    "new brunswick",
    "newfoundland and labrador",
    "nova scotia",
    "ontario",
    "prince edward island",
    "quebec",
    "saskatchewan",
]
ca_provinces_codes = {
    "AB",
    "BC",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PE",
    "QC",
    "SK",
    "YT",
}


class Util:
    def get_country_by_code(self, code=""):
        if us.states.lookup(code):
            return "US"
        elif code in ca_provinces_codes:
            return "CA"
        else:
            return "<MISSING>"

    # us ex: 904 Bayonne Crossing Way, Bayonne, NJ 07002
    def parse_address_simple(self, address):
        address = address.split(",")
        street_address = self._valid("".join(address[:-2]))
        city = self._valid(address[-2])
        state = self._valid(address[-1].strip().split(" ")[0])
        zip = self._valid(address[-1].strip().split(" ")[1])
        country_code = self.get_country_by_code(state)
        return street_address, city, state, zip, country_code

    def _valid(self, val):
        if val:
            return val.strip()
        else:
            return "<MISSING>"
