import termcolor
import pandas as pd
from .validator_utils import ValidatorUtils
from .abstract_checker import AbstractChecker


class DuplicationChecker(AbstractChecker):
    def __init__(self, data, debug):
        self.data = data
        self.debug = debug
        self.identityKeys = ["street_address", "city", "state", "zip", "country_code", "location_type"]
        self.latLngKeys = ["latitude", "longitude"]

    def check(self):
        print(termcolor.colored("Checking for duplicate rows in the data...", "blue"))
        identityDuplicates = self.checkForIdentityDuplicates()
        latLngDuplicates = self.checkLatLngsWithMultipleAddresses()
        self.warnIfSameAddrHasMultipleLatLngs()
        if len(identityDuplicates) == 0 and len(latLngDuplicates) == 0:
            print(termcolor.colored("No duplicates found...", "green"))

    def checkLatLngsWithMultipleAddresses(self):
        """
        This check will work slightly differently than checkForIdentityDuplicates because we don't want to drop
        duplicates here. The reason is because you might have a case where 2 POI share an address but have a different
        lat/lng (e.g. for a walmart and a walmart pharmarcy), in which case dropping duplicates will give you different
        results based on which of the duplicates you keep in your result set.

        So, a better strategy here is to group by <lat, lng> and see how many difference addresses belong to each
        one. If the number greater than 1, something is wrong.
        """
        resUnfiltered = self.data.groupby(self.latLngKeys)["street_address"].apply(set).reset_index()
        resUnfiltered["num_addrs"] = resUnfiltered["street_address"].apply(len)
        res = resUnfiltered[resUnfiltered["num_addrs"] > 1]
        res.rename(columns={"latitude": "same_lat_count", "longitude": "same_lng_count"}, inplace=True)
        if len(res) > 0:
            ValidatorUtils.fail("Found {} <lat, lng> pair(s) that belong to multiple addresses. Examples:\n{}\n"
                                .format(len(res), res.head(10)), self.debug)
        return res

    def checkForIdentityDuplicates(self):
        duplicateRows = self.getDuplicateRows(self.data, self.identityKeys)
        debugExamples = duplicateRows[self.identityKeys].head(10)
        if len(duplicateRows) > 0:
            ValidatorUtils.fail("Found {} duplicate rows in data. Examples:\n{}\n"
                                .format(len(duplicateRows), debugExamples), self.debug)
        return duplicateRows

    @staticmethod
    def getDuplicateRows(df, keys):
        return df[df.duplicated(subset=keys)]

    def warnIfSameAddrHasMultipleLatLngs(self):
        resUnfiltered = self.data.groupby(["street_address"])[self.latLngKeys].nunique().reset_index()
        res = resUnfiltered[resUnfiltered["latitude"] > 1]
        if len(res) > 0:
            message = "WARNING: We found {} cases where a single address has multiple <lat, lngs>. Are you sure you" \
                      " scraped correctly? Examples:\n{}\n".format(len(res), res.head(10))
            print(termcolor.colored(message, "yellow"))
        return res
