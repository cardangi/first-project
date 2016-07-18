jQuery(document).ready(function($){

	// Browser window scroll in pixels after which the "back to top" link is shown.
	var offset = 10000,
	
		// Browser window scroll in pixels after which the "back to top" link opacity is reduced.
		offset_opacity = 15000,
		
		// Duration in ms of the top scrolling animation.
		scroll_top_duration = 700,
		
		// Grab the "back to top" link.
		$back_to_top = $('.cd-top');

	// Hide or show the "back to top" link.
	$(window).scroll(function(){
		( $(this).scrollTop() > offset ) ? $back_to_top.addClass('cd-is-visible') : $back_to_top.removeClass('cd-is-visible cd-fade-out');
		if( $(this).scrollTop() > offset_opacity ) { 
			$back_to_top.addClass('cd-fade-out');
		}
	});

	// Smooth scroll to top.
	$back_to_top.on('click', function(event){
		event.preventDefault();
		$('body,html').animate({
			scrollTop: 0 ,
		 	}, scroll_top_duration
		);
	});

});