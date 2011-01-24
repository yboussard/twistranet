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
$("#view_comments"+ID).prepend(html);
$("#view"+ID).remove();
$("#two_comments"+ID).remove();
}
});
return false;
});
});

