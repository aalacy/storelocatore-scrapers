import csv
import sgrequests
import bs4


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    locator_domain = "https://ladybirdacademy.com/"
    missingString = "<MISSING>"

    def initSoup(site):
        h = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36"
        }
        s = sgrequests.SgRequests()
        return bs4.BeautifulSoup(s.get(site, headers=h).text, features="lxml")

    def getAllStores():
        r = []

        def getAllLinks():
            url = "http://ladybirdacademy.com/locations"
            s = initSoup(url)
            res = []
            for p in s.findAll("p", {"class": "link_visit"}):
                res.append(p.find("a")["href"])
            return res

        for link in getAllLinks():
            s = initSoup(link)
            name = (
                s.find("title").text.strip().replace("| Ladybird Academy", "").strip()
            )
            gb = s.find("div", {"class": "gray-box"})
            addr = list(
                filter(
                    None,
                    gb.findAll("p")[1].get_text(separator="\n").strip().split("\n"),
                )
            )
            street = addr[0].strip()
            city = addr[1].strip().replace(",", "")
            state = list(filter(None, addr[-1].strip().split(" ")))[0]
            zp = list(filter(None, addr[-1].strip().split(" ")))[1]
            h = gb.findAll("p")[2].text.strip().replace("Hours:", "").strip()
            ph = gb.findAll("p")[3].text.strip().replace("Phone:", "").strip()
            r.append(
                [
                    locator_domain,
                    link,
                    name,
                    street,
                    city,
                    state,
                    zp,
                    missingString,
                    missingString,
                    ph,
                    missingString,
                    missingString,
                    missingString,
                    h,
                ]
            )
        return r

    result = getAllStores()
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
