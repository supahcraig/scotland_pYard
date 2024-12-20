import csv

# we want to read in all the stops and build a distinct list of to/from (ignoring mode)
# then we will add an incognito mode to each to/from combo and add them back to the original file.

def inject_incognito_edges(stop_defs_file):
    edge_count = {}
    stop_list = []

    with open(stop_defs_file) as f:
        reader = csv.reader(f)
        next(reader)  # skip header row


        for mode_stop in reader:
            goes_from, goes_to, mode = int(mode_stop[0]), int(mode_stop[1]), mode_stop[2].strip()
            stop_list.append((goes_from, goes_to, mode))

            edge_count[(goes_from, goes_to)] = edge_count.get((goes_from, goes_to), 0) + 1

            if edge_count[(goes_from, goes_to)] == 1:
                stop_list.append((goes_from, goes_to, 'incognito'))

    # now sort them so you can find them in the raw data later
    mode_order = {'taxi': 0, 'bus': 1, 'underground': 2, 'ferry': 3, 'incognito': 4}

    sorted_stops = sorted(stop_list, key=lambda x: (x[0], mode_order[x[2]], x[1]))

    for s in sorted_stops:
        print(s)

    return s


if __name__ == '__main__':
    inject_incognito_edges('stop_defs.csv')

