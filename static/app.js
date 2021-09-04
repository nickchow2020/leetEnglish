$(document).ready(function(e){
	$("#avatar").msDropdown({visibleRows:4})
});

$("#addImageUrl").on( "click", function(){
	$("#addImageForm").toggle()
});

$(".tweets_group").on("click",function(e){
	$comment_icon = $(e.target).prop("tagName")
	$comment_form = $(e.target).parent().parent().prev()
	if ($comment_icon === "I"){
		if ($comment_form.hasClass("tweet_form") ){
			$comment_form.removeClass("tweet_form")
		}else{
			$comment_form.addClass("tweet_form")
		}
	}
})