import csv

from bs4 import BeautifulSoup

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    url = "https://www.sanfordhealth.org/coveo/rest/search/v2?sitecoreItemUri=sitecore%3A%2F%2Fweb%2F%7BAA2CFD83-3371-4D1E-913E-A23FF93C9E56%7D%3Flang%3Den%26amp%3Bver%3D1&siteName=ORG?actionsHistory=%5B%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222021-05-07T03%3A20%3A29.331Z%5C%22%22%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%22https%3A%2F%2Fwww.sanfordhealth.org%2Flocations%23radius%3D1000%22%2C%22time%22%3A%22%5C%222021-05-07T03%3A20%3A26.768Z%5C%22%22%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222021-05-07T03%3A14%3A22.646Z%5C%22%22%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%22https%3A%2F%2Fwww.sanfordhealth.org%2Flocations%23radius%3D1000%22%2C%22time%22%3A%22%5C%222021-05-07T03%3A14%3A20.480Z%5C%22%22%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%22https%3A%2F%2Fwww.sanfordhealth.org%2Flocations%2Fsanford-69th-and-minnesota-family-medicine%22%2C%22time%22%3A%22%5C%222021-05-05T22%3A46%3A58.425Z%5C%22%22%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%22https%3A%2F%2Fwww.sanfordhealth.org%2Flocations%2Fsanford-neurosurgery-and-spine-clinic%22%2C%22time%22%3A%22%5C%222021-04-23T00%3A27%3A40.284Z%5C%22%22%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%22https%3A%2F%2Fwww.sanfordhealth.org%2Flocations%2Fsanford-bemidji-walker-clinic%22%2C%22time%22%3A%22%5C%222021-04-23T00%3A25%3A00.841Z%5C%22%22%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%22https%3A%2F%2Fwww.sanfordhealth.org%2Flocations%2Fsanford-26th-and-sycamore-acute-care-and-orthopedic-fast-track-clinic%22%2C%22time%22%3A%22%5C%222021-04-23T00%3A24%3A43.516Z%5C%22%22%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%22https%3A%2F%2Fwww.sanfordhealth.org%2Flocations%2Fsanford-limb-preservation-center%22%2C%22time%22%3A%22%5C%222021-04-23T00%3A17%3A45.406Z%5C%22%22%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%22https%3A%2F%2Fwww.sanfordhealth.org%2Flocations%2Fdiabetes-education-center%22%2C%22time%22%3A%22%5C%222021-04-23T00%3A13%3A12.801Z%5C%22%22%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%22https%3A%2F%2Fwww.sanfordhealth.org%2Flocations%2Fdiabetes-education-center%22%2C%22time%22%3A%22%5C%222021-04-23T00%3A09%3A49.031Z%5C%22%22%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%22https%3A%2F%2Fwww.sanfordhealth.org%2Flocations%2Fcenterville-community-pharmacy%22%2C%22time%22%3A%22%5C%222021-04-23T00%3A09%3A45.545Z%5C%22%22%7D%2C%7B%22name%22%3A%22Query%22%2C%22time%22%3A%22%5C%222021-04-23T00%3A09%3A26.799Z%5C%22%22%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%22https%3A%2F%2Fwww.sanfordhealth.org%2Flocations%22%2C%22time%22%3A%22%5C%222021-04-23T00%3A09%3A21.594Z%5C%22%22%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%22https%3A%2F%2Fwww.sanfordhealth.org%2F%22%2C%22time%22%3A%22%5C%222021-04-23T00%3A08%3A34.783Z%5C%22%22%7D%2C%7B%22name%22%3A%22PageView%22%2C%22value%22%3A%22https%3A%2F%2Fwww.sanfordhealth.org%2F%22%2C%22time%22%3A%22%5C%222021-04-22T23%3A57%3A53.794Z%5C%22%22%7D%5D&referrer=&visitorId=becbde39-c66d-457e-afe4-7415ed6ec678&isGuestUser=false&aq=(((%40fz95xpath46747%3DAA2CFD8333714D1E913EA23FF93C9E56%20%40fz95xid46747%3C%3EAA2CFD8333714D1E913EA23FF93C9E56)%20(%40fhaslayout46747%3D%3D1%20%40fz95xtemplate46747%3D%3DF8CF55EA84BB4E58B7B08A39596DCCD6))%20NOT%20%40fz95xtemplate46747%3D%3D(ADB6CA4F03EF4F47B9AC9CE2BA53FF97%2CFE5DD82648C6436DB87A7C4210C7413B))&cq=(%40fz95xlanguage46747%3D%3Den)%20(%40fz95xlatestversion46747%3D%3D1)%20(%40source%3D%3D%22ORG_coveo_web_index%20-%20sanford-coveo-prod%22)&searchHub=ORG%20locations&locale=en&maximumAge=900000&firstResult=0&numberOfResults=1000&excerptLength=200&enableDidYouMean=false&sortCriteria=%40ftitle46747%20ascending&queryFunctions=%5B%5D&rankingFunctions=%5B%5D&groupBy=%5B%7B%22field%22%3A%22%40ffacilitytype46747%22%2C%22maximumNumberOfValues%22%3A6%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22allowedValues%22%3A%5B%5D%7D%2C%7B%22field%22%3A%22%40flocationservice46747%22%2C%22maximumNumberOfValues%22%3A6%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22allowedValues%22%3A%5B%5D%7D%2C%7B%22field%22%3A%22%40flocationstate46747%22%2C%22maximumNumberOfValues%22%3A6%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22allowedValues%22%3A%5B%5D%7D%2C%7B%22field%22%3A%22%40fcity46747%22%2C%22maximumNumberOfValues%22%3A6%2C%22sortCriteria%22%3A%22occurrences%22%2C%22injectionDepth%22%3A1000%2C%22completeFacetWithStandardValues%22%3Atrue%2C%22allowedValues%22%3A%5B%5D%7D%5D&facetOptions=%7B%7D&categoryFacets=%5B%5D&retrieveFirstSentences=true&timezone=America%2FPort_of_Spain&enableQuerySyntax=false&enableDuplicateFiltering=false&enableCollaborativeRating=false&debug=false&allowQueriesWithoutKeywords=true"

    jason_data = session.get(url, headers=headers).json()
    for anchor in jason_data["results"]:

        if "Title" in anchor:
            location_name = anchor["Title"]
        else:
            location_name = "<MISSING>"

        try:
            street_address = (
                anchor["raw"]["faddress46747"] + " " + anchor["raw"]["faddress246747"]
            )
        except:
            try:
                street_address = anchor["raw"]["faddress46747"]
            except:
                continue

        street_address = (
            street_address.replace("Van Demark Building", "")
            .replace(". , Suite", ". Suite")
            .strip()
        )
        page_url = (
            "https://www.sanfordhealth.org/locations/" + anchor["raw"]["fz95xname46747"]
        )
        city = anchor["raw"]["fcity46747"][0]
        if "flocationstate46747" in anchor["raw"]:
            state = anchor["raw"]["flocationstate46747"]
        else:
            state = "<MISSING>"
        if state == "Greater Accra" or state == "Central":
            continue

        try:
            req = session.get(page_url, headers=headers)
            base = BeautifulSoup(req.text, "lxml")
            script = base.find(
                "script", attrs={"type": "application/ld+json"}
            ).contents[0]
            zipp = (
                script.split('postalCode":')[1].split(",")[0].replace('"', "").strip()
            )
        except:
            zipp = "<INACCESSIBLE>"

        if "fphone46747" in anchor["raw"]:
            phone = anchor["raw"]["fphone46747"]
        else:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        if "flatitude46747" in anchor["raw"]:
            latitude = anchor["raw"]["flatitude46747"]
            longitude = anchor["raw"]["flongitude46747"]
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        if "fprimaryhours46747" in anchor["raw"]:
            hours = anchor["raw"]["fprimaryhours46747"]

        hours_of_operation = hours

        store = []
        store.append("https://www.sanfordhealth.org/")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(
            hours_of_operation.strip().replace("\n", " ")
            if hours_of_operation
            else "<MISSING>"
        )
        store.append(page_url)
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
