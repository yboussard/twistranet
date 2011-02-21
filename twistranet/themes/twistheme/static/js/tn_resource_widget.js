// resource widget helper

var default_publisher_id = '';
var current_selection ='';
var new_selection='';
var selector = '';
var Panels = {};
var allow_browser_selection=0;

showPreview = function(url, thumbnailurl, miniurl, summaryurl, previewurl, legend, type) {
    newResultContainer = jq('#renderer-new');
    if (newResultContainer.length) {
        currentResultContainer = jq('#renderer-current');
        if (type=='image') {
            result= '\
<a class="image-block"\
   href="'+ url +'"\
   title="' + legend + '">\
   <img src="' + miniurl + '"\
        alt="' + legend + '" />\
   <span class="image-block-legend">' + legend + '</span>\
</a>\
';
        }
        else {
            result= '\
<a class="image-block"\
   href="'+ url +'"\
   title="' + legend + '">\
   <img src="' + thumbnailurl + '"\
        alt="' + legend + '" />\
   <span class="image-block-legend">' + legend + '</span>\
</a>\
';
        }
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
                 id="selection-summary"\
                 name="selection"\
                 value="' + summaryurl + '" />\
          <label for="selection-summary">Small size (100*100)</label>\
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

        jq('>a', newResultContainer).remove();
        jq('.sizes-selection', newResultContainer).remove();
        newResultContainer.append(result);
        newResultContainer.css('visibility', 'visible');
        if (currentResultContainer.length) currentResultContainer.animate({'opacity': '0.4'}, 500);

        if (allow_browser_selection) {
            jq(document).ready(function(){
                jq('#browser-selection-form').bind('submit', function(e){
                    e.preventDefault();
                    e.stopPropagation();
                    URL = jq('input:checked', this).val();
                    FileBrowserDialogue.submit(URL, legend);
                    return false;
                });
            });
        }
    }
}

hidePreview = function() {
    newResultContainer = jq('#renderer-new');
    if (newResultContainer.length) {
        currentResultContainer = jq('#renderer-current');
        jq('a', newResultContainer).remove();
        if (currentResultContainer.length) currentResultContainer.animate({'opacity': '1'}, 500);
    }
}

// load resources in json for a publisher (scope_id)
loadScopeResources = function(scope_id, selection, media_type) {
    scopeContainer = jq('#resourcepane-'+scope_id);
    scopeUrl = home_url + 'resource_by_publisher/json/';
    var tnGrid = jq('.tnGrid', scopeContainer);
    tnGrid.empty();
    jq.get(scopeUrl + scope_id + '?selection=' + selection +'&media_type=' + media_type,
          function(data) {
              dataobject = eval( "(" + data + ")" );
              results = dataobject.results;
              nbresults = results.length;
              if (!nbresults) {
                  jq('.mediaresource-scopetitle', scopeContainer).hide();
                  jq('.mediaresource-noresults', scopeContainer).show();
              }
              else {
                  jq('.mediaresource-scopetitle', scopeContainer).show();
                  jq('.mediaresource-noresults', scopeContainer).hide();
              }
              jq(results).each(function() {
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
         name="grid-item-thumbnailurl"\
         class="grid-item-thumbnailurl"\
         value="' + this.thumbnail_url + '" />\
  <input type="hidden"\
         name="grid-item-summaryurl"\
         class="grid-item-summaryurl"\
         value="' + this.summary_url + '" />\
  <input type="hidden"\
         name="grid-item-type"\
         class="grid-item-type"\
         value="' + this.type + '" />\
</div>\
';
                  tnGrid.append(html);
              });
          if (tnGrid.length) {
              gridStyle(tnGrid[0]);
              gridOnSelect(tnGrid[0]) ;
          }
          //widgetHeight();
          } );
    Panels[scope_id] = 'loaded';

}
// function called after upload or any change (imagine possible things in future))
// TODO put a wait loading icon
reloadScope = function(scope_id, selection, reload) {
    jq('.resourcePane').hide();
    jq('.resourcePane').removeClass('activePane');
    jq('#resourcepane-'+scope_id).addClass('activePane');
    if (reload) {
        loadScopeResources(scope_id, selection);
    }
    if (typeof uploadparams != 'undefined') uploadparams.publisher_id = scope_id;
    jq('#resourcepane-'+scope_id).fadeIn(1000);
}

// calculate the good height
//it's important when displaying widget in a form to avoid bad moving effects
widgetHeight = function() {
    var selector_height = 0;
    jq('.tnGrid').each(function(){
        nbrows = jq('.tnGridRow', this).length ;
        new_height = 100*nbrows+20;
        if (new_height > selector_height) selector_height = new_height;
    });
    jq('#resources-selector').height(selector_height);
}

// XXX larache
getActivePublisher = function() {
    // if resource panes, we always upload on default publisher anyway
    publisher_pane = jq('.activePane input.publisherId')
    if (publisher_pane.length)   return publisher_pane.val();
    // upload alone
    return jq('input[name="publisher_id"]' ,jq('.resource-widget').parents('form')).val();
}




// TODO in V1: beurk jquery style like, make it more pythonic
jq(
    function(){
        reswidget = jq('.resource-widget');
        theform = reswidget.parents('form');
        target_selector = jq('input[name=selector_target]', reswidget);
        target_media_type = jq('input[name=media_type]', reswidget);
        allow_browser_selection_field = jq('#allow_browser_selection');
        if (allow_browser_selection_field.length) allow_browser_selection = parseInt(allow_browser_selection_field.val());
        if (target_selector.length) {
            selector = jq('#' + target_selector.val());
            current_selection = selector.val();
            new_selection = selector.val();
            default_publisher_id = getActivePublisher();
            // remove input fields used by ajax requests only
            theform.bind('submit', function(){
                 target_selector.remove();
                 target_media_type.remove();
                 allow_browser_selection_field.remove();
                 jq('.tnGrid input', reswidget).remove();
            })
            // preload resources in background
            jq('.resourcePaneFiles').each(function(){
                scope_id = jq('.scopeId', this).val();
                loadScopeResources(scope_id, current_selection, target_media_type.val());
            });
            // when selecting a scope (account) we show the good pane
            jq('#resourcepane-main .tnGridItem').click(function(e){
                var scope_id = jq('>input:hidden', this).val();
                jq('.resourcePane').hide();
                if (Panels[scope_id]=='unloaded') reloadScope(scope_id, new_selection, true);
                else reloadScope(scope_id, new_selection, false);
            })

            // back to all accounts action
            jq('.resource-back-button').click(function(e){
                jq('.resourcePane').hide();
                jq('#resourcepane-main').fadeIn(500);
            })
            // redefine the gridOnChange method (used everywhere on twistranet)
            // because we want to unselect all elements from all panels
            gridOnChange = function(grid) {
                jq('.resourcePane .tnGridItem').each(function(){
                    var checkbox = jq('>input:checkbox, >input:radio', this);
                    if (checkbox.length) {
                        if (checkbox.is(':checked')) {
                            jq(this).addClass('itemSelected');
                        }
                        else {
                            jq(this).removeClass('itemSelected');
                        }
                    }
                });
                if (! jq('.resourcePane .itemSelected').length) {
                    hidePreview();
                    new_selection = current_selection;
                }
                else {
                    itemselected = jq('.resourcePane .itemSelected')[0];
                    var checkbox = jq('>input:checkbox, >input:radio', itemselected);
                    new_selection = checkbox.val();
                    if (new_selection!=current_selection) {
                        // event triggered on hidden field for unload protection
                        selector.trigger('change');
                        showPreview(jq('a', itemselected).attr('href'),
                                    jq('.grid-item-thumbnailurl', itemselected).val(), 
                                    jq('.grid-item-miniurl', itemselected).val(),
                                    jq('.grid-item-summaryurl', itemselected).val(),
                                    jq('.grid-item-previewurl', itemselected).val(),
                                    jq('a', itemselected).attr('title'),
                                    jq('.grid-item-type', itemselected).val());
                    }
                    else {
                        hidePreview();
                    }
                }
                selector.val(new_selection);
            }
        }
    }
)
