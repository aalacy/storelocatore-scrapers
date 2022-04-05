from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("northwest_bank")

session = SgRequests(verify_ssl=False)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data(sgw: SgWriter):

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

    url = "https://www.northwest.bank/branch-locations/"

    for statenow in states:
        logger.info(statenow)
        payload = {"searchText": statenow}
        req = session.post(url, data=payload)
        soup = BeautifulSoup(req.text, "html.parser")

        try:
            loclist = soup.find_all(class_="card-body p-5")
            if not loclist:
                continue
        except:
            continue

        for loc in loclist:

            title = "<MISSING>"
            street = loc.h5.text
            raw_data = list(loc.p.stripped_strings)
            city_line = raw_data[0].strip().split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            pcode = city_line[-1].strip().split()[1].strip().replace("v", "")
            if len(loc.findAll("h2")) < 2:
                temp = loc.find(
                    "i", {"class": "icon icon-saving-bank-fill text-primary"}
                )
                if not temp:
                    continue
            try:
                phone = raw_data[1].split("(")[0]
            except:
                phone = ""
            try:
                hours = " ".join(list(loc.table.stripped_strings))
            except:
                hours = ""
            lat, longt = "", ""

            sgw.write_row(
                SgRecord(
                    locator_domain="https://www.northwest.bank/",
                    page_url="https://www.northwest.bank/branch-locations/",
                    location_name=title,
                    street_address=street,
                    city=city,
                    state=state,
                    zip_postal=pcode,
                    country_code="US",
                    store_number="<MISSING>",
                    phone=phone,
                    location_type="<MISSING>",
                    latitude=lat,
                    longitude=longt,
                    hours_of_operation=hours,
                )
            )


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
