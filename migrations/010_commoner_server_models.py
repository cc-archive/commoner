from dmigrations.mysql import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `server_trustedrelyingparty` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `user_id` integer NOT NULL,
        `root` varchar(255) NOT NULL
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8
    ;
""", """
    -- The following references should be added but depend on non-existent tables:
""", """
    -- ALTER TABLE `server_trustedrelyingparty` ADD CONSTRAINT user_id_refs_id_564e9017 FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `server_trustedrelyingparty`;
"""])
