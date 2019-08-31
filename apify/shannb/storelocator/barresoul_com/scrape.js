const Apify = require('apify');

const parseAddress = rawAddress => {
  const pattern = /(?<street_address>.+)\s\|\s(?<city>.+),\s(?<state>.+)\s(?<zip>\d{5})\sPhone:.+?(?<phone>[\d-]+)/;
  const match = rawAddress.match(pattern);
  if (match) {
    return match.groups;
  }
  return null;
};

(async () => {
  const requestList = new Apify.RequestList({
    sources: [{ url: 'https://www.10gym.com/contacts/' }],
  });

  await requestList.initialize();

  const handlePage = async ({ $ }) => {
    const locations = [];

    const hours = $('h3:contains("Club Hours")')
      .parent('div')
      .text()
      .replace('Club Hours', '')
      .replace(/(\r|\n)+/g, ' ');

    $('h3').each((index, el) => {
      const loc = {
        locator_domain: '10gym.com',
        location_name: null,
        street_address: null,
        city: null,
        state: null,
        zip: null,
        country_code: '<MISSING>',
        store_number: '<MISSING>',
        phone: null,
        location_type: '<MISSING>',
        latitude: '<MISSING>',
        longitude: '<MISSING>',
        hours_of_operation: hours,
      };

      const $thisH3 = $(el);

      const locationNameEl = $thisH3.find('strong');
      if (locationNameEl.length) {
        const locName = $(locationNameEl)
          .text()
          .trim();
        if (locName.length) {
          loc.location_name = locName;
          const $nextH3 = $thisH3.next('h3');
          if ($nextH3.length) {
            const addressEl = $nextH3.find('a');
            if (addressEl.length) {
              const rawAddress = addressEl.text().trim();
              const address = parseAddress(rawAddress);
              if (address) {
                Object.assign(loc, address);
              } else {
                loc.raw_address = rawAddress;
                loc.street_address = '<INACCESSIBLE>';
                loc.city = '<INACCESSIBLE>';
                loc.state = '<INACCESSIBLE>';
                loc.zip = '<INACCESSIBLE>';
                loc.phone = '<INACCESSIBLE>';
              }
            }
          }
          locations.push(loc);
        }
      }
    });

    await Apify.pushData(locations);
  };

  const crawler = new Apify.CheerioCrawler({
    requestList,
    handlePageFunction: handlePage,
  });

  await crawler.run();
})();
