$(document).ready(function(){
		jQuery.validator.addMethod("github", function( value, element ) {
			var result = this.optional(element) || (/^git@/i.test(value) && ! /\s/.test(value.trim()));
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

		jQuery.validator.addMethod("branch", function( value, element ) {
			var isValidate = false;
			if (/^https?:/.test(value)) {
				console.log("find it");
				if (/^https?:.*\/pull\/\d+$/.test(value)) {
					isValidate = true;
				} else {					
					isValidate = false;
				}
			} else {
				isValidate = this.optional(element) || ! /\s/.test(value.trim());
			}
			if (! isValidate) {
				//element.value = "";
				var validator = this;
				setTimeout(function() {
					validator.blockFocusCleanup = true;
					element.focus();
					validator.blockFocusCleanup = false;
				}, 1);
			}
			return isValidate;
		}, "Not a valid sugar branch");

		$("#addBuildForm").validate();
		$("#popView-actionBuildForm").validate();
		$("#popView-sendMailForm").validate();
	});
