from paikkala.models import Zone


def read_csv(infp, separator=','):
    headers = None
    for line in infp:
        line = line.strip().split(separator)
        if not headers:
            headers = line
            continue
        yield dict(zip(headers, line))


def read_csv_file(filename, separator=','):
    with open(filename, encoding='utf-8') as infp:
        yield from read_csv(infp, separator)


def import_zones(csv_list):
    zones = {}
    for r_dict in csv_list:
        zone = zones.get(r_dict['zone'])
        if not zone:
            zone = zones[r_dict['zone']] = Zone.objects.create(name=r_dict['zone'])
        row = zone.rows.create(
            start_number=int(r_dict['start']),
            end_number=int(r_dict['end']),
            name=int(r_dict['row']),
        )
        assert row.capacity > 0
    return list(zones.values())
