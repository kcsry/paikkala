from paikkala.models import Zone, Room


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
    rooms_zones = {}
    for r_dict in csv_list:
        room_name = r_dict.get('room', 'Room')
        zone_name = r_dict['zone']
        rz_key = (room_name, zone_name)
        zone = rooms_zones.get(rz_key)
        if not zone:
            room, _ = Room.objects.get_or_create(name=room_name)
            zone = rooms_zones[rz_key] = Zone.objects.create(room=room, name=zone_name)
        row = zone.rows.create(
            start_number=int(r_dict['start']),
            end_number=int(r_dict['end']),
            name=int(r_dict['row']),
        )
        assert row.capacity > 0
    return list(rooms_zones.values())
