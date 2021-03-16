from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgFirefox
from sgscrape.sgpostal import parse_address_intl
import json
from bs4 import BeautifulSoup as bs
import time
import re


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def _desc(_):
    desc = (
        _["description"]
        .replace("\u003c", "<")
        .replace("\u003e", ">")
        .replace("\u0026", "&")
        .replace("&nbsp;", "")
        .replace("Drive Thru", "")
    )
    return [dd.text for dd in bs(desc, "lxml").select("p") if dd.text.strip()]


def fetch_data():
    locator_domain = "https://www.faststopmarkets.com/"
    base_url = "https://www.faststopmarkets.com/locations"
    with SgFirefox(executable_path=r"/mnt/g/work/mia/geckodriver.exe") as driver:
        driver.get(base_url)
        exist = False
        while not exist:
            time.sleep(1)
            for rr in driver.requests:
                if (
                    rr.url.startswith("https://www.powr.io/wix/map/public")
                    and rr.response
                ):
                    exist = True
                    locations = json.loads(rr.response.body.decode("utf-8"))["content"][
                        "locations"
                    ]
                    for _ in locations:
                        if not _["address"]:
                            continue
                        addr = parse_address_intl(_["address"])
                        block = _desc(_)
                        hours_of_operation = "; ".join(block[3:])
                        if re.search(r"coming soon", hours_of_operation, re.IGNORECASE):
                            continue
                        location_name = bs(_["name"], "lxml").text
                        store_number = location_name.split("#")[-1]
                        yield SgRecord(
                            store_number=store_number,
                            page_url=driver.current_url,
                            location_name=location_name,
                            street_address=block[0],
                            city=addr.city,
                            state=addr.state,
                            zip_postal=addr.postcode,
                            country_code=addr.country,
                            phone=block[2],
                            latitude=_["lat"],
                            longitude=_["lng"],
                            locator_domain=locator_domain,
                            hours_of_operation=_valid(hours_of_operation),
                        )

                    break


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
