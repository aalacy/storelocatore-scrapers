from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()


def fetch_data():
    base_url = "https://snuffers.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }
    r = session.get(base_url + "/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    main = soup.find_all("div", {"class": "location-info"})
    for dt in main:
        loc = list(dt.stripped_strings)
        del loc[0]
        del loc[0]
        del loc[0]
        hour = " ".join(loc)

        r = session.get(
            dt.find("a", {"class": "more-btn"})["href"] + "?req=more-info",
            headers=headers,
        )
        soup = BeautifulSoup(r.text, "lxml")
        vk = soup.find("div", {"class": "location-info"})

        name = vk.find("h3").text.strip()
        address = vk.find("span", {"itemprop": "streetAddress"}).text.strip()
        city = ""

        if vk.find("span", {"itemprop": "addressLocality"}) is not None:
            city = (
                vk.find("span", {"itemprop": "addressLocality"})
                .text.strip()
                .split(",")[0]
                .strip()
            )
        state = ""
        if vk.find("span", {"itemprop": "addressRegion"}) is not None:
            state = vk.find("span", {"itemprop": "addressRegion"}).text.strip()
        zip = ""
        if vk.find("span", {"itemprop": "postalCode"}) is not None:
            zip = vk.find("span", {"itemprop": "postalCode"}).text.strip()
        phone = vk.find("div", {"class": "phone"}).text.strip().replace("P: ", "")

        lat = ""
        lng = ""
        storeno = ""
        country = "US"
        yield SgRecord(
            page_url=dt.find("a", {"class": "more-btn"})["href"] + "?req=more-info",
            store_number=storeno,
            location_name=name,
            street_address=address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country,
            latitude=lat,
            longitude=lng,
            phone=phone,
            locator_domain=base_url,
            hours_of_operation=(hour if hour.strip() else SgRecord.MISSING),
            raw_address=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
        )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
