$(function() 
{
  $(".view_comments").click(function() 
  {
    var ID = $(this).attr("id");
    
    $.ajax({
      type: "GET",
      url: "/comment/" + ID + "/list.xml",
      // data: "msg_id="+ ID, 
      cache: false,
      success: function(html){
        var comments_container = $("#view_comments"+ID);
        comments_container.prepend(html);
        $("#view"+ID).remove();
        $("#two_comments"+ID).remove(); 
        twistranet.showCommentsActions();
        $('a.confirmbefore', comments_container).click(function(e){
           e.preventDefault();
           initConfirmBox(this);
        } );
      }
    });
    return false;
  });
});

