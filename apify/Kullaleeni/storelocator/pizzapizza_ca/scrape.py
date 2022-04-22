from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


logger = SgLogSetup().get_logger("pizzapizza_ca")

session2 = SgRequests()
session1 = SgRequests()
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-request-id": "bd65600d-8669-4903-8a14-af88203add38",
    "session-token": "5e57f395-4453-44a4-9b02-8c73904b1168",
}
headers1 = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36",
    "x-request-id": "449704b9-6540-48b0-b9f2-432fa5dd1891",
    "session-token": "029149bd-86ba-4246-9d90-c6e3eb5ea850",
}


def fetch_data(sgw: SgWriter):

    url = "https://www.pizzapizza.ca/ajax/store/api/v1/province_cities"
    r = session.get(url, headers=headers).json()
    logger.info(r)
    for states in r:
        province = states["province_slug"]

        cities = states["cities"]
        for city in cities:

            mlink = (
                "https://www.pizzapizza.ca/restaurant-locator/"
                + province
                + "/"
                + city["city_slug"]
            )
            branchlink = (
                "https://www.pizzapizza.ca/ajax/store/api/v1/search/store_locator?province="
                + province
                + "&city="
                + city["city_slug"]
            )

            try:
                r1 = session.get(branchlink, headers=headers).json()
                r = r1["stores"]
            except:
                try:

                    r1 = session1.get(branchlink, headers=headers1).json()
                    r = r1["stores"]
                except:

                    r1 = session2.get(branchlink, headers=headers).json()
                    r = r1["stores"]
            for branch in r:

                title = branch["name"]
                street = branch["address"].lstrip()
                city = branch["city"]
                state = branch["province"]
                pcode = branch["postal_code"]
                store = str(branch["store_id"])
                hourlist = branch["operating_hours"]
                phone = branch["market_phone_number"]
                lat = branch["latitude"]
                longt = branch["longitude"]
                hours = ""
                for hr in hourlist:
                    hours = (
                        hours
                        + hr["label"]
                        + " "
                        + hr["start_time"]
                        + " - "
                        + hr["end_time"]
                        + "; "
                    )
                if hours.endswith("; "):
                    hours = "".join(hours[:-2])

                link = (
                    mlink
                    + "/"
                    + street.lstrip().lower().replace(" ", "-")
                    + "/"
                    + store
                )

                row = SgRecord(
                    locator_domain="https://www.pizzapizza.ca/",
                    page_url=link,
                    location_name=title,
                    street_address=street,
                    city=city,
                    state=state,
                    zip_postal=pcode,
                    country_code="CA",
                    store_number=store,
                    phone=phone,
                    location_type=SgRecord.MISSING,
                    latitude=lat,
                    longitude=longt,
                    hours_of_operation=hours,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
