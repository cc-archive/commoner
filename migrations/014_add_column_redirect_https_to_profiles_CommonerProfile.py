from dmigrations.mysql import migrations as m
import datetime
migration = m.AddColumn('profiles', 'CommonerProfile', 'redirect_https', 'bool NOT NULL')
