const Apify = require('apify');

const MISSING = '<MISSING>';
Apify.main(async () => {
  // Begin scraper
  const page_url = 'https://www.blackstonesteakhouse.com/location/blackstone-steakhouse/';
  const requestList = await Apify.openRequestList('black-stone-steak-house', [page_url]);

  const crawler = new Apify.CheerioCrawler({
    requestList,
    async handlePageFunction({ $ }) {
      const script = $('script[type="application/ld+json"]').get(0).lastChild.data;
      const data = JSON.parse(script)['subOrganization'][0];

      locator_domain = 'blackstonesteakhouse.com';
      location_type = data['@type'];
      location_name = data['name'];

      address = data['address'];
      street_address = address['streetAddress'];
      city = address['addressLocality'];
      state = address['addressRegion'];
      zip = address['postalCode'];

      map = $('.gmaps');
      lat = map.attr('data-gmaps-lat');
      lng = map.attr('data-gmaps-lng');

      phone = data['telephone'];

      hours = [];
      $('#intro p').each(function (i) {
        if (i) {
          const el = $(this);
          const [dayComp, timeComp] = el.html().split(/<br>/);
          const day = $(dayComp).html().replace('&#x2013;', '-').replace('&#xA0;', '');
          const time = timeComp.replace('&#xA0;', '');
          hours.push(`${day}: ${time}`);
        }
      });
      hours_of_operation = hours.join(', ');

      const poi = {
        locator_domain,
        location_name: location_name || MISSING,
        street_address: street_address || MISSING,
        city: city || MISSING,
        state: state || MISSING,
        zip: zip || MISSING,
        country_code: 'US',
        store_number: MISSING,
        phone: phone || MISSING,
        location_type: MISSING,
        latitude: lat || MISSING,
        longitude: lng || MISSING,
        hours_of_operation: hours_of_operation || MISSING,
      };

      await Apify.pushData(poi);
    },
  });

  await crawler.run();
  // End scraper
});
