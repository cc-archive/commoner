from dmigrations.mysql import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `registration_partialregistration` (
        `key` varchar(40) NOT NULL PRIMARY KEY,
        `last_name` varchar(30) NOT NULL,
        `first_name` varchar(30) NOT NULL,
        `email` varchar(75) NOT NULL,
        `complete` bool NOT NULL,
        `transaction_id` varchar(255) NULL,
        `user_id` integer NULL
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8
    ;
""", """
    -- The following references should be added but depend on non-existent tables:
""", """
    -- ALTER TABLE `registration_partialregistration` ADD CONSTRAINT user_id_refs_id_4708d51a FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `registration_partialregistration`;
"""])
