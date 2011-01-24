// resource widget helper

var default_publisher_id = '';
var current_selection ='';
var new_selection='';
var selector = '';
var Panels = {};
var allow_browser_selection=0;

showPreview = function(url, miniurl, previewurl, legend, type) {
    newResultContainer = jQuery('#renderer-new');
    if (newResultContainer.length) {
        currentResultContainer = jQuery('#renderer-current');
        result= '\
<a class="image-block image-block-mini"\
   href="'+ url +'"\
   title="' + legend + '">\
   <img src="' + miniurl + '"\
        alt="' + legend + '" />\
</a>\
';
        if (allow_browser_selection) {
            if (type=='image') {
                result += '\
    <div class="sizes-selection">\
      <h4>Choose Sizes for "' + legend + '"</h4>\
      <form id="browser-selection-form">\
        <p>\
          <input type="radio"\
                 checked="checked"\
                 id="selection-full"\
                 name="selection"\
                 value="' + url + '" />\
          <label for="selection-full">Full size</label>\
        </p>\
        <p>\
          <input type="radio"\
                 id="selection-preview"\
                 name="selection"\
                 value="' + previewurl + '" />\
          <label for="selection-preview">Medium size (500*500 max)</label>\
        </p>\
        <p>\
          <input type="radio"\
                 id="selection-mini"\
                 name="selection"\
                 value="' + miniurl + '" />\
          <label for="selection-mini">Thumbnail cropped (100*100)</label>\
        </p>\
        <div class="form-controls">\
          <input type="submit" value="OK" />\
        </div>\
      </form>\
    </div>\
    ';
            }
            // for simple file
            else {
                result += '\
    <div class="sizes-selection">\
      <h4>' + legend + '</h4>\
      <form id="browser-selection-form">\
        <p>\
          <input type="radio"\
                 checked="checked"\
                 id="selection-full"\
                 name="selection"\
                 value="' + url + '" />\
          <label for="selection-full">Link the file</label>\
        </p>\
        <div class="form-controls">\
          <input type="submit" value="OK" />\
        </div>\
      </form>\
    </div>\
    ';
            }
        }

        jQuery('>a', newResultContainer).remove();
        jQuery('.sizes-selection', newResultContainer).remove();
        newResultContainer.append(result);
        newResultContainer.css('visibility', 'visible');
        if (currentResultContainer.length) currentResultContainer.animate({'opacity': '0.4'}, 500);
        
        if (allow_browser_selection) {
            jQuery(document).ready(function(){
                jQuery('#browser-selection-form').bind('submit', function(e){
                    e.preventDefault();
                    e.stopPropagation();
                    URL = jQuery('input:checked', this).val();
                    FileBrowserDialogue.submit(URL, legend);
                    return false;
                });
            });
        }
    }
}

hidePreview = function() {
    newResultContainer = jQuery('#renderer-new');
    if (newResultContainer.length) {
        currentResultContainer = jQuery('#renderer-current');
        jQuery('a', newResultContainer).remove();
        if (currentResultContainer.length) currentResultContainer.animate({'opacity': '1'}, 500);
    }
}

// load resources in json for a publisher (scope_id)
loadScopeResources = function(scope_id, selection) {
    scopeContainer = jQuery('#resourcepane-'+scope_id);
    scopeUrl = '/resource_by_publisher/json/';
    var tnGrid = jQuery('.tnGrid', scopeContainer);
    tnGrid.empty();
    jQuery.get(scopeUrl+scope_id+'?selection=' + selection,
          function(data) {
              dataobject = eval( "(" + data + ")" );
              results = dataobject.results;
              nbresults = results.length;
              if (!nbresults) {
                  jQuery('.mediaresource-scopetitle', scopeContainer).hide();
                  jQuery('.mediaresource-noresults', scopeContainer).show();
              }
              else {
                  jQuery('.mediaresource-scopetitle', scopeContainer).show();
                  jQuery('.mediaresource-noresults', scopeContainer).hide();
              }
              jQuery(results).each(function() {
                  html = '\
<div class="tnGridItem">\
  <div class="thumbnail-account-part thumbnail-50-bottom">\
    <a href="' + this.url + '"\
       title="' + this.title + '"\
       class="image-block image-block-tile">\
      <img src="' + this.thumbnail_url + '"\
           alt="' + this.title + '" />\
    </a>\
    <label>\
      <a href="' + this.url + '">' + this.title + '</a>\
    </label>\
  </div>\
  <input type="radio"\
         name="grid-item-input"\
         class="grid-item-input"\
         value="' + this.id + '"\
         ' + this.selected + ' />\
  <input type="hidden"\
         name="grid-item-previewurl"\
         class="grid-item-previewurl"\
         value="' + this.preview_url + '" />\
  <input type="hidden"\
         name="grid-item-miniurl"\
         class="grid-item-miniurl"\
         value="' + this.mini_url + '" />\
  <input type="hidden"\
         name="grid-item-type"\
         class="grid-item-type"\
         value="' + this.type + '" />\
</div>\
';
                  tnGrid.append(html);
              });
          gridStyle(tnGrid[0]);
          gridOnSelect(tnGrid[0]) ;
          widgetHeight();
          } );
    Panels[scope_id] = 'loaded';

}
// function called after upload or any change (imagine possible things in future))
// TODO put a wait loading icon
reloadScope = function(scope_id, selection, reload) {
    jQuery('.resourcePane').hide();
    jQuery('.resourcePane').removeClass('activePane');
    jQuery('#resourcepane-'+scope_id).addClass('activePane');
    if (reload) {
        loadScopeResources(scope_id, selection);
    }
    if (typeof uploadparams != 'undefined') uploadparams.publisher_id = scope_id;
    jQuery('#resourcepane-'+scope_id).fadeIn(1000);
}

// calculate the good height
//it's important when displaying widget in a form to avoid bad moving effects
widgetHeight = function() {
    var selector_height = 0;
    jQuery('.tnGrid').each(function(){
        nbrows = jQuery('.tnGridRow', this).length ;
        new_height = 100*nbrows+20;
        if (new_height > selector_height) selector_height = new_height;
    });
    jQuery('#resources-selector').height(selector_height);
}

getActivePublisher = function() {
    return jQuery('.activePane input.scopeId').val();
}




// TODO in V1: beurk jquery style like, make it more pythonic
jQuery(
    function(){
        reswidget = jQuery('.resource-widget');
        theform = reswidget.parents('form');
        target_selector = jQuery('#selector_target', reswidget);
        allow_browser_selection_field = jQuery('#allow_browser_selection');
        if (allow_browser_selection_field.length) allow_browser_selection = parseInt(allow_browser_selection_field.val());
        if (target_selector.length) {
            selector = jQuery('#' + target_selector.val());
            current_selection = selector.val();
            new_selection = selector.val();
            default_publisher_id = getActivePublisher();
            // remove input fields used by ajax requests only
            theform.bind('submit', function(){
                 target_selector.remove();
                 allow_browser_selection_field.remove();
                 jQuery('.tnGrid input', reswidget).remove();
            })
            // preload resources in background
            jQuery('.resourcePaneFiles').each(function(){
                scope_id = jQuery('.scopeId', this).val();
                loadScopeResources(scope_id, current_selection);
            });
            // when selecting a scope (account) we show the good pane
            jQuery('#resourcepane-main .tnGridItem').click(function(e){
                var scope_id = jQuery('>input:hidden', this).val();
                jQuery('.resourcePane').hide();
                if (Panels[scope_id]=='unloaded') reloadScope(scope_id, new_selection, true);
                else reloadScope(scope_id, new_selection, false);
            })

            // back to all accounts action
            jQuery('.resource-back-button').click(function(e){
                jQuery('.resourcePane').hide();
                jQuery('#resourcepane-main').fadeIn(500);
            })
            // redefine the gridOnChange method (used everywhere on twistranet)
            // because we want to unselect all elements from all panels
            gridOnChange = function(grid) {
                jQuery('.resourcePane .tnGridItem').each(function(){
                    var checkbox = jQuery('>input:checkbox, >input:radio', this);
                    if (checkbox.length) {
                        if (checkbox.is(':checked')) {
                            jQuery(this).addClass('itemSelected');
                        }
                        else {
                            jQuery(this).removeClass('itemSelected');
                        }
                    }
                });
                if (! jQuery('.resourcePane .itemSelected').length) {
                    hidePreview();
                    new_selection = current_selection;
                }
                else {
                    itemselected = jQuery('.resourcePane .itemSelected')[0];
                    var checkbox = jQuery('>input:checkbox, >input:radio', itemselected);
                    new_selection = checkbox.val();
                    if (new_selection!=current_selection) {
                        showPreview(jQuery('a', itemselected).attr('href'),
                                    jQuery('.grid-item-miniurl', itemselected).val(),
                                    jQuery('.grid-item-previewurl', itemselected).val(),
                                    jQuery('a', itemselected).attr('title'),
                                    jQuery('.grid-item-type', itemselected).val());
                    }
                }
                selector.val(new_selection).trigger('change');
            }
        }
    }
)