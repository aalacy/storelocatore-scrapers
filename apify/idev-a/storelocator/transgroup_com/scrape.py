from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("transgroup")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "http://www.transgroup.com"
base_url = "http://www.transgroup.com/locations.aspx"
url = "https://siws.transgroup.com/StationInfo.asmx/GetStationInfoJSonIncludeSpecServices?callback=jQuery183023879191175909176_1625502747472&cityCode=%22{}%22&_=1625502788447"
streets = []


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.column.right-channel ul li a")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = locator_domain + link["href"]
            logger.info(f"{page_url}")
            locations = json.loads(
                json.loads(
                    session.get(
                        url.format(link["href"].split("=")[1]), headers=_headers
                    ).text.split("jQuery183023879191175909176_1625502747472(")[1][:-1]
                )["d"]
            )
            for _ in locations["AddressList"]:
                street_address = _["Address1"]
                if _["Address2"]:
                    street_address += "" + _["Address2"]

                if street_address.endswith(","):
                    street_address = street_address[:-1]
                if street_address in streets:
                    continue
                streets.append(street_address)
                phone = ""
                for pp in _["PhoneList"]:
                    if pp["PhoneType"] == "Local":
                        phone = (
                            pp["PhoneNum"]
                            .replace("(24 Hours)", "")
                            .replace("(Rep)", "")
                        )
                        break

                yield SgRecord(
                    page_url=page_url,
                    location_name=locations["CityName"],
                    street_address=street_address,
                    city=_.get("City"),
                    state=_.get("State"),
                    zip_postal=_.get("Zip"),
                    country_code=locations["CountryName"],
                    phone=phone,
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
