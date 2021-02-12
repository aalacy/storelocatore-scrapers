from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs

locator_domain = "https://www.bmstores.co.uk"


def fetch_data():
    with SgRequests() as session:
        base_url = "https://www.bmstores.co.uk"
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "cookie": "cftoken=0; CURRENTFARCRYPROJECT=bmstorescouk; FARCRYDEVICETYPE=desktop; _ALGOLIA=anonymous-2beb611b-d307-4db0-910b-81e1448ec1b6; _ga=GA1.3.624511035.1611222053; _gid=GA1.3.197517442.1611222053; _gat_UA-23199122-1=1; INGRESSCOOKIE=46a06f577086c2c7f08d6e67b0feb709; OptanonConsent=isIABGlobal=false&datestamp=Thu+Jan+21+2021+13%3A42%3A03+GMT-0500+(Eastern+Standard+Time)&version=5.8.0&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1%2C0_17%3A1%2C0_27%3A1%2C0_26%3A1%2C0_25%3A1%2C0_24%3A1%2C0_23%3A1%2C0_22%3A1%2C0_21%3A1%2C0_20%3A1%2C0_19%3A1%2C0_18%3A1&AwaitingReconsent=false; SESSIONSCOPETESTED=true; HASSESSIONSCOPE=true; cfid=d37d7d0f-023c-44ce-a3af-c253a9b3caae",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        res = session.get(
            "https://www.bmstores.co.uk/hpcstores/StoresGeoJson&start=1&maxrows=700",
            headers=headers,
            verify=False,
        )
        store_list = json.loads(res.text)["features"]
        for store in store_list:
            page_url = base_url + store["properties"]["link"]
            res = session.get(page_url, verify=False)
            soup = bs(res.text, "lxml")
            location_name = store["properties"]["title"]
            try:
                contents = soup.select_one("table.detailssingle td").contents
                table_data = []
                for x in contents:
                    if x.string is not None and x.string != "\n":
                        table_data.append(x.string)
                table_data = table_data[:-1]
                street_address = table_data[0]
                city = store["properties"]["cityCounty"] or "<MISSING>"
                state = "<MISSING>"
                zip = store["properties"]["postcode"]
                phone = (
                    "<MISSING>"
                    if len(table_data) < 3
                    else table_data[2].replace("Phone", "").replace(":", "").strip()
                )
                hours = table_data[3:]
            except:
                street_address = soup.select_one("span[itemprop='streetAddress']").text
                city = (
                    soup.select_one("span[itemprop='addressLocality']").string
                    or "<MISSING>"
                )
                state = (
                    soup.select_one("span[itemprop='addressRegion']").string
                    or "<MISSING>"
                )
                zip = soup.select_one("span[itemprop='postalCode']").string
                phone = soup.select_one("span[itemprop='telephone']")
                phone = "Get" if phone is None else phone.string
                hours = soup.select("li.bm-store-hours")
            street_address = street_address.replace("\n", " ").strip()
            phone = "<MISSING>" if "Get" in phone else phone
            country_code = "GB"
            location_type = store["type"]
            latitude = store["geometry"]["coordinates"][0]
            longitude = store["geometry"]["coordinates"][1]
            hours_of_operation = ""
            for x in hours:
                if x.string is None:
                    hours_of_operation += (
                        "" if x.text is None else x.text.replace("\n", "") + " "
                    )
                else:
                    hours_of_operation += x.replace("\xa0", "").replace("\n", "") + " "
            hours_of_operation = hours_of_operation.replace("Store Hours:", "").strip()
            record = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
            yield record


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
