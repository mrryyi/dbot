CREATE TABLE IF NOT EXISTS npc_names (
    id INTEGER PRIMARY KEY,
    name varchar(255) CHECK (name <> ''),
    taken BOOL DEFAULT 0,
    datetime_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    datetime_taken DATETIME NULL DEFAULT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_npc_names_name ON npc_names(name);