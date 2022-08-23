from configparser import ConfigParser


def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser["postgresql"] = {
        "host": "localhost", "database": "BDD_Artistique", "user": "postgres", "password": "r3m1_1995"
    }

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db
