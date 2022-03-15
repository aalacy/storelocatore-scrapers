from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kfcturkiye")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

header1 = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://kfcturkiye.com",
    "referer": "https://kfcturkiye.com/restoranlar",
    "x-requested-with": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

base_url = "https://kfcturkiye.com/restoranlar"
district_url = "https://kfcturkiye.com/front/front/get_districts"
street_url = "https://kfcturkiye.com/front/front/get_streets"
locator_domain = "https://kfcturkiye.com/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        cities = soup.select("div#city_select_restaurants option")
        for city1 in cities:
            if not city1.get("value"):
                continue
            data = {"country_id": city1["value"]}
            districts = bs(
                session.post(district_url, headers=header1, data=data).json()[
                    "selectbox"
                ],
                "lxml",
            ).select("option")
            for district in districts:
                if not district.get("value"):
                    continue
                d_data = {"district_id": district["value"]}
                links = bs(
                    session.post(street_url, headers=header1, data=d_data).json()[
                        "restaurant_item"
                    ],
                    "lxml",
                ).select("div.restaurants-item")
                logger.info(
                    f"[{city1['value']}] [{district['value']}] {len(links)} found"
                )
                for link in links:
                    page_url = urljoin(locator_domain, link.a["href"])
                    logger.info(page_url)
                    res = session.get(page_url, headers=_headers)
                    if len(res.url.__str__().split("/")) < 5:
                        continue
                    sp1 = bs(res.text, "lxml")
                    raw_address = (
                        sp1.select_one("div.restaurant-detail-area p")
                        .text.replace("/", ",")
                        .strip()
                    )
                    addr = raw_address.split(",")
                    hours = [
                        hh.text.strip()
                        for hh in sp1.select("div.working-hours-info div.hours-item")
                    ]
                    city = addr[-2]
                    street_address = ", ".join(addr[:-2])
                    state = addr[-1]
                    if city == "1 Kadıköy":
                        city = "Kadıköy"
                        street_address += " 1"
                    elif city == "1B Nilüfer":
                        city = "Nilüfer"
                        street_address += " 1B"
                    elif "No:16A Kağıthane" in city:
                        street_address += " " + city.replace("Kağıthane", "")
                        city = "Kağıthane"

                    if (
                        "Şehit Metin Kaya Sokak No:11 Mağaza No:237 Eyüp Istanbul"
                        in raw_address
                        and not street_address
                    ):
                        city = "Eyüp"
                        state = "Istanbul"
                        street_address = "Vialand Alışveriş Merkezi, Yeşilpınar Mahallesi Şehit Metin Kaya Sokak No:11 Mağaza No:237"

                    if not street_address:
                        _cc = city.split()
                        city = _cc[-1]
                        street_address = " ".join(_cc[:-1])

                    yield SgRecord(
                        page_url=page_url,
                        location_name=sp1.select_one(
                            "div.restaurant-detail-area h3"
                        ).text.strip(),
                        street_address=street_address,
                        city=city,
                        state=state,
                        country_code="Turkey",
                        locator_domain=locator_domain,
                        hours_of_operation="; ".join(hours).replace("–", "-"),
                        raw_address=raw_address,
                    )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
