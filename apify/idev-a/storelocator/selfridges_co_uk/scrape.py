from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome

_headers = {
    "referer": "https://www.selfridges.com/US/en/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}


def fetch_data():
    locator_domain = "https://www.selfridges.com"
    base_url = "https://www.selfridges.com/US/en/features/info/stores/london/"
    with SgChrome() as driver:
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        page_links = soup.select("ul.navigation-root a")
        for link in page_links:
            page_url = locator_domain + link["href"]
            driver.get(page_url)
            soup = bs(driver.page_source, "lxml")
            store_info = soup.select(
                "div.richText.component.section.default-style.col-xs-12.col-sm-6"
            )
            try:
                address_contents = (
                    store_info[1].select_one("div.richText-content p").contents
                )
            except:
                store_info = soup.select(
                    "div.richText.component.section.default-style.col-xs-12.col-sm-3"
                )
                address_contents = (
                    store_info[1].select_one("div.richText-content p").contents
                )
            address = []
            for item in address_contents:
                if item.string is None:
                    continue
                address.append(item.string)
            zip = address.pop()
            city = address.pop()
            geo = soup.select_one(
                ".richText.component.section.col-xs-12.richtext.default-style .richText-content a.cta"
            )["href"]
            latitude = geo.split("=")[1].split(",")[0]
            longitude = geo.split("=")[1].split(",")[1]
            hours_of_operation = ", ".join(
                store_info[0]
                .select_one("div.richText-content")
                .text.replace("\xa0", " ")
                .split("\n")[2:9]
            )

            yield SgRecord(
                page_url=page_url,
                location_name=address[0],
                street_address=", ".join(address[1:]),
                city=city,
                latitude=latitude,
                longitude=longitude,
                zip_postal=zip,
                country_code="UK",
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
