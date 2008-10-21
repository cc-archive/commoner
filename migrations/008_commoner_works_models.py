from dmigrations.mysql import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `works_registration` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `owner_id` integer NULL,
        `created` datetime NOT NULL,
        `updated` datetime NOT NULL
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `works_feed` (
        `registration_ptr_id` integer NOT NULL PRIMARY KEY,
        `url` varchar(255) NOT NULL,
        `license` varchar(255) NOT NULL
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `works_feed` ADD CONSTRAINT registration_ptr_id_refs_id_5711355c FOREIGN KEY (`registration_ptr_id`) REFERENCES `works_registration` (`id`);
""", """
    CREATE TABLE `works_work` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `registration_id` integer NOT NULL,
        `url` varchar(255) NOT NULL,
        `title` varchar(255) NOT NULL,
        `license_url` varchar(255) NOT NULL,
        `registered` datetime NOT NULL,
        `updated` datetime NOT NULL,
        `same_as_id` integer NULL
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `works_work` ADD CONSTRAINT registration_id_refs_id_1b6c0313 FOREIGN KEY (`registration_id`) REFERENCES `works_registration` (`id`);
""", """
    ALTER TABLE `works_work` ADD CONSTRAINT same_as_id_refs_id_4d40798b FOREIGN KEY (`same_as_id`) REFERENCES `works_work` (`id`);
""", """
    CREATE TABLE `works_constraint` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `work_id` integer NULL,
        `constraint` varchar(20) NOT NULL,
        `mode` varchar(20) NOT NULL,
        `var` varchar(255) NOT NULL
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `works_constraint` ADD CONSTRAINT work_id_refs_id_39fc2ac3 FOREIGN KEY (`work_id`) REFERENCES `works_work` (`id`);
""", """
    ALTER TABLE `works_registration` ADD CONSTRAINT owner_id_refs_id_25345264 FOREIGN KEY (`owner_id`) REFERENCES `auth_user` (`id`);
"""], sql_down=["""
    DROP TABLE `works_constraint`;
""", """
    ALTER TABLE `works_work` DROP FOREIGN KEY same_as_id_refs_id_4d40798b;
""", """
    DROP TABLE `works_work`;
""", """
    DROP TABLE `works_feed`;
""", """
    DROP TABLE `works_registration`;
"""])
