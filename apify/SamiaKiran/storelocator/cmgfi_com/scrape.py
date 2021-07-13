import json
import usaddress
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from fuzzywuzzy import process

session = SgRequests()
website = "cmgfi_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://cmgfi.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        states = [
            "AL",
            "AK",
            "AZ",
            "AR",
            "CA",
            "CO",
            "CT",
            "DC",
            "DE",
            "FL",
            "GA",
            "HI",
            "ID",
            "IL",
            "IN",
            "IA",
            "KS",
            "KY",
            "LA",
            "ME",
            "MD",
            "MA",
            "MI",
            "MN",
            "MS",
            "MO",
            "MT",
            "NE",
            "NV",
            "NH",
            "NJ",
            "NM",
            "NY",
            "NC",
            "ND",
            "OH",
            "OK",
            "OR",
            "PA",
            "RI",
            "SC",
            "SD",
            "TN",
            "TX",
            "UT",
            "VT",
            "VA",
            "WA",
            "WV",
            "WI",
            "WY",
        ]
        for state in states:
            url = (
                "https://www.cmgfi.com/webapi/search/branch?searchType=state&userInput="
                + state
            )
            loclist = session.get(url, headers=headers).json()
            loclist = json.loads(loclist)["items"]
            for loc in loclist:
                page_url = "https://www.cmgfi.com" + loc["branchUrl"]
                log.info(page_url)
                location_name = loc["name"]
                address = loc["address"]
                address = address.replace(",", " ")
                address = usaddress.parse(address)
                i = 0
                street_address = ""
                city = ""
                state = ""
                zip_postal = ""
                while i < len(address):
                    temp = address[i]
                    if (
                        temp[1].find("Address") != -1
                        or temp[1].find("Street") != -1
                        or temp[1].find("Recipient") != -1
                        or temp[1].find("Occupancy") != -1
                        or temp[1].find("BuildingName") != -1
                        or temp[1].find("USPSBoxType") != -1
                        or temp[1].find("USPSBoxID") != -1
                    ):
                        street_address = street_address + " " + temp[0]
                    if temp[1].find("PlaceName") != -1:
                        city = city + " " + temp[0]
                    if temp[1].find("StateName") != -1:
                        state = state + " " + temp[0]
                    if temp[1].find("ZipCode") != -1:
                        zip_postal = zip_postal + " " + temp[0]
                    i += 1
                country_code = "US"
                phone = loc["phone"]
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone.strip(),
                    location_type=MISSING,
                    latitude=MISSING,
                    longitude=MISSING,
                    hours_of_operation=MISSING,
                )


def remakeSgRecord(record):
    return SgRecord(
        page_url=str(record[0]),
        location_name=str(record[1]),
        street_address=str(record[2]),
        city=str(record[3]),
        state=str(record[4]),
        zip_postal=str(record[5]),
        country_code=str(record[6]),
        store_number=str(record[7]),
        phone=str(record[8]),
        location_type=str(record[9]),
        latitude=str(record[10]),
        longitude=str(record[11]),
        locator_domain=str(record[12]),
        hours_of_operation=str(record[13]),
        raw_address=str(record[14]),
    )


def dedupe(dataset):
    copy = []

    for i in dataset:
        copy.append(json.dumps(i.as_row()))

    z = process.dedupe(copy, threshold=90)  # dict.keys() without duplicates
    k = copy - z  # set of duplicates
    z = list(z)  # list without duplicates
    k = list(k)  # list of duplicates
    i = 0
    while i < len(copy):
        if i < len(z):
            rec = json.loads(z[i])
            yield remakeSgRecord(rec)
        else:
            rec = json.loads(k[i - len(z)])
            rec.pop(-1)
            rec.append("<DUPLICATE>")
            yield remakeSgRecord(rec)
        i += 1


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = dedupe(fetch_data())
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
