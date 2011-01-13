// reource widget helper


jQuery(
    function(){
        reswidget = jQuery('.resource-widget');
        theform = reswidget.parents('form');
        target_selector = jQuery('#selector_target', reswidget);
        if (target_selector.length) {
            theform.bind('submit', function(){
                 selectedfield = jQuery('.tnGrid input:checked', reswidget);
                 if (selectedfield.length) {
                     jQuery('#' + target_selector.val()).val(selectedfield.val());
                 }
                 target_selector.remove();
                 jQuery('input .tnGrid', reswidget).remove();
            })
            // when selecting a scope (account show the good pane)
            jQuery('#resourcepane-main .tnGridItem').click(function(){
                var scope_id = jQuery('>input:hidden', this).val();
                jQuery('.resourcePane').hide();
                jQuery('#resourcepane-'+scope_id).show(1000);
            })
            
            // redefine the gridOnChange method
            // because we want to unselect all elements from all panels
            gridOnChange = function(grid) {
                jQuery('.resourcePane .tnGridItem').each(function(){
                    var item = jQuery(this);       
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
            }
        }
    }
)