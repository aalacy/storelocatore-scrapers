import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "llbean_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://llbean.com/"
MISSING = "<MISSING>"


def fetch_data():
    pattern = re.compile(r"\s\s+")
    url = "https://www.llbean.com/llb/shop/1000001703?pla1=1"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    link_list = soup.find("div", {"id": "storeLocatorZone"}).findAll("a")
    url = "https://global.llbean.com/Retail.html"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    link_list1 = soup.findAll("div", {"class": "row_intl"})[1].findAll("a")
    for link in link_list1:
        link_list.append(link)
    for alink in link_list:

        if "global" in alink["href"] or (
            alink.text.find(":") == -1 or alink.find("Freeport") == -1
        ):

            if "https" in alink["href"]:
                link = alink["href"]
                pass
            else:
                link = "https://www.llbean.com" + alink["href"]
            r = session.get(link, headers=headers, verify=False)

            soup = BeautifulSoup(r.text, "html.parser")
            log.info(link)
            if "Temporarily Closed" in soup.text or "opening" in soup.text.lower():
                continue
            title = soup.find("h1").text
            try:
                phone = soup.find("address").find("strong", {"class", "tel"}).text
            except:
                try:
                    phone = (
                        soup.find("div", {"class", "address"})
                        .select_one("a[href*=tel]")
                        .text.strip()
                    )
                except:
                    phone = soup.select_one("a[href*=tel]").text
            try:
                street = soup.find("span", {"class": "street-address"}).text
                city = soup.find("em", {"class": "locality"}).text
                state = soup.find("abbr", {"class": "region"}).text
                pcode = soup.find("em", {"class": "postal-code"}).text
            except:
                address = soup.find("div", {"class": "font-size-16px"}).text
                address = re.sub(pattern, "\n", str(address)).strip().splitlines()
                street = address[0]
                city, state = address[1].split(", ", 1)
                state, pcode = state.split(" ", 1)
                title = soup.findAll("div", {"class": "font-montserrat"})[
                    0
                ].text.strip()
                lat, longt = (
                    soup.select_one("a[href*=map]")["href"]
                    .split("@", 1)[1]
                    .split("data", 1)[0]
                    .split(",", 1)
                )
                longt = longt.split(",", 1)[0]
            store = link.split("/")[-1]
            if store.isdigit():
                pass
            else:
                store = "<MISSING>"
            try:
                hours = (
                    soup.find("ul", {"class": "hoursActive"})
                    .text.replace("\n", "")
                    .strip()
                )
                hours = re.sub(pattern, " ", hours).strip()
            except:
                try:

                    if "Temporarily Closed" in soup.text or "OPENING" in soup.text:
                        continue
                    hours = soup.text.split("store hours", 1)[1].split(
                        "In this store", 1
                    )[0]
                    hours = re.sub(pattern, " ", hours).replace("\n", " ").strip()
                except:
                    hours = MISSING
            if len(hours) < 3:
                hours = MISSING
            if "Temporarily Closed" in hours or "OPENING" in hours:
                continue
            ccode = "US"
            if "global" in link:
                ccode = "CA"
            try:
                lat = (
                    r.text.split("var latitude", 1)[1].split("=", 1)[1].split(";", 1)[0]
                )

                longt = (
                    r.text.split("var longitude", 1)[1]
                    .split("=", 1)[1]
                    .split(";", 1)[0]
                )
            except:
                if ccode == "CA":
                    pass
                else:
                    lat = longt = MISSING
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=link,
                location_name=title,
                street_address=street,
                city=city,
                state=state,
                zip_postal=pcode,
                country_code=ccode,
                store_number=store,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=lat,
                longitude=longt,
                hours_of_operation=hours.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
