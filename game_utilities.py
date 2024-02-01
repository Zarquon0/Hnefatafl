from functools import reduce
from copy import copy
import operator

#CONSTANTS
BOARD_DIM = 11
NUM_TYPE_MAP = {
    '0' : 'blank',
    '1' : 'invader',
    '2' : 'defender',
    '3' : 'king'
}
SPEC_IDCS = [(int((BOARD_DIM-1)/2), int((BOARD_DIM-1)/2)), (0,0), (0,BOARD_DIM-1), (BOARD_DIM-1, 0), (BOARD_DIM-1, BOARD_DIM-1)]
BOARD_IDCS = range(0, BOARD_DIM)

#GENERAL HELPERS
def valid_idcs(idcs):
    return idcs[0] in BOARD_IDCS and idcs[1] in BOARD_IDCS

def adj_abstract(dirs):
    def func(idcs, board):
        adj_idcs = map(lambda dir: (idcs[0] + dir[0], idcs[1] + dir[1]), dirs)
        fadj_idcs = filter(valid_idcs, adj_idcs)
        return list(map(lambda idcs: (board[idcs[0]][idcs[1]], idcs), fadj_idcs))
    return func

def adj_tls(idcs, board):
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    return adj_abstract(dirs)(idcs, board)

def neighbor_tls(idcs, board):
    dirs = [(-1,0),(0,1),(1,0),(0,-1)]
    return adj_abstract(dirs)(idcs, board)

def vec_add(v1, v2, op=operator.add):
    if len(v1) != len(v2):
        raise Exception("Vectors not same length")
    return tuple([op(v1[i], v2[i]) for i in range(len(v1))])

#UTILITY HELPERS
def find_loops(strt_idcs, board):
    def inner_find_loops(entry, seen, first=False):
        if not first and entry[1] == strt_idcs:
            return [[]]
        elif entry[0] == "1" and entry[1] not in seen:
            seen.append(entry[1])
            adj_pc_lookup = adj_tls(entry[1], board)
            loops = reduce(lambda cum, ent: cum + list(inner_find_loops(ent, copy(seen))), adj_pc_lookup, [])
            for loop in loops:
                loop.append(entry[1])
            return loops
        else:
            return []
    return list(filter(lambda loop: len(loop) > 3, inner_find_loops(('1', strt_idcs), [], first=True)))

def contains_all(loop, board):
    row_dict = {}
    for i in BOARD_IDCS:
        row_dict[str(i)] = []
    for idcs in loop:
        row_dict[str(idcs[0])].append(idcs[1])
        row_dict[str(idcs[0])].sort()
    for i in BOARD_IDCS:
        for n in BOARD_IDCS:
            pc = board[i][n]
            loop_idcs = row_dict[str(i)]
            if pc in ['2', '3'] and (len(loop_idcs) < 2 or n < loop_idcs[0] or n > loop_idcs[-1]):
                return False
    return True

def encirclement(move, board):
    to_idcs = move['end']
    loops = find_loops(to_idcs, board)
    for loop in loops:
        if contains_all(loop, board):
            return True
    return False

def no_moves(move, board):
    side = ['1'] if move['type'] in ['2','3'] else ['2', '3']
    for i in BOARD_IDCS:
        for n in BOARD_IDCS:
            pc = board[i][n]
            if pc in side:
                for tl in neighbor_tls((i,n), board):
                    if tl[0] == '0' and not (pc != '3' and tl[1] in SPEC_IDCS):
                        return False
    return True

def king_capd(move):
    for pair in move['caps']:
        if pair[0] == '3':
            return True
    return False

def king_escapd(move):
    return move['type'] == '3' and move['end'] in SPEC_IDCS[1:]

def valid_choice(move, board, game, player):
    side = ['2','3'] if game.players[game.king] == player else ['1']
    frm = move['start']
    pc = board[frm[0]][frm[1]]
    return game.players[game.turn] == player and pc in side and move['type'] == pc

def valid_movement(move, board):
    frm = move['start']
    to = move['end']
    if to[0] - frm[0] == 0:
        chk_idcs = [(frm[0], h_idx) for h_idx in range(min(frm[1], to[1]), max(frm[1], to[1])+1)]
    elif to[1] - frm[1] == 0:
        chk_idcs = [(v_idx, frm[1]) for v_idx in range(min(frm[0], to[0]), max(frm[0], to[0])+1)]
    else:
        return False
    chk_idcs.remove(frm)
    for idcs in chk_idcs:
        if board[idcs[0]][idcs[1]] != '0':
            return False
    if to in SPEC_IDCS and move['type'] != '3':
        return False
    return True

def tri_surrounded(idcs, board):
    nbors = neighbor_tls(idcs, board)
    cnt = 0
    for tl in nbors:
        if tl[0] == '1':
            cnt += 1
    return cnt == 3

def valid_captures(move, board):
    cap_idcs = list(map(lambda cap: cap[1], move['caps']))
    to_idcs = move['end']
    ptntl_caps = neighbor_tls(to_idcs, board)
    side = ['1'] if move['type'] == '1' else ['2', '3']
    for cap in cap_idcs:
        is_valid = False
        for p_cap in ptntl_caps:
            if p_cap[1] == cap and p_cap[0] not in side and p_cap[0] != 0:
                if p_cap[0] == '3':
                    if tri_surrounded(p_cap[1], board):
                        is_valid = True
                        break
                    else:
                        continue
                dir = vec_add(p_cap[1], to_idcs, op=operator.sub)
                swich_idcs = vec_add(p_cap[1], dir)
                if valid_idcs(swich_idcs): 
                    swich_pc = board[swich_idcs[0]][swich_idcs[1]]
                    if swich_pc in side or (swich_idcs in SPEC_IDCS and swich_pc == '0'):
                        is_valid = True
                        break
        if not is_valid:
            return False
    return True
    
#UTILITIES
def prep_board(board):
    html_board = []
    for i in range(len(board)):
        row = board[i]
        for n in range(len(row)):
            tile = row[n]
            type = NUM_TYPE_MAP[tile]
            piece_class = None
            if type != 'blank':
                piece_class = f'piece {type}'
            tile_class = 'tile'
            if (i,n) in SPEC_IDCS:
                tile_class += ' spec_tile'
            else:
                tile_class += ' norm_tile'
            html_board.append((f'tile{i}{n}', (tile_class, piece_class)))
    return html_board

def detect_victory(move, board):
    return encirclement(move, board) or no_moves(move, board) or king_escapd(move) or king_capd(move)

def validate_move(move, game, player):
    board = game.retrieve_board()
    return valid_choice(move, board, game, player) and valid_movement(move, board) and valid_captures(move, board)