from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()

headers = {
    "Request-Id": "|HTTDs.jfJ5R",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_data():

    streetlist = []
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

    pattern = re.compile(r"\s\s+")
    for statenow in states:

        url = (
            "https://www.alliedcash.com/service/location/getlocationsin?state="
            + statenow
            + "&radius=1000&brandFilter=Allied%20Cash"
        )

        loclist = session.get(url, headers=headers).json()

        for loc in loclist:

            title = loc["ColloquialName"]
            street = loc["Address1"] + " " + str(loc["Address2"])
            city = loc["City"]
            state = loc["StateCode"]
            pcode = loc["ZipCode"]
            phone = loc["FormattedPhone"]
            lat = loc["Latitude"]
            longt = loc["Longitude"]
            store = loc["StoreNum"]
            if title in streetlist:
                continue
            streetlist.append(title)
            link = "https://locations.alliedcash.com/locations" + loc["Url"]

            r = session.get(link, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            hours = (
                soup.find("table", {"class": "store-hours-details"})
                .text.replace("Day of the Week", "")
                .replace("Hours", "")
            )
            hours = re.sub(pattern, " ", hours).strip()

            yield SgRecord(
                locator_domain="https://www.alliedcash.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=str(store),
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
