$(document).ready(function(){
		jQuery.validator.addMethod("github", function( value, element ) {
			var result = this.optional(element) || /^git@/i.test(value);
			if (!result) {
				//element.value = "";
				var validator = this;
				setTimeout(function() {
					validator.blockFocusCleanup = true;
					element.focus();
					validator.blockFocusCleanup = false;
				}, 1);
			}
			return result;
		}, "Not a valid git repo");
		jQuery.validator.addMethod("version", function( value, element ) {
			var result = this.optional(element) || /^v?(\d+\.)+\d+((beta)|(RC))?\d*$/i.test(value);
			if (!result) {
				//element.value = "";
				var validator = this;
				setTimeout(function() {
					validator.blockFocusCleanup = true;
					element.focus();
					validator.blockFocusCleanup = false;
				}, 1);
			}
			return result;
		}, "Not a valid sugar version");
		$("#addBuildForm").validate();
		$("#popView-actionBuildForm").validate();
		$("#popView-sendMailForm").validate();
	});
