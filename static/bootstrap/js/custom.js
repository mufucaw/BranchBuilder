$(document).ready(function(){
		var builder = {"hasRunningTask": false};
        window.favicon = new Favico({
            "animation": "none"
        });
        function update_favicon() {
            var length = $('td[name="list_status"].Running, td[name="list_status"].InQueue').length;
            window.favicon_len = length;
            favicon.badge(length);
        }
        update_favicon();

		$("li.active").removeClass("active");
		$("#navHome").addClass("active");

        var get_username = function(author) {
            var username = "";
            author = author.replace(/\.|_|-|#|(|)/g, "");
            var part_list = author.trim().split(/\s+/);

            if (part_list.length > 1) {
                username = part_list[0].charAt(0) + part_list[part_list.length - 1];
            } else {
                username = part_list[0];
            }
            console.log(username);

            return username.toLowerCase().substr(0, 64);
        };

        var get_branch_name = function (branch) {
            if (/^https?:.*\/pull\/\d+$/.test(branch)) {
                var pattern = /^https?:.*\/pull\/(\d+)$/g;
                var matched = pattern.exec(branch);

                branch = "pr" + matched[1];
            } 

            return branch;   
        
        };

        var tr_render = function (build) {
            var trBody = ' \
                <td><a href="../build' + build["username"] + get_branch_name(build["branch"]) + '.html">' + get_branch_name(build["branch"]) + '</a></td> \
                <td>' + build["version"] + '</td> \
                <td><a href="../public/builds/' + build["username"] + get_branch_name(build["branch"]) + '/latest">' + build["last_build_date"] + '</a></td> \
                <td>' + build["build_number"] + '</td> \
                <td name="list_status" class="' + build["status"] + '"' + 'id="build_status_' + build["task_id"] + '">' + build["status"] + '</td> \
                <td>' + build["repos"] + '</td> \
                <td>' + build["author"] + '</td> \
                <td><a href="/logs/builds/' + build["task_id"] + '.log" target="_blank">log</a></td> \
                <td>' +  ' \
                    <input type="button" class="btn btn-success" name="rebuild" id="buildList-' + build["task_id"] + '"  value="Build" >  \
                    <input type="button" data-toggle="modal" name="editBuild" class="btn" data-target="#popupViewBuild" id="editList-' + build["task_id"] + '" value="Edit" > \
                    <a data-toggle="modal" name="duplicateBuild" class="btn" data-target="#popupViewBuild" id="dupList-' + build["task_id"] + '" >Duplicate</a> \
                    <input type="button" class="btn btn-danger" name="removeBuild" id="buildListRemove-' + build["task_id"] + '" value="Remove"> \
                </td> \
                ';
            return trBody;
        };

        var build_render = function (build) {
            var actionPart = ' \
                    <input type="button" class="btn btn-success" name="rebuild" id="buildList-' + build["task_id"] + '"  value="Build" >  \
                    <input type="button" data-toggle="modal" name="editBuild" class="btn" data-target="#popupViewBuild" id="editList-' + build["task_id"] + '" value="Edit" > \
                    <a data-toggle="modal" name="duplicateBuild" class="btn" data-target="#popupViewBuild" id="dupList-' + build["task_id"] + '" >Duplicate</a> \
                    <input type="button" class="btn btn-danger" name="removeBuild" id="buildListRemove-' + build["task_id"] + '" value="Remove"> \
                    ';
            if (build["status"] == "Running" || build["status"] == "InQueue") {
                actionPart = ' \
                    <input type="button" class="btn btn-success" name="rebuild" id="buildList-' + build["task_id"] + '"  value="Build" >  \
                    <input type="button" data-toggle="modal" name="editBuild" class="btn" data-target="#popupViewBuild" id="editList-' + build["task_id"] + '" value="Edit" > \
                    a href="stopbuild?task_id=${build.task_id}" name="stopBuild" class="btn" id="stopList-$build.task_id" >Stop</a> \
                    ';
            }
            var renderBody = ' \
            <tr id="' + build["task_id"] + '"> \
                <td><a href="../build' + build["username"] + get_branch_name(build["branch"]) + '.html">' + get_branch_name(build["branch"]) + '</a></td> \
                <td>' + build["version"] + '</td> \
                <td><a href="../public/builds/' + build["username"] + get_branch_name(build["branch"]) + '/latest">' + build["last_build_date"] + '</a></td> \
                <td>' + build["build_number"] + '</td> \
                <td name="list_status" class="' + build["status"] + '"' + 'id="build_status_' + build["task_id"] + '">' + build["status"] + '</td> \
                <td>' + build["repos"] + '</td> \
                <td>' + build["author"] + '</td> \
                <td><a href="/logs/builds/' + build["task_id"] + '.log" target="_blank">log</a></td> \
                <td>' +  ' \
                    <input type="button" class="btn btn-success" name="rebuild" id="buildList-' + build["task_id"] + '"  value="Build" >  \
                    <input type="button" data-toggle="modal" name="editBuild" class="btn" data-target="#popupViewBuild" id="editList-' + build["task_id"] + '" value="Edit" > \
                    <a data-toggle="modal" name="duplicateBuild" class="btn" data-target="#popupViewBuild" id="dupList-' + build["task_id"] + '" >Duplicate</a> \
                    <input type="button" class="btn btn-danger" name="removeBuild" id="buildListRemove-' + build["task_id"] + '" value="Remove"> \
                </td> \
            </tr>';
            
            return renderBody;
        };

        var buildListEventBind = function () {
            $('#package-help-info').popover({'title': 'Package info', 'content': 'Package can be "ult,ent,corp,pro,com"'});
            $('td[name="list_status"]').each(function (i, domEle){
                if ($(domEle).text() == "Running" || $(domEle).text() == "InQueue") {
                    var task_id = $(domEle).parent().attr("id");
                    $("#buildList-" + task_id).attr("disabled", "disabled");
                    $('#editList-' + task_id).attr("disabled", "disabled");
                    $('#buildListRemove-' + task_id).attr("disabled", "disabled");
                }
            });
            $('input[name="removeBuild"]').each(function(i, domEle){
                $(domEle).click(function(){
                    var task_id = $(domEle).parent().parent().attr("id");
                    $(this).attr("disabled", "disabled");
                    $.get(
                        './remove',
                        {"task_id": task_id},
                        function(data){
                            //window.location.reload(true);
                            $("#" + task_id).remove();
                        }
                    );
                });
            });
            $('input[name="rebuild"]').each(function(i, domEle){
                $(domEle).click(function(){
                    var task_id = $(domEle).parent().parent().attr("id");
                    $(this).attr("disabled", "disabled");
                    $('#build_status_' + task_id).text("Starting...");
                    $('#editList-' + task_id).attr("disabled", "disabled");
                    $('#buildListRemove-' + task_id).attr("disabled", "disabled");
                    $.get(
                        './build',
                        {"task_id": task_id},
                        function(data){
                            $('#build_status_' + data.task_id).text(data.status);
                            $('#build_status_' + data.task_id).attr("class", data.status);
                            //window.location.reload(true);
                        }
                    )
                    .fail(function(){
                        $(this).removeAttr("disabled");
                        $('#build_status_' + task_id).text("Available");
                        $('#editList-' + task_id).removeAttr("disabled");
                        $('#buildListRemove-' + task_id).removeAttr("disabled");
                        alert("Failed to start current build, please wait a second or reload the page then re-try !");
                    });
                });
            });

            $('a[name="duplicateBuild"]').each(function(i, domEle){
                $(domEle).unbind("click").click(function(){
                    var task_id = $(domEle).parent().parent().attr("id");
                    $.get('./getbuild',
                        {"task_id": task_id},
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
                            $('#popView-upgrade_package').attr("checked", buildObj['upgrade_package'] == "1" ? true : false);
                            $('#popView-latin').attr("checked", buildObj['latin'] == "1" ? true : false);
                            $('#popView-demo_data').attr("checked", buildObj['demo_data'] == "1" ? true : false);
                            $('#popView-expired_tag').attr("checked", buildObj['expired_tag'] == "1" ? true : false);
                            
                            //Set selectAction as editBuild
                            $('#popView-selectAction').val('duplicateBuild');

                            //Update the popup view title and build ID
                            $('#popView-title').text('Duplicate build -- Task ID ' + task_id);

                            $('#popView-selectBuildID').val(task_id);
                        }
                    );
                });
            });

            $('input[name="editBuild"]').each(function(i, domEle){
                $(domEle).click(function(){
                    var task_id = $(domEle).parent().parent().attr("id");
                    $.get('./getbuild',
                        {"task_id": task_id},
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
                            $('#popView-upgrade_package').attr("checked", buildObj['upgrade_package'] == "1" ? true : false);
                            $('#popView-latin').attr("checked", buildObj['latin'] == "1" ? true : false);
                            $('#popView-demo_data').attr("checked", buildObj['demo_data'] == "1" ? true : false);
                            $('#popView-expired_tag').attr("checked", buildObj['expired_tag'] == "1" ? true : false);

                            //Set selectAction as editBuild
                            $('#popView-selectAction').val('editBuild');

                            //Update the popup view title and build ID
                            $('#popView-title').text('Edit build -- Task ID ' + task_id);
                            $('#popView-selectBuildID').val(task_id);
                        }
                    );
                });
            });
        
            $('#popView-Save').unbind("click").click(function(){
                //Check form validate firstly
                if (! $('#popView-actionBuildForm').valid()){
                    return false;
                }

                var upgrade_package = $('#popView-upgrade_package').attr('checked') ? 1 : 0;
                var latin = $('#popView-latin').attr('checked') ? 1 : 0;
                var demo_data = $('#popView-demo_data').attr('checked') ? 1 : 0;
                var expired_tag = $('#popView-expired_tag').attr('checked') ? 1 : 0;
                if ($('#popView-selectAction').val() == 'duplicateBuild') {
                    $.post('./add', 

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
                         "demo_data": demo_data,
                         "expired_tag": expired_tag
                         },

                         function(data){
                            $("#popupViewBuild").modal("hide");
                            window.location.reload(true);
                         }
                    );
                } else if ($('#popView-selectAction').val() == 'editBuild'){
                    $.post('./updatebuild', 

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
                         "demo_data": demo_data,
                         "expired_tag": expired_tag
                         },

                         function(data){
                            $("#popupViewBuild").modal("hide");
                            if (data && data['task_id']) {
                                var tr_id = data['task_id'];
                                $('#' + tr_id).html(tr_render(data));
                                buildListEventBind();
                            }

                         }
                    );
                }
            });
        }

        buildListEventBind();

		$('#mailToAdmin').click(function(){
				$('#popView-MailFrom').val(""),
				$('#popView-MailSubject').val("");
				$('#popView-MailMessage').val("");
		});

		$('#popView-Send').click( function(){
			if ($('#popView-sendMailForm').valid()) {
				$.post('./sendmail',
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

                        if ($('#build_status_' + data[x].task_id).text() != data[x].status) {
                            $('#buildList-' + data[x].task_id).attr("disabled", "disabled");
                            $('#build_status_' + data[x].task_id).text(data[x].status);
                            $('#build_status_' + data[x].task_id).attr("class", data[x].status);
                            
                            //Disable the edit button
                            $('#editList-' + data[x].task_id).attr("disabled", "disabled");
							$('#buildListRemove-' + data[x].task_id).attr("disabled", "disabled");
                        }
                        builder.hasRunningTask = true;
                    
					}
                    $('td[name="list_status"].Running, td[name="list_status"].InQueue').each(function(i, domEle) {
						var task_id = $(domEle).parent().attr("id"); 
                        if (task_id_list.indexOf(task_id) == -1) {
							$('#buildList-' + task_id).removeAttr("disabled", "disabled");
							$('#build_status_' + task_id).text("Available");
							$('#build_status_' + task_id).attr("class", "Available");
							$('#editList-' + task_id).removeAttr("disabled");
							$('#buildListRemove-' + task_id).removeAttr("disabled");
                        }
                    });
                
                    var length = $('td[name="list_status"].Running, td[name="list_status"].InQueue').length;
                    if (length != window.favicon_len) {
                        favicon.badge(data.length);
                        window.favicon_len;
                    }
                    /*
					if (task_id_list.length == 0 &&  builder.hasRunningTask == true){
						window.location.reload()
					}
                    */
					
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


        var builds_render = function (builds, perPage) {
            var renderBody = "";

            for(var index = 0; index < builds.length; index ++) {
                renderBody += build_render(builds[index]);

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

                $("#buildList-tbody").html(builds_render(builds_data["builds"], perPage));
                $("#buildList-pageNum-link").text(pageNum + " of " + pageCount);
                $("#buildList-pageNum").val(pageNum);
                $("#buildList-totalPage").val(pageCount);

                buildListEventBind();

             })
             .fail(function(jqxhr, textStatus, error){
                 console.log( "Request Failed: " + textStatus + "," + error);
             });
        }

        function executeFullSearch() {
            var q = encodeURIComponent($("#searchForm-query").val().trim());
            var queryURL = "./searchbuild";
            if (_.isNull(q.match(/^["]/)) && q.match(/[-\_\s]/)) {
                q = '"' + q + '"';
            }

            renderBuildList(q, queryURL, 1);
        }
        
        $("#searchForm-query").on('keyup', _.debounce(executeFullSearch, 500, false));
        /*

        $("#searchForm-query").keyup(function(){
            var q = encodeURIComponent($(this).val().trim());
            var queryURL = "./searchbuild";

            renderBuildList(q, queryURL, 1);
        });
        */

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
            if (parseInt($("#buildList-totalPage").val()) > 1 && parseInt($("#buildList-pageNum").val()) < parseInt($("#buildList-totalPage").val())) {
                var q = $("#searchForm-query").val();
                var queryURL = "./searchbuild";

                renderBuildList(q, queryURL, parseInt($("#buildList-pageNum").val()) + 1);

                $("#buildList-firstPage").removeClass("disabled");
                $("#buildList-firstPage").addClass("active");
                $("#buildList-prePage").removeClass("disabled");
                $("#buildList-prePage").addClass("active");
            }

            if (parseInt($("#buildList-pageNum").val()) == parseInt($("#buildList-totalPage").val() - 1)) {
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

                $("#buildList-nextPage").removeClass("active");
                $("#buildList-nextPage").addClass("disabled");
                $("#buildList-lastPage").removeClass("active");
                $("#buildList-lastPage").addClass("disabled");

                $("#buildList-firstPage").removeClass("disabled");
                $("#buildList-firstPage").addClass("active");
                $("#buildList-prePage").removeClass("disabled");
                $("#buildList-prePage").addClass("active");
            }
        });

        $("#addBuildForm").submit(function(event) {
            var self = this;
            event.preventDefault();

            if ($(self).valid()) {
                    var styleguide_repo = $('#add-styleguide_repo').val() == undefined ? "" : $('#add-styleguide_repo').val(); 
                    var styleguide_branch = $('#add-styleguide_repo').val() == undefined ? "" : $('#add-styleguide_branch').val();
                    var data = {
                         "repos": $('#add-repos').val(),
                         "branch": $('#add-branch').val(), 
                         "version": $('#add-version').find(":selected").val(), 
                         "author": $('#add-author').val(),
                         "styleguide_repo": styleguide_repo,
                         "styleguide_branch": styleguide_branch,
                         "sidecar_repo": $('#add-sidecar_repo').val(),
                         "sidecar_branch": $('#add-sidecar_branch').val()
                         };
                    $.post(
                        './add', 
                        data
                    )
                    .done(function(build) {
                        build["username"] = get_username(build["author"]);
                        var new_build = build_render(build);

                        $("#buildList-tbody").prepend(new_build);
                        buildListEventBind();
                        $("#mapped_version").hide();
                        $("#add-version").val("blank");
                        alert("Add a new build successfully!");
                        
                    })
                    .fail(function() {
                        alert("Failed to add a new build, please contact admin or retry!");
                    });
            } else {
                console.log("! form is not validate for submit");
            }
        });

});
