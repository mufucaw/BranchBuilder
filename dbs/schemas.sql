create virtual table builds using fts4 (
    task_id text primary key,
    repos text,
    branch text,
    version text,
    author text,
    last_build_date text,
    start_time text,
    build_number integer,
    status text,
    deploy_status text,
    package_list text,
    upgrade_package integer default 0,
    styleguide_repo text,
    styleguide_branch text,
    sidecar_repo text,
    sidecar_branch text,
    latin integer,
    demo_data integer,
    expired_tag text default 1
);
create table if not exists builds_status(
    id integer primary key,
    task_id text,
    status text,
    priority integer,
    kue_job_id text
);
create view if not exists builds_status_left_join_view as
    select a.task_id, a.author, a.build_number, a.branch, a.repos, a.version,
           a.styleguide_repo, a.styleguide_branch, a.sidecar_repo,
           a.sidecar_branch, a.last_build_date, a.demo_data, a.package_list,
           a.upgrade_package, a.latin, a.expired_tag, ifnull(b.status, a.status) as status
    from builds as a
    left join  builds_status as b
    on a.task_id=b.task_id;
;
