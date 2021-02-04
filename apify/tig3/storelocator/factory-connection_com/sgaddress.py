import usaddress


# TODO
class SgAddress:

    __street_address = ""

    AddressNumberPrefix = ""
    AddressNumber = ""
    AddressNumberSuffix = ""

    StreetNamePreDirectional = ""
    StreetNamePreModifier = ""
    StreetNamePreType = ""
    StreetName = ""
    # TODO - IntersectionSeparator
    IntersectionSeparator = ""
    StreetNamePostDirectional = ""
    StreetNamePostModifier = ""
    StreetNamePostType = ""

    SubaddressType = ""
    SubaddressIdentifier = ""

    OccupancyType = ""
    OccupancyIdentifier = ""

    PlaceName = ""
    StateName = ""
    ZipCode = ""
    CountryCode = ""

    # TODO - to be discussed
    BuildingName = ""
    Recipient = ""

    def __init__(self, address_str):
        self.__parse(address_str)

    def __parse(self, address_str):
        try:
            address_dict = usaddress.parse(address_str)
        except usaddress.RepeatedLabelError as e:
            # ERROR: Unable to tag this string because more than one area of the string has the same label
            # handle this addresses without usaddress
            # TODO
            exit(f"Can not parse: {e.original_string}")

        for value, key in address_dict:
            if hasattr(self, key):
                setattr(self, key, getattr(self, key) + value + " ")

        self.__set_street_address()

    def __set_street_address(self):
        address = (
            self.AddressNumberPrefix.strip()
            + " "
            + self.AddressNumber
            + " "
            + self.AddressNumberSuffix
            + " "
            + self.StreetNamePreDirectional
            + " "
            + self.StreetNamePreModifier
            + " "
            + self.StreetNamePreType
            + " "
            + self.StreetName
            + " "
            + self.StreetNamePostDirectional
            + " "
            + self.StreetNamePostModifier
            + " "
            + self.StreetNamePostType
            + " "
            + self.SubaddressType
            + " "
            + self.SubaddressIdentifier
            + " "
            + self.OccupancyType
            + " "
            + self.OccupancyIdentifier
        )

        self.__street_address = self.filter(address)

    def street_address(self):
        return self.filter(self.__street_address)

    def city(self):
        return self.filter(self.PlaceName)

    def state(self):
        return self.filter(self.StateName)

    def zip(self):
        return self.filter(self.ZipCode)

    def country_code(self):
        return "TODO"

    def filter(self, val):
        val = " ".join(val.split())
        return val.strip(", ")
