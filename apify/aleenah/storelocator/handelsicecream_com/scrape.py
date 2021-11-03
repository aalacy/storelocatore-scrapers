from sglogging import SgLogSetup
import json
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


logger = SgLogSetup().get_logger("handelsicecream_com")


def write_output(data):
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for row in data:
            writer.write_row(row)


session = SgRequests()


def fetch_data():

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "cross-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
    }

    res = session.get("https://handelsicecream.com/", headers=headers)

    soup = BeautifulSoup(res.text, "html.parser")
    stores = (
        str(soup.find("body").find("script"))
        .replace("<script>", "")
        .replace("</script>", "")
        .strip()
        .strip(";")
        .replace("var branches = ", "")
        .strip()
    )
    stores = json.loads(stores)

    for store in stores:
        # Store id

        store = stores[store]

        addr = store["address"].split("<br>")
        street = addr[0]
        addr = addr[1].split(",")
        city = addr[0]
        addr = addr[1].strip().split(" ")
        zip = addr[-1]
        del addr[-1]
        state = " ".join(addr)

        type = ""

        tim = (
            "Monday: "
            + store["monday"]
            + ", "
            + "Tuesday: "
            + store["tuesday"]
            + ", "
            + "Wednesday: "
            + store["wednesday"]
            + ", "
            + "Thursday: "
            + store["thursday"]
            + ", "
            + "Friday: "
            + store["friday"]
            + ", "
            + "Saturday: "
            + store["saturday"]
            + ", "
            + "Sunday: "
            + store["sunday"]
        )

        if "status" in store:
            tim = "<MISSING>"
            type = "Coming Soon"

        phone = ""
        res = session.get(store["link"], headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        sa = soup.find_all("a")

        for a in sa:
            if "tel:" in a.get("href"):
                phone = a.text.strip()
                break

        yield SgRecord(
            locator_domain="https://handelsicecream.com/",
            page_url=store["link"],
            location_name=store["title"].strip()
            if store["title"].strip() != ""
            else "<MISSING>",
            street_address=street.strip() if street.strip() != "" else "<MISSING>",
            city=city.strip() if city.strip() != "" else "<MISSING>",
            state=state.strip() if state.strip() != "" else "<MISSING>",
            zip_postal=zip.strip() if zip.strip() != "" else "<MISSING>",
            country_code="US",
            store_number=store["id"] if str(store["id"]).strip() != "" else "<MISSING>",
            phone=phone.strip() if phone.strip() != "" else "<MISSING>",
            location_type=type if type != "" else "<MISSING>",
            latitude=store["lat"] if str(store["lat"]).strip() != "" else "<MISSING>",
            longitude=store["lng"] if str(store["lng"]).strip() != "" else "<MISSING>",
            hours_of_operation=tim,
        )


def scrape():
    write_output(fetch_data())


scrape()
