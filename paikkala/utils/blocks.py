from collections import defaultdict


def get_per_program_blocks(program, zone):
    blocks_by_row_id = defaultdict(set)
    for block in program.blocks.filter(row__zone=zone):
        blocks_by_row_id[block.row_id] |= block.get_excluded_set()
    return blocks_by_row_id
