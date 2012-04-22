CREATE TABLE programs (
        id            VARCHAR(40)         NOT NULL PRIMARY KEY,
        code          TEXT                NOT NULL,
        date_created  TIMESTAMP           DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
