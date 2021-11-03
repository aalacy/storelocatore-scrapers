from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import re
import json


def fetch_data():
    with SgRequests() as session:
        locator_domain = "https://www.tacotime.com/"
        base_url = "https://www.tacotime.com/locator/index.php?brand=7&mode=desktop&pagesize=5&q="
        r = session.get(base_url)
        soup = bs(r.text, "lxml")
        all_scripts = " ".join(
            [_.contents[0] for _ in soup.select("script") if len(_.contents)]
        )
        scripts = re.findall(
            r'{"StoreId":\d{4},"Latitude":\d+.\d+,"Longitude":\-\d+.\d+', all_scripts
        )
        for script in scripts:
            script += "}"
            script = json.loads(script)
            page_url = urljoin(
                "https://www.tacotime.com",
                f"/stores/{script['StoreId']}",
            )
            r1 = session.get(page_url)
            soup1 = bs(r1.text, "lxml")
            location_name = (
                soup1.select_one("div.info h1")
                .text.replace(f"#{script['StoreId']}", "")
                .strip()
            )
            street_address = (
                soup1.select_one("li.address.icon-address")
                .text.replace(",", "")
                .strip()
            )
            address = [_.text for _ in soup1.select("li.address span")]
            city = address[0].replace(",", "").strip()
            state = address[1].strip()
            zip = address[2].strip()
            phone = ""
            try:
                phone = soup1.select_one("li.phone.icon-phone a").text
            except:
                pass
            latitude = script["Latitude"]
            longitude = script["Longitude"]
            hours_of_operation = "; ".join(
                [_.text for _ in soup1.select("div.hours ul li")]
            )

            yield SgRecord(
                page_url=page_url,
                store_number=script["StoreId"],
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code="US",
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
