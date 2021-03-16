from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgFirefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from lxml import html


def _phone(val):
    phone = (
        "".join(val[2:])
        .replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
    )
    return phone.isdigit() and len(phone) > 9


def fetch_data():
    with SgFirefox() as driver:
        locator_domain = "https://www.dicarlospizza.com/"
        base_url = "https://www.dicarlospizza.com/locations"
        driver.get(base_url)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//html/body/div/div[1]/div[1]/div/div[1]/div[2]",
                )
            )
        )
        soup = html.fromstring(driver.page_source)
        blocks = soup.xpath("//html/body/div/div[1]/div[1]/div/div[1]/div[2]//h6")
        states = soup.xpath("//html/body/div/div[1]/div[1]/div/div[1]/div[2]//h3")
        for x, block in enumerate(blocks[:-1]):
            texts = block.xpath(".//text()")
            _ = []
            for text in texts:
                text = text.replace("\ufeff", "")
                if not text.strip():
                    continue
                if text.strip() in ["ORDER PICKUP", "|", "ORDER DELIVERY"]:
                    continue
                _.append(text)
                if _phone(_):
                    yield SgRecord(
                        page_url=base_url,
                        location_name=_[0],
                        street_address=_[1],
                        state=states[x].xpath(".//text()")[0],
                        country_code="US",
                        phone="".join(_[2:]),
                        locator_domain=locator_domain,
                    )
                    _ = []


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
