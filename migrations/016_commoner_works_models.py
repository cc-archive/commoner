from dmigrations.mysql import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `works_feed` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `registration_id` integer NOT NULL,
        `url` varchar(255) NOT NULL,
        `license_url` varchar(255) NOT NULL,
        `cron_enabled` bool NOT NULL,
        `consumed` datetime NOT NULL
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8
    ;
"""], sql_down=["""
    DROP TABLE `works_feed`;
"""])
