from dmigrations.mysql import migrations as m
import datetime
migration = m.Migration(sql_up=["""
    CREATE TABLE `broadcast_alert` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `author_id` integer NOT NULL,
        `message` varchar(200) NOT NULL,
        `date_created` datetime NOT NULL
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `broadcast_alert` ADD CONSTRAINT author_id_refs_id_7122094b FOREIGN KEY (`author_id`) REFERENCES `auth_user` (`id`);
""", """
    CREATE TABLE `broadcast_message` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `title` varchar(100) NOT NULL,
        `content` longtext NOT NULL,
        `start_date` datetime NOT NULL,
        `end_date` datetime NULL,
        `ack_req` bool NOT NULL,
        `enabled` bool NOT NULL
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8
    ;
""", """
    CREATE TABLE `broadcast_log` (
        `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `user_id` integer NOT NULL,
        `message_id` integer NOT NULL,
        `acked` bool NOT NULL
    ) ENGINE=MyISAM DEFAULT CHARSET=utf8
    ;
""", """
    ALTER TABLE `broadcast_log` ADD CONSTRAINT user_id_refs_id_228b3541 FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
""", """
    ALTER TABLE `broadcast_log` ADD CONSTRAINT message_id_refs_id_3588db7c FOREIGN KEY (`message_id`) REFERENCES `broadcast_message` (`id`);
"""], sql_down=["""
    DROP TABLE `broadcast_log`;
""", """
    DROP TABLE `broadcast_message`;
""", """
    DROP TABLE `broadcast_alert`;
"""])
