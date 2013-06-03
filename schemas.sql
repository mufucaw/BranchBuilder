create virtual table if not exists builds using fts4 (
    task_id integer primary key,
    repos text,
    branch text,
    version text,
    author text,
    last_build_date text,
    start_time text,
    build_number integer,
    status text,
    package_list text,
    upgrade_package integer default 0,
    styleguide_repo text,
    styleguide_branch text,
    sidecar_repo text,
    sidecar_branch text,
    latin integer,
    demo_data integer
);
create table if not exists build_configs(
    id integer primary key,
    version text,
    author text,
    build_config_content blob
);
create table if not exists builds_status(
    id integer primary key,
    task_id integer,
    status text,
    priority integer
);
create view if not exists builds_status_left_join_view as
    select a.task_id, a.author, a.build_number, a.branch, a.repos, a.version, a.author, a.styleguide_repo, a.styleguide_branch,
        a.sidecar_repo, a.sidecar_branch, a.last_build_date, ifnull(b.status, a.status) as status
    from builds as a
    left join  builds_status as b
    on a.task_id=b.task_id
;
create table if not exists deploys_status(
    id integer primary key,
    task_id integer,
    status text
);
create table if not exists od_deployer (
    id integer primary key,
    username text,
    version text,
    webroot text,
    status text,
    deploy_config text,
    last_deploy_date text
);
