CREATE DATABASE IF NOT EXISTS hash_framework;
USE hash_framework;

CREATE TABLE tasks (
    id BIGINT AUTO_INCREMENT NOT NULL,

    max_threads INT NOT NULL,
    priority INT NOT NULL,

    name VARCHAR(1024) UNIQUE NOT NULL,
    algo VARCHAR(64) NOT NULL,
    started DATETIME NOT NULL,

    PRIMARY KEY(id)
);

CREATE TABLE jobs (
    id BIGINT AUTO_INCREMENT NOT NULL,

    kernel VARCHAR(64) NOT NULL,
    algo VARCHAR(64) NOT NULL,
    args TEXT NOT NULL,
    result_table VARCHAR(64) NOT NULL,

    PRIMARY KEY(id)
);

CREATE TABLE hosts (
    id BIGINT AUTO_INCREMENT NOT NULL,

    ip VARCHAR(128) NOT NULL,
    hostname VARCHAR(512) NOT NULL,

    cores SMALLINT NOT NULL,
    memory BIGINT NOT NULL,
    disk BIGINT NOT NULL,

    registerred DATETIME NOT NULL,
    last_seen DATETIME NOT NULL,

    version VARCHAR(512) NOT NULL,

    PRIMARY KEY(id)
);

CREATE TABLE host_metadata (
    host_id BIGINT NOT NULL REFERENCES hosts(id),
    name VARCHAR(512) NOT NULL,
    value TEXT NOT NULL
);

CREATE TABLE assigns (
    task_id BIGINT NOT NULL REFERENCES tasks(id),
    job_id BIGINT NOT NULL REFERENCES jobs(id),
    owner BIGINT NOT NULL REFERENCES hosts(id),

    state INT NOT NULL,

    start_time DATETIME,
    compile_time DATETIME,
    run_time DATETIME,
    finalize_time DATETIME,
    checked_back DATETIME
);

CREATE TABLE results (
    job_id BIGINT NOT NULL REFERENCES jobs(id),
    result_table VARCHAR(64) NOT NULL,
    result_id BIGINT NOT NULL
);
