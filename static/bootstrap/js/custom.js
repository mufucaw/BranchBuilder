$(document).ready(function(){
		var builder = {"hasRunningTask": false};

        var build_render = function (builds, perPage, pageNum) {
            var renderBody = "";

            for(var index = 0; index < builds.length; index ++) {
                renderBody += ' \
                <tr> \
                    <td>' + builds[index]["branch"] + '</td> \
                    <td>' + builds[index]["version"] + '</td> \
                    <td>' + builds[index]["last_build_date"] + '</td> \
                    <td>' + builds[index]["build_number"] + '</td> \
                    <td>' + builds[index]["status"] + '</td> \
                    <td>' + builds[index]["repos"] + '</td> \
                    <td>' + builds[index]["author"] + '</td> \
                    <td>' +  ' \
                        <input type="button" class="btn btn-success" name="rebuild" id="buildList-' + builds.task_id + '"  value="Build" >  \
                        <input type="button" data-toggle="modal" name="editBuild" class="btn" data-target="#popupViewBuild" id="editList-' + builds.task_id + '" value="Edit" > \
                        <a data-toggle="modal" name="duplicateBuild" class="btn" data-target="#popupViewBuild" id="dupList-' + builds.task_id + '" >Duplicate</a> \
                        <input type="button" class="btn btn-danger" name="removeBuild" id="buildListRemove-' + builds.task_id + '" value="Remove"> \
                    </td> \
                </tr>';

                if (index + 1 >= 20) {
                    break;
                }
            }

            return renderBody;
        };

        var getPageCount = function (totalCount, perPage) {
            var pageCount = 0;
            var perPage = perPage == "" ? 20 : perPage;

            pageCount = Math.floor(totalCount / perPage);

            if ((totalCount % perPage) > 0 && totalCount > perPage ) {
                pageCount ++;
            }

            if (pageCount == 0 && totalCount > 0) {
                pageCount ++;
            }
            
            return pageCount;
        }

        var renderBuildList = function(q, queryURL, pageNum) {
            $.getJSON( queryURL, {"q": q, "pageNum": pageNum})
             .done(function(builds_data){
                var perPage = 20;
                var pageCount = getPageCount(builds_data["builds_count"], perPage);

                if (pageCount == 0) {
                    pageNum = 0;
                }

                $("#buildList-tbody").html(build_render(builds_data["builds"], perPage));
                $("#buildList-pageNum-link").text(pageNum + " of " + pageCount);
                $("#buildList-pageNum").val(pageNum);
                $("#buildList-totalPage").val(pageCount);

             })
             .fail(function(jqxhr, textStatus, error){
                 console.log( "Request Failed: " + textStatus + "," + error);
             });
        }

		$("li.active").removeClass("active");
		$("#navHome").addClass("active");

		$('#package-help-info').popover({'title': 'Package info', 'content': 'Package can be "ult,ent,corp,pro,com"'});
		$('td[name="list_status"]').each(function (i, domEle){
			if ($(domEle).text() == "Running"){
				var task_id = $(domEle).attr("id").split("_");
				$("#buildList-" + task_id[2]).attr("disabled", "disabled");
				$('#editList-' + task_id[2]).attr("disabled", "disabled");
				$('#buildListRemove-' + task_id[2]).attr("disabled", "disabled");
			}
		});
		$('input[name="removeBuild"]').each(function(i, domEle){
			$(domEle).click(function(){
				var task_id = $(domEle).attr("id").split("-");
				$(this).attr("disabled", "disabled");
				$.get(
					'/BranchBuilder/remove',
					{"task_id": task_id[1]},
					function(data){
						window.location.reload(true);
					}
				);
			});
		});
		$('input[name="rebuild"]').each(function(i, domEle){
			$(domEle).click(function(){
				var task_id = $(domEle).attr("id").split("-");
				$(this).attr("disabled", "disabled");
				$('#build_status_' + task_id[1]).text("Starting...");
				$('#editList-' + task_id[1]).attr("disabled", "disabled");
				$('#buildListRemove-' + task_id[1]).attr("disabled", "disabled");
				$.get(
					'/BranchBuilder/build',
					{"task_id": task_id[1]},
					function(data){
						$('#build_status_' + data.task_id).text(data.status);
						window.location.reload(true);
					}
				);
			});
		});

		$('a[name="duplicateBuild"]').each(function(i, domEle){
			$(domEle).click(function(){
				var task_id = $(domEle).attr("id").split("-");
				$.get('/BranchBuilder/getbuild',
					{"task_id": task_id[1]},
					function(data){
						buildObj = data;
						$('#popView-repos').val(buildObj['repos']);
						$('#popView-branch').val(buildObj['branch']); 
						$('#popView-version').val(buildObj['version']); 
						$('#popView-author').val(buildObj['author']);
						$('#popView-styleguide_repo').val(buildObj['styleguide_repo']);
						$('#popView-styleguide_branch').val(buildObj['styleguide_branch']);
						$('#popView-sidecar_repo').val(buildObj['sidecar_repo']);
						$('#popView-sidecar_branch').val(buildObj['sidecar_branch']);
						$('#popView-package_list').val(buildObj['package_list']);
						$('#popView-upgrade_package').attr("checked", buildObj['upgrade_package'] ? true : false);
						$('#popView-latin').attr("checked", buildObj['latin'] ? true : false);
						$('#popView-demo_data').attr("checked", buildObj['demo_data'] ? true : false);
						
						//Set selectAction as editBuild
						$('#popView-selectAction').val('duplicateBuild');

						//Update the popup view title and build ID
						$('#popView-title').text('Duplicate build -- Task ID ' + task_id[1]);

						$('#popView-selectBuildID').val(task_id[1]);
					}
				);
			});
		});

		$('input[name="editBuild"]').each(function(i, domEle){
			$(domEle).click(function(){
				var task_id = $(domEle).attr("id").split("-");
				$.get('/BranchBuilder/getbuild',
					{"task_id": task_id[1]},
					function(data){
						var buildObj = data;
						$('#popView-repos').val(buildObj['repos']);
						$('#popView-branch').val(buildObj['branch']); 
						$('#popView-version').val(buildObj['version']); 
						$('#popView-author').val(buildObj['author']);
						$('#popView-styleguide_repo').val(buildObj['styleguide_repo']);
						$('#popView-styleguide_branch').val(buildObj['styleguide_branch']);
						$('#popView-sidecar_repo').val(buildObj['sidecar_repo']);
						$('#popView-sidecar_branch').val(buildObj['sidecar_branch']);
						$('#popView-package_list').val(buildObj['package_list']);
						$('#popView-upgrade_package').attr("checked", buildObj['upgrade_package'] ? true : false);
						$('#popView-latin').attr("checked", buildObj['latin'] ? true : false);
						$('#popView-demo_data').attr("checked", buildObj['demo_data'] ? true : false);

						//Set selectAction as editBuild
						$('#popView-selectAction').val('editBuild');

						//Update the popup view title and build ID
						$('#popView-title').text('Edit build -- Task ID ' + task_id[1]);
						$('#popView-selectBuildID').val(task_id[1]);
					}
				);
			});
		});
	
		$('#popView-Save').click(function(){
			//Check form validate firstly
			if (! $('#popView-actionBuildForm').valid()){
				return false;
			}

			var upgrade_package = $('#popView-upgrade_package').attr('checked') ? 1 : 0;
			var latin = $('#popView-latin').attr('checked') ? 1 : 0;
			var demo_data = $('#popView-demo_data').attr('checked') ? 1 : 0;
			if ($('#popView-selectAction').val() == 'duplicateBuild') {
				$.post('/BranchBuilder/add', 

					{
					 "repos": $('#popView-repos').val(),
					 "branch": $('#popView-branch').val(), 
					 "version": $('#popView-version').val(), 
					 "package_list": $('#popView-package_list').val(),
					 "author": $('#popView-author').val(),
					 "styleguide_repo": $('#popView-styleguide_repo').val(),
					 "styleguide_branch": $('#popView-styleguide_branch').val(),
					 "sidecar_repo": $('#popView-sidecar_repo').val(),
					 "sidecar_branch": $('#popView-sidecar_branch').val(),
					 "upgrade_package": upgrade_package,
					 "latin": latin,
					 "demo_data": demo_data
					 },

					 function(data){
						$("#popupViewBuild").modal("hide");
						location.reload();
					 }
				);
			} else if ($('#popView-selectAction').val() == 'editBuild'){
				$.post('/BranchBuilder/updatebuild', 

					{
					 "task_id": $('#popView-selectBuildID').val(), 
					 "repos": $('#popView-repos').val(),
					 "branch": $('#popView-branch').val(), 
					 "version": $('#popView-version').val(), 
					 "package_list": $('#popView-package_list').val(),
					 "author": $('#popView-author').val(),
					 "styleguide_repo": $('#popView-styleguide_repo').val(),
					 "styleguide_branch": $('#popView-styleguide_branch').val(),
					 "sidecar_repo": $('#popView-sidecar_repo').val(),
					 "sidecar_branch": $('#popView-sidecar_branch').val(),
					 "upgrade_package": upgrade_package,
					 "latin": latin,
					 "demo_data": demo_data
					 },

					 function(data){
						$("#popupViewBuild").modal("hide");

						location.reload();
					 }
				);
			}
		});

		$('#mailToAdmin').click(function(){
				$('#popView-MailFrom').val(""),
				$('#popView-MailSubject').val("");
				$('#popView-MailMessage').val("");
		});

		$('#popView-Send').click( function(){
			if ($('#popView-sendMailForm').valid()) {
				$.post('/BranchBuilder/sendmail',
					{
						"from_address": $('#popView-MailFrom').val(),
						"to": $('#popView-MailTo').val(),
						"subject": $('#popView-MailSubject').val(),
						"message": $('#popView-MailMessage').val()
					},
					function(data){
						$("#popupViewMail").modal("hide");
					}
				);
			}
		});
	
		setInterval(function(){
			var requestURL = "";
			if ( window.location.pathname.substr(-1) == "/" ) {
				requestURL = "./cron";
			} else {
				requestURL = window.location.pathname + "/cron";
			}
			$.get(
				requestURL,
				function(data){
					var task_id_list = [];
					var task_status_list = [];
					for (var x=0; x < data.length; x++) {
						task_id_list.push(data[x].task_id.toString());
						task_status_list.push(data[x].status.toString());
					}
					$('input[name="rebuild"]').each(function(i, domEle){
						var task_id =$(domEle).attr("id").split("-")[1]; 
						if (task_id_list.indexOf(task_id) != -1){
							var task_status = task_status_list[task_id_list.indexOf(task_id)];
							$('#buildList-' + task_id).attr("disabled", "disabled");
							$('#build_status_' + task_id).text(task_status);
							$('#build_status_' + task_id).attr("class", task_status);
							
							//Disable the edit button
							$('#editList-' + task_id).attr("disabled", "disabled");
							builder.hasRunningTask = true;
							
						} else {
							//window.location.reload()
							/*
							$(domEle).removeAttr('disabled');						
							//$('#build_status_' + task_id).text('Available');						
							$('#build_status_' + task_id).attr('class', 'Available');						
							//Remove disabled attr for edit button
							$('#editList-' + task_id).removeAttr("disabled");
							
							//Remove disabled attr for remove button
							$('#buildListRemove-' + task_id).removeAttr("disabled");
							*/
						}
					});
					if (task_id_list.length == 0 &&  builder.hasRunningTask == true){
						window.location.reload()
					}
					
				}
			);

		}, 10000);

        if ($("#buildList-pageNum").attr("value") == $("#buildList-totalPage").attr("value")) {
            $("#buildList-nextPage").removeClass("active");
            $("#buildList-nextPage").addClass("disabled");
            $("#buildList-nextPage-link").attr("href", "#");
            $("#buildList-lastPage").removeClass("active");
            $("#buildList-lastPage").addClass("disabled");
            $("#buildList-lastPage-link").attr("href", "#");
        }

        if ($("#buildList-pageNum").attr("value") == 1) {
            $("#buildList-prePage").removeClass("active");
            $("#buildList-prePage").addClass("disabled");
            $("#buildList-prePage-link").attr("href", "#");
            $("#buildList-firstPage").removeClass("active");
            $("#buildList-firstPage").addClass("disabled");
            $("#buildList-firstPage-link").attr("href", "#");
        }

        $("#searchForm-query").keyup(function(){
            var q = $(this).val();
            var queryURL = "./searchbuild";

            renderBuildList(q, queryURL, 1);
        });

        $("#buildList-firstPage-link").click(function(){
            if ($("#buildList-pageNum").val() > 1) {
                var q = $("#searchForm-query").val();
                var queryURL = "./searchbuild";

                renderBuildList(q, queryURL, 1);
            }
        });

        $("#buildList-prePage-link").click(function(){
            if ($("#buildList-pageNum").val() > 1) {
                var q = $("#searchForm-query").val();
                var queryURL = "./searchbuild";

                renderBuildList(q, queryURL, parseInt($("#buildList-pageNum").val()) - 1);
            }

            if ($("#buildList-pageNum").val() == 1) {
                $("#buildList-firstPage").removeClass("active");
                $("#buildList-firstPage").addClass("disabled");
                $("#buildList-prePage").removeClass("active");
                $("#buildList-prePage").addClass("disabled");
            }
        });

        $("#buildList-nextPage-link").click(function(){
            if ($("#buildList-totalPage").val() > 1 && $("#buildList-pageNum").val() < $("#buildList-totalPage").val()) {
                var q = $("#searchForm-query").val();
                var queryURL = "./searchbuild";

                renderBuildList(q, queryURL, parseInt($("#buildList-pageNum").val()) + 1);

                $("#buildList-firstPage").removeClass("disabled");
                $("#buildList-firstPage").addClass("active");
                $("#buildList-prePage").removeClass("disabled");
                $("#buildList-prePage").addClass("active");
            }

            if ($("#buildList-pageNum").val() == $("#buildList-totalPage").val() - 1) {
                $("#buildList-nextPage").removeClass("active");
                $("#buildList-nextPage").addClass("disabled");
                $("#buildList-lastPage").removeClass("active");
                $("#buildList-lastPage").addClass("disabled");
            }
        });

        $("#buildList-lastPage-link").click(function(){
            if ($("#buildList-totalPage").val() > 1) {
                var q = $("#searchForm-query").val();
                var queryURL = "./searchbuild";

                renderBuildList(q, queryURL, parseInt($("#buildList-totalPage").val()));
            }
        });


	});
