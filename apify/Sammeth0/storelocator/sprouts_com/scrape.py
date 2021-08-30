from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger("sprouts.com")

session = SgRequests()

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
headers = {"User-Agent": user_agent}


def fetch_data(sgw: SgWriter):
    url = "https://shop.sprouts.com/api/v2/stores"
    loclist = session.get(url, headers=headers, verify=False).json()["items"]
    for loc in loclist:
        street = loc["address"]["address1"]
        if str(loc["address"]["address2"]) != "None":
            street = street + " " + str(loc["address"]["address2"])
        city = loc["address"]["city"]
        pcode = loc["address"]["postal_code"]
        state = loc["address"]["province"]
        link = loc["external_url"]
        phone = loc["phone_number"]
        store = loc["id"]
        title = loc["name"]
        lat = loc["location"]["latitude"]
        longt = loc["location"]["longitude"]
        log.info(link)
        try:
            r = session.get(link, headers=headers, verify=False)
            hours = r.text.split('"openingHours":"', 1)[1].split('"', 1)[0]
        except:
            link = ""
            hours = ""

        sgw.write_row(
            SgRecord(
                locator_domain="https://www.sprouts.com/",
                page_url=link,
                location_name=title,
                street_address=street,
                city=city,
                state=state,
                zip_postal=pcode,
                country_code="US",
                store_number=store,
                phone=phone,
                location_type="<MISSING>",
                latitude=lat,
                longitude=longt,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
