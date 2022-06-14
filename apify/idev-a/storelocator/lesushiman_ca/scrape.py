from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sgpostal.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://lesushiman.ca",
    "referer": "https://lesushiman.ca/find-us-and-order/",
    "x-requested-with": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://lesushiman.ca"
base_url = "https://lesushiman.ca/find-us-and-order/"
detail_url = "https://lesushiman.ca/wp-admin/admin-ajax.php"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div.map-card"
        )
        for _ in locations:
            location_name = _.select_one("p.card-name").text.strip()
            data = f"action=selected_store&storeId={_['data-id']}&distance="
            page_url = bs(
                session.post(detail_url, headers=header1, data=data).text, "lxml"
            ).select("a")[-1]["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            bb = sp1.select("div.single-rest_case")
            raw_address = bb[0].text.strip()
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            temp = list(sp1.select_one("div.opening-hours").stripped_strings)
            for x in range(0, len(temp), 2):
                hours.append(f"{temp[x]}: {temp[x+1]}")

            location_type = ""
            if "TEMPORARILY CLOSED" in location_name:
                location_type = "TEMPORARILY CLOSED"
            yield SgRecord(
                store_number=_["data-id"],
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["data-lat"],
                longitude=_["data-lng"],
                country_code="CA",
                phone=_.select_one("div.phone").text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                location_type=location_type,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
