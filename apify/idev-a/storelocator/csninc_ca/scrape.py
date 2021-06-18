from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
import re
import math
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("csncollision")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
session = SgRequests().requests_retry_session()
max_workers = 1
locator_domain = "https://csncollision.com/"
base_url = "https://csncollision.com/all-locations/"


def fetchConcurrentSingle(data):
    response = request_with_retries(data)
    return data, response.text


def fetchConcurrentList(_list, occurrence=max_workers):
    output = []
    total = len(_list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchConcurrentSingle, _list):
            count = count + 1
            if count % reminder == 0:
                logger.debug(f"Concurrent Operation count = {count}")
            output.append(result)
    return output


def request_with_retries(url):
    return session.get(url, headers=_headers)


def fetch_data():
    soup = bs(request_with_retries(base_url).text, "lxml")
    links = [
        link.a["href"] for link in soup.select("div.container div.col-6.col-lg-4.my-4")
    ]
    logger.info(f"{len(links)} found")
    for page_url, res in fetchConcurrentList(links):
        sp1 = bs(res, "lxml")
        script = json.loads(
            res.split("var csn_location =")[1].split("</script>")[0].strip()[:-1]
        )
        addr = script["address"].split(",")
        temp = (
            sp1.select("div.holder p")[1]
            .text.replace("Shop Hours:", "")
            .replace("(winter only)", "")
            .replace("Shop Hours", "")
            .replace("|", ":")
            .replace("–", "-")
            .split("or")[0]
            .strip()
            .replace("\n", ";")
        )
        hours = []
        for hh in temp.split(";"):
            if "appointment" in hh.lower():
                continue
            hours.append(hh)
        phone = ""
        if sp1.find("a", href=re.compile(r"tel:")):
            phone = sp1.find("a", href=re.compile(r"tel:")).text
        yield SgRecord(
            page_url=page_url,
            location_name=script["name"].replace("’", "'"),
            street_address=" ".join(addr[:-3]).strip(),
            city=addr[-3].strip(),
            state=addr[-2].strip(),
            zip_postal=addr[-1].strip(),
            country_code="CA",
            phone=phone,
            locator_domain=locator_domain,
            latitude=script["latitude"],
            longitude=script["longitude"],
            hours_of_operation="; ".join(hours),
        )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
