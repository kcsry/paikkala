from django.core.exceptions import ValidationError


def parse_number_set(number_set):
    """
    Parse a number set string to a set of integers.

    The string is a comma-separated range of "atoms", which may be

    * A single value (`1`)
    * A range of values (`1-5`) separated with either a dash or double dots.

    and these may also be negated with a leading exclamation mark.

    >>> parse_number_set('1-5,8-9')
    {1, 2, 3, 4, 5, 8, 9}

    >>> parse_number_set('1-5,!4')
    {1, 2, 3, 5}

    >>> parse_number_set('1,2,3')
    {1, 2, 3}

    >>> sorted(parse_number_set('-1..-5'))
    [-5, -4, -3, -2, -1]

    """
    incl = set()
    excl = set()
    for atom in number_set.split(','):
        atom = atom.strip()
        if not atom:
            continue
        if atom.startswith('!'):
            dest = excl
            atom = atom[1:]
        else:
            dest = incl
        if '-' in atom[1:] or '..' in atom:
            start, end = [int(v) for v in atom.split(('..' if '..' in atom else '-'), 1)]
            if start > end:
                end, start = start, end
            dest.update(set(range(start, end + 1)))
        else:
            dest.add(int(atom))
    return incl - excl


def validate_number_set(number_set):
    try:
        return parse_number_set(number_set)
    except Exception as exc:
        raise ValidationError('number set: %s' % exc) from exc
