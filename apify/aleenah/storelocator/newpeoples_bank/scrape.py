import re
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import time
import usaddress


logger = SgLogSetup().get_logger("newpeoples_bank")
session = SgRequests()
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    # Your scraper here
    all = []

    with SgChrome() as driver:
        driver.get("https://newpeoples.bank/Locations.aspx")
        time.sleep(10)
        ls = driver.find_element_by_id(
            "subcontentContainer"
        ).find_elements_by_class_name("subsection")
        del ls[0]
        del ls[0]

        for l in ls:

            addr, phone = re.findall(
                r"Address:(.*)Office:(.*)Mailing Address", l.text, re.DOTALL
            )[0]
            tagged = usaddress.tag(addr.replace("\n", " ").strip())[0]
            try:
                street = (
                    tagged["AddressNumber"]
                    + " "
                    + tagged["StreetNamePreDirectional"]
                    + " "
                    + tagged["StreetName"]
                    + " "
                    + tagged["StreetNamePostType"]
                    + " "
                    + tagged["StreetNamePostDirectional"]
                )
            except:
                try:
                    street = (
                        tagged["AddressNumber"]
                        + " "
                        + tagged["StreetName"]
                        + " "
                        + tagged["StreetNamePostType"]
                        + " "
                        + tagged["StreetNamePostDirectional"]
                    )
                except:
                    try:
                        street = (
                            tagged["AddressNumber"]
                            + " "
                            + tagged["StreetName"]
                            + " "
                            + tagged["StreetNamePostDirectional"]
                        )
                    except:
                        try:
                            street = (
                                tagged["AddressNumber"]
                                + " "
                                + tagged["StreetName"]
                                + " "
                                + tagged["StreetNamePostType"]
                            )
                        except:
                            street = (
                                tagged["AddressNumber"] + " " + tagged["StreetName"]
                            )

            city = tagged["PlaceName"]
            state = tagged["StateName"]
            zip = tagged["ZipCode"]

            trs = l.find_elements_by_tag_name("tbody")[1].find_elements_by_tag_name(
                "tr"
            )
            del trs[-1]
            tim = ""
            for tr in trs:
                tds = tr.find_elements_by_tag_name("td")
                tim += tds[0].text + ": " + tds[2] + " "

            tim = tim.strip()
            phone = phone.strip()
            loc = l.find_element_by_tag_name("h2").text.strip()
            yield SgRecord(
                locator_domain="https://newpeoples.bank",
                page_url="https://newpeoples.bank/Locations.aspx",
                location_name=loc,
                street_address=street,
                city=city,
                state=state,
                zip_postal=zip,
                country_code="US",
                store_number="<MISSING>",
                phone=phone,
                location_type="Branch",
                latitude="<MISSING>",
                longitude="<MISSING>",
                hours_of_operation=tim,
            )

    return all


def scrape():
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


if __name__ == "__main__":
    scrape()
