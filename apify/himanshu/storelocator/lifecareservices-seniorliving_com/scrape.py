from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()

gd_soup = BeautifulSoup(
    session.get("https://www.lifecareservices-seniorliving.com/find-a-community/").text,
    "lxml",
)

gd_nonce = str(gd_soup).split("nonce: '")[1].split("'")[0]


def fetch_data(sgw: SgWriter):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""

    url = "https://www.lifecareservices-seniorliving.com/wp/wp-admin/admin-ajax.php"

    data1 = {"pg": "1", "action": "get_communities", "gd_nonce": str(gd_nonce)}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    }
    response = session.post(url, headers=headers, data=data1).json()
    for ut in response["results"]:
        soup1 = BeautifulSoup(ut["html"], "lxml")
        for data in soup1.find_all("div", {"class": "cmnty-results-address"}):
            full = list(data.find("p", {"class": "address"}).stripped_strings)
            if full[0] == "Information Center":
                del full[0]
            city = list(data.find("p", {"class": "address"}).stripped_strings)[
                -1
            ].split(",")[0]
            state = (
                list(data.find("p", {"class": "address"}).stripped_strings)[-1]
                .split(",")[-1]
                .strip()
                .split(" ")[0]
            )
            zipp = (
                list(data.find("p", {"class": "address"}).stripped_strings)[-1]
                .split(",")[-1]
                .strip()
                .split(" ")[-1]
                .replace("IL", "")
            )
            street_address = " ".join(full[:-1])
            location_name = data.find(
                "h5", {"class": "cmnty-results-item-heading"}
            ).text.strip()
            if ", The" in location_name:
                location_name1 = location_name.split(",")[0]
                location_name = "The " + str(location_name1)
            phone = (
                list(data.stripped_strings)[-2]
                .replace("Chicago,       IL", "<MISSING>")
                .replace("Austin,       TX       78731", "<MISSING>")
                .replace("West Lafayette,       IN       47906-1431", "<MISSING>")
                .replace("Wheaton,       IL       60187", "<MISSING>")
                .replace("Bridgewater,       NJ       08807", "<MISSING>")
                .replace("Atchison,       KS       66002", "<MISSING>")
                .replace("Phoenix,       AZ       85018", "(480) 573-3700")
            )

            try:
                page_url = data.find(
                    "h5", {"class": "cmnty-results-item-heading"}
                ).find("a")["href"]
            except:
                page_url = "<MISSING>"
            latitude = ut["latitude"]
            longitude = ut["longitude"]
            store_number = ut["id"]
            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"
            if "Under Construction" in street_address:
                continue
            else:
                sgw.write_row(
                    SgRecord(
                        locator_domain="https://www.lifecareservices-seniorliving.com",
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zipp,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                    )
                )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
