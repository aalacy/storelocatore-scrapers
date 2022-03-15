from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    pattern = re.compile(r"\s\s+")
    url = "https://www.llbean.com/llb/shop/1000001703?nav=gn-"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    link_list = soup.find("div", {"class": "wcm-grid-container"}).findAll("a")

    url = "https://global.llbean.com/Retail.html"
    r = session.get(url, headers=headers)
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
            title = alink.text
            r = session.get(link, headers=headers)

            soup = BeautifulSoup(r.text, "html.parser")
            if "Temporarily Closed" in soup.text or "opening" in soup.text.lower():
                continue
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
                street = soup.find("div", {"itemprop": "streetAddress"}).text
                city = (
                    soup.find("span", {"itemprop": "addressLocality"})
                    .text.replace(",", "")
                    .strip()
                )
                state = soup.find("span", {"itemprop": "addressRegion"}).text
                pcode = soup.find("span", {"itemprop": "postalCode"}).text
            except:
                try:
                    phone = soup.find("a", {"class": "font-size-16px"}).text.strip()
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
                except:
                    continue
            try:
                store = link.split("shop/", 1)[1].split("?", 1)[0]
                if store.isdigit():
                    pass
                else:
                    store = "<MISSING>"
            except:
                store = "<MISSING>"
            try:
                hours = (
                    soup.find("div", {"class": "StorePage_store-hours"})
                    .text.replace("\n", "")
                    .strip()
                )
                hours = re.sub(pattern, " ", hours).strip()
            except:

                if "Temporarily Closed" in soup.text or "OPENING" in soup.text:
                    continue
                hours = soup.text.split("store hours", 1)[1].split("In this store", 1)[
                    0
                ]
                hours = re.sub(pattern, " ", hours).replace("\n", " ").strip()
            if len(hours) < 3:
                hours = "<MISSING>"
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
                    lat = longt = "<MISSING>"
            yield SgRecord(
                locator_domain="https://www.llbean.com",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=str(store),
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours.replace("p.m.", "p.m. ")
                .replace("Store Hours:", "")
                .replace("NOW OPEN ", "")
                .strip(),
            )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
