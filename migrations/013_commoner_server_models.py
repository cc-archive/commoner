from dmigrations.mysql import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `server_trustedmetadata` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `relying_party_id` integer NOT NULL,
        `field_name` varchar(100) NOT NULL
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8
    ;
"""], sql_down=["""
    DROP TABLE `server_trustedmetadata`;
"""])
