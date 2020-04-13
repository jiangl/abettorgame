#!/usr/bin/env python
import sys, getopt
import yaml
import logging
import psycopg2
import argparse
import re


log = logging.getLogger(__name__)

def connect_from_yaml(config_file_name):
    with open(config_file_name, 'r') as f:
        vals = yaml.load(f)

    if not ('host' in vals.keys() and
            'user' in vals.keys() and
            'password' in vals.keys() and
            'database' in vals.keys() and
            'port' in vals.keys()):
        raise Exception('Bad config file: ' + config_file_name)

    return get_connection(vals['database'], vals['user'],
                          vals['host'], vals['port'],
                          vals['password'])

def get_connection(db, user, host, port, password):
    connection = psycopg2.connect(user=user,
                                  password=password,
                                  host=host,
                                  port=port,
                                  database=db)
    cursor = connection.cursor()
    return connection, cursor

def insert_csv_values(cursor, filename):
    # Test queries
    # cursor.execute("INSERT INTO maingame_userrole (name) VALUES (%s)", ('MANUAL_TEST',))
    # cursor.execute("INSERT INTO maingame_user (first_name,last_name,join_date,email,phone_number) VALUES (%s, %s, %s, %s, %s)",
    #                ("MANUAL_LISA", '', '2020-04-12 14:47:57-04', "feefifofisa@gmail.com", None))
    template_sql = "INSERT INTO {table} ({keys}) VALUES ("

    with open(filename, 'r') as f:
        tables = yaml.load(f)
    for table in tables:
        keys = tables[table]['header']
        keys_string = ','.join(keys)
        mod_sql = template_sql.format(table=table, keys=keys_string)
        mod_sql = mod_sql + ', '.join(['%s']* len(keys)) + ')'

        bulk_values = tables[table]['data']

        for row in bulk_values:
            cursor.execute(mod_sql, tuple(row))

def main(datafile, config="config.yaml"):
    connection = None

    try:
        connection, cursor = connect_from_yaml(config)
        log.info("Connected to PostgreSQL database.")
        insert_csv_values(cursor, datafile)
        connection.commit()
        log.info("Successfully inserted values.")
    except:
        log.exception("Something fucked up.")
        return None
    finally:
        if (connection):
            cursor.close()
            connection.close()

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Seed the DB')
    parser.add_argument('-d', '--datafile', type=str, nargs='?',
                        help='The datafile to load the DB with, yaml format',
                        required=True)
    args = parser.parse_args()
    main(args.datafile)