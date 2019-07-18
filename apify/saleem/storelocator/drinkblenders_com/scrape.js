const Apify = require('apify')
const request = require('request-promise');
const cheerio = require('cheerio');

Apify.main(async () => {
  const data = await scrape();
  await Apify.pushData(data);
});

async function scrape() {

  // Begin scraper
  const rootAddress = 'https://www.drinkblenders.com/blendersland/';
  const records = [];
  await request({
    url: rootAddress,
    headers: {
      'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15"
    }
  })
    .then(async function (html) {
      console.log(html);
      let $ = cheerio.load(html);

      // location hours is the same across locations and given in the footer of the page
      let hoursHeader = $('h3:contains(Store Hours)');
      if (hoursHeader.length !== 1) {
        throw 'Either the page is down, the crawler is being blocked, or modification of the page structure has made the crawler obsolete.'
      }
      const [hours_of_operation] = hoursHeader.next().text().match(/[A-Za-z][\S\s]*PM/);

      // most symantic approach to grabbing individual locations
      // is by names, h4. However, there is one empty h4 that must
      // be handled, apparently they removed it, or something...
      const locationNameList = $('h4').toArray();
      for (const element of locationNameList) {
        locationNameElement = $(element);
        // catch empty spot
        if (locationNameElement.is(':empty')) {
          continue
        }

        location_name = locationNameElement.text();

        // get address. Address is the next sibling to each name element
        const rawAddress = locationNameElement.next().text();
        const {groups: addressParts} = rawAddress.match(/^\s*(\((?<city>.+)\)\n)?(?<street_address>.+)\n.*?(?<phone>[-\d]*)$/);

        records.push({
          locator_domain: 'drinkblenders.com',
          location_name: location_name,
          // Including raw address because it contains some additional info not found in the other fields
          raw_address: rawAddress,
          street_address: addressParts.street_address,
          // some of the locations are just called by their city, others that have a particular name
          // the city is given in parentheses before the address
          city: addressParts.city || location_name,
          // state is not given with each location, but it is the same across all
          state: 'CA',
          zip: '<MISSING>',
          country_code: 'US',
          store_number: '<MISSING>',
          phone: addressParts.phone,
          location_type: '<MISSING>',
          latitude: '<MISSING>',
          longitude: '<MISSING>',
          hours_of_operation: hours_of_operation,
        });
      };
    });

  return records;
	// End scraper

}
