$(document).ready(
	function() {
		$("#add-version").change(function() {
			self = this;
			var repo_branch_ids = {
				"Mango": {
					"repo_id": "add-repos",
					"branch_id": "add-branch"
				},
				"Sidecar": {
					"repo_id": "add-sidecar_repo",
					"branch_id": "add-sidecar_branch"
				},
				"Styleguide": {
					"repo_id": "add-styleguide_repo",
					"branch_id": "add-styleguide_branch"
				}
			};
			
			function render_version(data) {
				var trs = '';
				
				data.forEach(function(item) {
					var id_list = repo_branch_ids[item.repo_name];
					var repo_id = "";
					var branch_id = "";
						
					trs += '<tr>';
					
					trs +='<td width="15%">' + item.repo_name + ':</td>';
					trs +='<td width="45%"><input type="text"  \
						id="' + id_list["repo_id"] + '" \
						class="span12 required github" name="repos" placeholder="Git Repository URI" \
						value="' + item.repo_url + '"/> \
					</td>';
					trs +='<td width="40%"><input type="text" \
						id="' + id_list["branch_id"] + '" class="span12 required" name="branch" placeholder="Branch" \
						value="' + item.branch + '"/> \
					</td>';
					
					trs += '</tr>';
				});
				
				trs += '<td>Author</td>';
				trs += '<td><input type="text" id="add-author" class="input-xlarge required" name="author" placeholder="Author" /></td>';
				trs += '<td></td>';
				
				return trs;
			}
			
			if ($(self).find(":selected").val() != "blank") {
				$.get(
					'./mappedversion',
					{
					"version": $(self).find(":selected").val()
					}
				)
				.done(function(data) {
					if (data.length > 0) {
						$("#mapped_version").show();
						
						$("#mapped_version_list").html(render_version(data));
					} else {
						console.log("can not find available version");
					}
				})
				.fail(function() {
					alert("failed to retrieve version!");
				});		
			} else {
				$("#mapped_version").hide();
			}

		});

});
