/*---------------------------------------------------------------- 
  Copyright: 
  Copyright (C) 2009 danielfajardo web
  
  License:
  GPL Software 
  
  Author: 
  danielfajardo - http: //wwww.danielfajardo.com
---------------------------------------------------------------- */

jQuery(document).ready(function(){

    
    // Forms tab switching
    jQuery("fieldset.fieldset-inline-form legend a").click(function(event){
        event.preventDefault();
        event.stopPropagation();
        jQuery(this).parents("fieldset").hide();
        jQuery(jQuery(this).attr('href')).show();
        return false;
    });
    

	// Superfish mainmenu
	//
  jQuery("#mainmenu ul.sf-menu").superfish({
  	animation: {width:'show'},
		speed: 2,   // speed for submenu apparition
		delay: 400, // the delay in milliseconds that the mouse can remain outside a submenu without closing 
		minWidth: 10,
		maxWidth: 20,
		extraWidth: 0
  });
	if( BrowserDetect.browser=="Explorer" ) {
	  jQuery("#mainmenu").mouseenter(
			function(){
				jQuery("#breadcrumb").fadeOut();
			}
	  ).mouseleave(
			function(){
				jQuery("#breadcrumb").fadeIn(1000);
			}
	  );
	}

	// Links effect
	//
	/*
	if( BrowserDetect.browser!="Explorer" ) {
		jQuery("a").hover(
			function(){
				jQuery(this).parent().addClass("selected");
				jQuery(this).animate({opacity: 0.5},200);
				jQuery(this).animate({opacity: 1},100);
			},
			function(){
				jQuery(this).parent().removeClass("selected");
				jQuery(this).animate({opacity: 1},100);
			}
		);
	}*/

	// External Links
	//
	jQuery("ul.links li a").append(" <img src='/images/icons/external.png' border ='0' />");
	jQuery("a.external").append(" <img src='/images/icons/external.png' border ='0' />");

	// Go To Top
	//
	/*
	jQuery("span#gototop a").click( function() {
		jQuery.scrollTo(jQuery("body"), 1000);
		return false;
	});
	*/
});
