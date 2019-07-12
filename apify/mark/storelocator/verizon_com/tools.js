// Leaves only digits for the phone number
const formatPhoneNumber = string => string.replace(/\D/g, '');

const extractHourString = (array) => {
  if (!array || array.length < 1) {
    return undefined;
  }
  return array[0];
};

module.exports = {
  formatPhoneNumber,
  extractHourString,
};

/* Pre-format

{ location_name: 'Aspen Grove',
  '@context': 'http://schema.org',
  '@type': 'Store',
  image:
   'https://ss7.vzw.com/is/image/VerizonWireless/store-aspen-grove-203452-outside',
  '@id': 'https://www.verizonwireless.com/',
  name: 'Verizon Wireless',
  serviceJson: '',
  address:
   { '@type': 'PostalAddress',
     streetAddress: '7301 S Santa Fe Dr, Ste 724',
     addressLocality: 'Littleton',
     addressRegion: 'CO',
     postalCode: '80120',
     addressCountry: 'US' },
  geo:
   { '@type': 'GeoCoordinates',
     latitude: 39.5823397,
     longitude: -105.0258531 },
  url:
   'https://www.verizonwireless.com/stores/colorado/littleton/aspen-grove-203452/',
  telephone: '+1303.797.3224',
  openingHoursSpecification:
   [ { '@type': 'OpeningHoursSpecification', dayOfWeek: [Array] } ] }

*/
