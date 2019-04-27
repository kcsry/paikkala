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


def import_zones(row_csv_list, qualifier_csv_list=(), default_room_name='Room'):
    rooms_zones = {}

    def get_or_create_room(data):
        room_name = data.get('room', default_room_name)
        zone_name = data['zone']
        rz_key = (room_name, zone_name)
        zone = rooms_zones.get(rz_key)
        if not zone:
            room, _ = Room.objects.get_or_create(name=room_name)
            zone = rooms_zones[rz_key] = Zone.objects.create(room=room, name=zone_name)
        return zone

    for r_dict in row_csv_list:
        zone = get_or_create_room(r_dict)
        row = zone.rows.create(
            start_number=int(r_dict['start']),
            end_number=int(r_dict['end']),
            name=int(r_dict['row']),
        )
        assert row.capacity > 0

    for q_dict in qualifier_csv_list:
        zone = get_or_create_room(q_dict)
        zone.seat_qualifiers.create(
            start_number=int(q_dict['start']),
            end_number=int(q_dict['end']),
            text=q_dict['text'],
        )

    return list(rooms_zones.values())
