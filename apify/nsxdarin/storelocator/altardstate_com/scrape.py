from sgrequests import SgRequests
from sglogging import SgLogSetup
import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("altardstate_com")


def fetch_data():
    url = "https://www.altardstate.com/on/demandware.store/Sites-altardstate-Site/default/Stores-FindStores?showMap=true&radius=5000&postalCode=55441&radius=300"
    r = session.get(url, headers=headers)
    website = "altardstate.com"
    typ = "<MISSING>"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["stores"]:
        store = item["ID"]
        name = item["name"]
        add = item["address1"]
        city = item["city"]
        state = item["stateCode"]
        country = item["countryCode"]
        lat = item["latitude"]
        lng = item["longitude"]
        zc = item["postalCode"]
        phone = item["phone"]
        hours = str(item["storeHours"])
        try:
            hours = (
                hours.split("<td>", 1)[1]
                .replace("\n", "")
                .replace("\r", "")
                .replace("\t", "")
            )
            hours = hours.replace("</td>    </tr>    <tr>        <td>", "; ")
            hours = (
                hours.replace("</td><td>", ": ")
                .replace("</td></tr><tr><td>", "; ")
                .replace("</td>    </tr></table>", "")
                .replace("</td></tr></tbody></table>", "")
            )
        except:
            hours = "<MISSING>"
        yield SgRecord(
            locator_domain=website,
            page_url=loc,
            location_name=name,
            street_address=add,
            city=city,
            state=state,
            zip_postal=zc,
            country_code=country,
            phone=phone,
            location_type=typ,
            store_number=store,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours,
        )


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
