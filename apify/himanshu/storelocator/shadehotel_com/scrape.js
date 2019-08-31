const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'http://shadehotel.com/';
async function scrape(){

  return new Promise(async (resolve,reject)=>{
request(url,(err,res,html)=>{

  if(!err && res.statusCode==200){
   
     const $  =cheerio.load(html);
        var items=[];
        var main = $('.content-wrapper').children('div');
        function mainhead(i)

        {
            if(main.length>i)

                {
          var link_tmp =   $('.content-wrapper').find('.shade-property').eq(i).attr('onclick').split(',');
          var location_name =  $('.content-wrapper').find('.shade-property').eq(i).find('p').text();
          
          var link_tmp1 =link_tmp[1].split("');");
          var link = link_tmp1[0].replace("'","");
          request(link,(err,res,html)=>{

            if(!err && res.statusCode==200){
              const $  =cheerio.load(html);
               var main1 = $('.footer-middle-table').find('.c2').find('p').find('a').html();
               var add_tmp = main1.split('<br>');
               var address = add_tmp[0];
               var city_tmp = add_tmp[1].split(',');
               var city = city_tmp[0].replace(/\s/g,'').replace('Beach','');
               var state_tmp = city_tmp[1].split(' ');
               var state = state_tmp[1];
               var zip = state_tmp[2];


               var phone  = $('.footer-middle-table').find('.c2').find('p:nth-child(3)').find('a').text();
               var hour = $('.footer-middle-table').find('.c3').find('p').text().trim().replace(/\s/g,'');
              
               items.push({  

                locator_domain: 'http://shadehotel.com/', 

                location_name: location_name, 

                street_address: address,

                city: city, 

                state: state,

                zip:  zip,

                country_code: 'US',

                store_number: '<MISSING>',

                phone: phone,

                location_type: 'shadehotel',

                latitude: '<MISSING>',

                longitude: '<MISSING>', 

                hours_of_operation: hour});
                mainhead(i+1);

            }
          });
          
        
        

         
               
              
               
              
             
            }


            else{
        
            resolve(items);
        
            }
      } 

   mainhead(0);
               

          }
 
     });

  
    });
  }
  
    
   
  
  Apify.main(async () => {
  
      
  
      const data = await scrape();
      
      
       await Apify.pushData(data);
    
    });