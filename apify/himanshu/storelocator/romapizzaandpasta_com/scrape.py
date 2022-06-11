from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sglogging import sglog

session = SgRequests(retry_behavior=None, proxy_rotation_failure_threshold=0)
log = sglog.SgLogSetup().get_logger(logger_name="romapizzaandpasta.com")


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://romapizzaandpasta.com/locations/"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    k1 = soup.find("div", {"class": "x-column x-sm vc x-1-1"}).find_all("p")[1:]
    for i in k1:
        location_name = i.find("strong").text.strip()
        page_url = i.find_all("a")[-1]["href"]
        log.info(page_url)
        span = i.find_all("span")
        hours1 = ""
        for s in span:
            hours1 = " ".join(list(s.stripped_strings))
        city = ""
        state = ""
        zipcode = ""
        phone = ""
        hours = ""
        if "https:" in page_url:
            if "opendining.net" in page_url:
                if (
                    page_url
                    != "https://www.opendining.net/menu/5bec37d9515ee9202e15a752"
                ):
                    r = session.get(page_url, headers=headers)
                    soup2 = BeautifulSoup(r.text, "lxml")
                    v2 = list(
                        soup2.find("div", {"class": "restaurant-info"}).stripped_strings
                    )
                    location_name = v2[0]
                    addr = v2[1].split(",")
                    street_address = addr[0]
                    city = addr[1].replace("\n\t\t\t\t\t\t\t", "")
                    state = addr[2].strip().split(" ")[0]
                    zipcode = addr[2].strip().split(" ")[1]
                    phone = v2[2].strip()
                else:
                    page_url = "<MISSING>"
                    location_name = "Clarksville"
                    street_address = "3441 Fort Campbell Blvd."
                    city = "Clarksville"
                    zipcode = "<MISSING>"
                    phone = "931-546-5005"
                    hours = "mon-sun 10am-midnight, buffet 10:30am-2pm"

            else:

                r = session.get(page_url, headers=headers)
                soup1 = BeautifulSoup(r.text, "lxml")
                k = soup1.find_all("div", {"class": "col-lg-3"})
                for i in k:
                    hours = ""
                    p = i.find("div", {"class": "card-body"})

                    zipcode = list(p.stripped_strings)[2].split(",")[1].split()[1]
                    state = list(p.stripped_strings)[2].split(",")[1].split()[0]
                    city = list(p.stripped_strings)[2].split(",")[0]
                    street_address = list(p.stripped_strings)[1]
                    time = p.find_all("div", {"class": "mt-2"})
                    phone = list(time[-1].stripped_strings)[-1]

                    if len(list(time[-2].stripped_strings)) == 2:
                        hours = list(time[-2].stripped_strings)[-1]
                    else:
                        hours = hours1

            yield SgRecord(
                locator_domain="romapizzaandpasta.com",
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zipcode,
                country_code="US",
                store_number="<MISSING>",
                phone=phone,
                location_type="romapizzaandpasta",
                latitude="<MISSING>",
                longitude="<MISSING>",
                hours_of_operation=hours,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
