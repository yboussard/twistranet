/*!
 * jQuery JavaScript Library v1.4.2
 * http://jquery.com/
 *
 * TwistraNet  javascript
 */

// helpers

setFirstAndLast = function(block, sub) {
   jQuery(block).each(function() {
      jQuery(sub+':first', jQuery(this)).addClass('first');
      jQuery(sub+':last', jQuery(this)).addClass('last');
   })
}

// global vars

var defaultDialogMessage = '';
// confirm boxes using jqueryui
initConfirmBox = function(elt){
    actionLabel = jQuery(elt).attr('title');
    actionLink = jQuery(elt).attr('href');
    dialogBox = jQuery('#tn-dialog');
    // the title of the box is kept using link title + ' ?'
    jQuery('#ui-dialog-title-tn-dialog').text(actionLabel+ ' ?');
    // the legend of the box is kept inside a invisible block with class 
    // confirm-message 
    // inside the link
    actionLegend = jQuery('.confirm-message', elt);
    if (actionLegend.length) jQuery('#tn-dialog-message').text(actionLegend.text());
    // translations for buttons are kept in the current page 
    // (could also be done using django javascript translations tools >> TODO)
    var cancelLabel = jQuery('#tn-dialog-button-cancel', dialogBox).text();
    var okLabel = jQuery('#tn-dialog-button-ok', dialogBox).text();
    var tnbuttons = {};  
    tnbuttons[okLabel] = function() {
    // ok action for now just redirect to the link
      window.location.replace(actionLink);
    };
    tnbuttons[cancelLabel] = function() {
      jQuery( this ).dialog( "close" );
    }; 
    dialogBox.dialog({   
      buttons: tnbuttons 
    });
    dialogBox.dialog('open');
}

// main class
var twistranet = {
    __init__: function(e) {
        /* finalize styles */
        twistranet.finalizestyles();
        twistranet.initconfirmdialogs();
    },
    finalizestyles: function(e) {
        /* some first and last classes */
        elts = [['.content-actions', 'li'] ];
        jQuery(elts).each(function(){
           setFirstAndLast(this[0], this[1]);
        } );
    },
    initconfirmdialogs: function(e){
        defaultDialogMessage = jQuery('#tn-dialog-message').text();
        jQuery("#tn-dialog").dialog({  
          resizable: false,
          draggable: false,
          autoOpen: false,
          height: 130,
          modal: true,
          close: function(ev, ui) { 
            jQuery('#tn-dialog-message').text(defaultDialogMessage);
            jQuery(this).hide(); 
          }
        });
        links = 'a.confirmbefore';
        jQuery(links).click(function(e){
           e.preventDefault();
           initConfirmBox(this);
        } );
    }
}

jQuery(document).ready(twistranet.__init__)