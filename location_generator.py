import decimal
import random
import sys


def gen_random_position():
    latitude = decimal.Decimal('%d.%d' % (random.randint(-90, 90), random.randint(0, 99999)))
    longitude = decimal.Decimal('%d.%d' % (random.randint(-180, 180), random.randint(0, 99999)))

    return (latitude, longitude)


def write_sql_data(filename, app, model, num):
    file = open(filename, 'w')
    for i in range(num):
        position = gen_random_position()
        file.write("INSERT INTO %s_%s (latitude, longitude) VALUES ('%.5f', '%.5f');\n" % (app, model, position[0], position[1]))
    file.close()

if len(sys.argv) < 2:
    sys.stderr.write('Usage: sys.argv[0] <filename> <appname> <modelname> <recordnum>')
    sys.exit(1)

write_sql_data(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
