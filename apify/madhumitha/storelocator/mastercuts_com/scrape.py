from bs4 import BeautifulSoup

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

domain = "mastercuts.com"

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
hdr = {"User-Agent": user_agent}
session = SgRequests()


def fetch_data():
    storelist = []
    url = "https://www.signaturestyle.com/salon-directory.html"
    response = session.get(url, headers=hdr)
    soup = BeautifulSoup(response.content, "html.parser")
    loclist = soup.select("a[href*=locations]")
    for loc_url in loclist:
        loc_url = "https://www.signaturestyle.com" + loc_url["href"]

        if "pr.html" in loc_url:
            continue
        res = session.get(loc_url, headers=hdr)
        soup = BeautifulSoup(res.text, "html.parser")
        linklist = soup.select("a[href*=haircuts]")
        for link in linklist:
            link = "https://www.signaturestyle.com" + link["href"]
            r = session.get(link, headers=hdr)
            if r.status_code != 200:
                continue
            loc_data = BeautifulSoup(r.text, "html.parser")
            loc_soup = loc_data.find(class_="salondetailspagelocationcomp")
            try:
                location_name = loc_data.find("h2").text.strip()
                country = "US"

                hours_of_operation = " ".join(
                    list(loc_soup.find(class_="salon-timings").stripped_strings)
                )
            except Exception:
                continue
            phone = loc_soup.find(id="sdp-phone").text.strip()
            street_address = loc_soup.find(
                "span", attrs={"itemprop": "streetAddress"}
            ).text.strip()
            city = loc_soup.find(
                "span", attrs={"itemprop": "addressLocality"}
            ).text.strip()
            state = loc_soup.find(
                "span", attrs={"itemprop": "addressRegion"}
            ).text.strip()
            zipcode = loc_soup.find(
                "span", attrs={"itemprop": "postalCode"}
            ).text.strip()
            lat = loc_data.find("meta", attrs={"itemprop": "latitude"})["content"]
            lon = loc_data.find("meta", attrs={"itemprop": "longitude"})["content"]
            store_number = link.split("-")[-1].split(".")[0]
            location_type = ""

            if " " in zipcode:
                country = "CA"
            if len(hours_of_operation) < 3:
                hours_of_operation = ""
            if store_number in storelist:
                continue
            storelist.append(store_number)
            item = SgRecord(
                locator_domain=domain,
                page_url=link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipcode,
                country_code=country,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=lat,
                longitude=lon,
                hours_of_operation=hours_of_operation,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
