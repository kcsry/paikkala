from paikkala.models import Room, Zone


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


def import_zones(row_csv_list, qualifier_csv_list=(), default_room_name='Room', verbose=False):
    rooms_zones = {}

    def get_or_create_zone(data):
        room_name = data.get('room', default_room_name)
        zone_name = data['zone']
        rz_key = (room_name, zone_name)
        zone = rooms_zones.get(rz_key)
        if not zone:
            room, room_created = Room.objects.get_or_create(name=room_name)
            zone, zone_created = Zone.objects.get_or_create(room=room, name=zone_name)
            if verbose:
                if room_created:
                    print(f'Room {room} (id {room.id}) created')
                if zone_created:
                    print(f'Zone {zone} (id {zone.id}) created')
            rooms_zones[rz_key] = zone
        return zone

    for r_dict in row_csv_list:
        zone = get_or_create_zone(r_dict)
        row, row_created = zone.rows.get_or_create(
            name=r_dict['row'],
            defaults=dict(
                start_number=int(r_dict['start']),
                end_number=int(r_dict['end']),
            ),
        )
        if verbose and row_created:
            print(f'Row {row} (id {row.id}) created')

        assert row.capacity > 0

    for q_dict in qualifier_csv_list:
        zone = get_or_create_zone(q_dict)
        qual, qual_created = zone.seat_qualifiers.get_or_create(
            start_number=int(q_dict['start']),
            end_number=int(q_dict['end']),
            text=q_dict['text'],
        )
        if verbose and qual_created:
            print(f'Qualifier {qual} (id {qual.id}) created')

    return list(rooms_zones.values())
