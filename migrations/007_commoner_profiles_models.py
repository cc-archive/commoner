from dmigrations.mysql import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `profiles_commonerprofile` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `user_id` integer NOT NULL UNIQUE,
        `nickname` varchar(255) NOT NULL,
        `photo` varchar(100) NULL,
        `homepage` varchar(255) NOT NULL,
        `location` varchar(255) NOT NULL,
        `story` longtext NOT NULL,
        `created` datetime NOT NULL,
        `updated` datetime NOT NULL,
        `expires` datetime NOT NULL
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8
    ;
""", """
    -- The following references should be added but depend on non-existent tables:
""", """
    -- ALTER TABLE `profiles_commonerprofile` ADD CONSTRAINT user_id_refs_id_7ae12c52 FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `profiles_commonerprofile`;
"""])
