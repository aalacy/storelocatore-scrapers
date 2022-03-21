from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import dirtyjson as json

logger = SgLogSetup().get_logger("bodynbrain")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.bodynbrain.com"
base_url = "https://www.bodynbrain.com/locations"


def fetch_records(http):
    areas = bs(http.get(base_url, headers=_headers).text, "lxml").select(
        "ul.centerList li.link a"
    )
    for area in areas:
        url = locator_domain + area["href"]
        logger.info(url)

        sp1 = bs(http.get(url, headers=_headers).text, "lxml")
        ss = sp1.find("script", type="application/ld+json").string
        try:
            _ = json.loads(ss)[0]
        except:
            _ = json.loads(
                ss.replace(": https", ': "https').replace(',"open', '","open')
            )[0]
        addr = _["address"]
        street_address = (
            addr["streetAddress"].split(addr["addressLocality"].strip())[0].strip()
        )
        if street_address.isdigit():
            street_address = addr["streetAddress"].strip()
        hours = []
        days = [
            dd.text.strip().split()[0] for dd in sp1.select("aside.sidebar h5.date")
        ]
        times = [
            dd.select("p")[-1].text.strip()
            for dd in sp1.select("aside.sidebar div.DateClass div.eventClass")
        ]
        for x in range(len(days)):
            hours.append(f"{days[x]}: {times[x]}")
        yield SgRecord(
            page_url=url,
            location_name=_["name"],
            street_address=street_address,
            city=addr["addressLocality"].strip(),
            state=addr["addressRegion"].strip(),
            zip_postal=addr["postalCode"].strip(),
            country_code="US",
            phone=_["telephone"],
            latitude=_["geo"]["latitude"],
            longitude=_["geo"]["longitude"],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
        )


if __name__ == "__main__":
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http):
                writer.write_row(rec)
