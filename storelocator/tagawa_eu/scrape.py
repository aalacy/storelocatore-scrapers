from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
from sgselenium import SgChrome
import dirtyjson as json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.tagawa.eu"
base_url = "https://www.tagawa.eu/stores/"
map_url = "https://www.google.com/maps/d/embed?mid=1H8hQRNujZ8zFDyAKlFrlsT9mBo7Z0uQ1"


def _latlng(locs, name):
    for loc in locs:
        if name.lower() in loc[5][0][1][0].lower():
            return loc[1][0][0]


def fetch_data():
    locs = []
    with SgChrome(
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        is_headless=True,
    ) as driver:
        driver.get(map_url)
        cleaned = (
            driver.page_source.replace("\\\\u003d", "=")
            .replace("\\\\u0026", "&")
            .replace('\\"', '"')
            .replace("\xa0", " ")
        )
        locs = json.loads(
            cleaned.split('var _pageData = "')[1].split('";</script>')[0]
        )[1][6][0][12][0][13][0]

    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select(
            'main > div[data-content-region="page_builder_content"] > div > div'
        )
        for _ in locations:
            if not _.text.strip():
                continue
            block = list(_.stripped_strings)
            _addr = block[1:3]
            if "Find" in _addr[-1]:
                del _addr[-1]
            hours = []
            phone = ""
            for x, bb in enumerate(block):
                if "tel" in bb.lower():
                    phone = block[x + 1]
                if "Opening Hours" in bb:
                    hours = block[x + 1 :]

            raw_address = " ".join(_addr)
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            location_name = " ".join(_.strong.text.strip().split()[1:])
            try:
                lat, lng = _latlng(locs, location_name.split()[0].replace("-", " "))
            except:
                lat, lng = 0, 0
            country_code = addr.country
            city = addr.city
            if country_code == "Woluwé-Saint-Pierre":
                country_code = ""
                city = "Woluwé-Saint-Pierre"
            yield SgRecord(
                page_url=base_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=country_code,
                phone=phone,
                latitude=lat,
                longitude=lng,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
