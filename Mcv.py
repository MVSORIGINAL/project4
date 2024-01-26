from time import time


def monitor(func):
    def wrap_func(*args, **kwargs):
        t1 = time()
        try:
            result = func(*args, **kwargs)
        except:
            print(f'Function {func.__name__!r} executed in {(time() - t1):.16f}s')
            return
        print(f'Function {func.__name__!r} executed in {(time() - t1):.16f}s')
        return result

    return wrap_func


Game = object
value_of_cell = []
constraint_on_cell = []
order_domain_values = []


@monitor
def mcv_solve(game):
    global Game
    global value_of_cell
    global order_domain_values
    global constraint_on_cell
    Game = game
    value_of_cell = []
    constraint_on_cell = []
    order_domain_values = []

    for i in range(9):
        row = []
        constraint = []
        values = []
        for j in range(9):
            if [i, j] not in game.data_fills:
                row.append((0, 0))
                constraint.append([(-1, -1), (-1, -1)])
                values.append([1, 2, 3, 4, 5, 6, 7, 8, 9])
            else:
                row.append(0)
                constraint.append([(-1, -1), (-1, -1)])
                values.append([1, 2, 3, 4, 5, 6, 7, 8, 9])
        constraint_on_cell.append(constraint)
        value_of_cell.append(row)
        order_domain_values.append(values)

    for cell in game.data_totals:
        i, j = cell[2], cell[3]
        _x, _y = value_of_cell[i][j]
        if cell[1] == 'v':
            value_of_cell[i][j] = (_x, cell[0])
        else:
            value_of_cell[i][j] = (cell[0], _y)

    for cell in game.data_fills:
        x, y = cell[0], cell[1]
        xi, yi = get_left_consist(x, y)
        xj, yj = get_up_consist(x, y)
        constraint_on_cell[x][y] = [(xi, yi), (xj, yj)]

    # for row in value_of_cell:
    #     print(row)
    back_track(0)
    return Game.data_filled


def back_track(current_cell_index):
    global Game
    global value_of_cell
    global order_domain_values
    # print(Game.data_filled, ' data filed size')
    # print(Game.data_filled)
    if current_cell_index == -1:
        if Game.check_win():
            print(' ACCEPTED ')
            return True
        else:
            # print(len(Game.data_filled), len(Game.data_fills))
            # print(' FAILED ')
            # print_mp()
            return False
    current_cell = Game.data_fills[current_cell_index]
    domain = order_domain_values[current_cell[0]][current_cell[1]].copy()
    for i in domain:
        # print(" ********************* ")
        value_of_cell[current_cell[0]][current_cell[1]] = i
        if update_filled_sum_value(current_cell[0], current_cell[1]):
            # print(" ****** ++++++++++++++++++++++++++++++++++")
            Game.data_filled.append([current_cell[0], current_cell[1], i])
            update_order_domain_values(current_cell[0], current_cell[1], i, True)
            if back_track(get_next_unassigned_variable()):
                return True
            # Game.data_filled.remove([current_cell[0], current_cell[1], i])
            Game.data_filled.pop()
            update_order_domain_values(current_cell[0], current_cell[1], i, False)
        value_of_cell[current_cell[0]][current_cell[1]] = 0
    return False


def column_sum(i, j):
    global Game
    global value_of_cell
    summ = 0
    cnt = 0
    while True:
        i += 1
        if i > 8 or isinstance(value_of_cell[i][j], tuple):
            break
        summ += value_of_cell[i][j]
        cnt += (value_of_cell[i][j] == 0)

    minn = ((cnt + 1) * cnt / 2)
    maxx = 45 - ((9 - cnt) * (9 - cnt + 1) / 2)

    return summ + minn, maxx + summ


def row_sum(i, j):
    global Game
    summ = 0
    cnt = 0
    while True:
        j += 1
        if j > 8 or isinstance(value_of_cell[i][j], tuple):
            break
        summ += value_of_cell[i][j]
        cnt += (value_of_cell[i][j] == 0)

    minn = ((cnt + 1) * cnt / 2)
    maxx = 45 - ((9 - cnt) * (9 - cnt + 1) / 2)
    return summ + minn, maxx + summ


def get_left_consist(i, j):
    global value_of_cell
    while True:
        j -= 1
        if isinstance(value_of_cell[i][j], tuple):
            return i, j


def get_up_consist(i, j):
    global value_of_cell
    while True:
        i -= 1
        if isinstance(value_of_cell[i][j], tuple):
            return i, j


def update_filled_sum_value(i, j):
    global Game
    global constraint_on_cell
    xi, yi = constraint_on_cell[i][j][0]
    xj, yj = constraint_on_cell[i][j][1]
    sum_min_row, sum_max_row = row_sum(xi, yi)
    sum_min_column, sum_max_column = column_sum(xj, yj)
    # print(sum_max_row, consistent_values[(xi, yi)][0], sum_min_row)
    # print(sum_max_column, consistent_values[(xj, yj)][1], sum_min_column)
    # print(' */* ')
    # print(sum_max_row >= consistent_values[(xi, yi)][0] >= sum_min_row and \
    #       sum_max_column >= consistent_values[(xj, yj)][1] >= sum_min_column
    #       )
    return sum_max_row >= value_of_cell[xi][yi][0] >= sum_min_row and \
           sum_max_column >= value_of_cell[xj][yj][1] >= sum_min_column


def update_order_domain_values(i, j, value, remove):
    global order_domain_values
    global Game
    xi, yi = constraint_on_cell[i][j][0]
    xj, yj = constraint_on_cell[i][j][1]
    if remove:
        yi = yi + 1
        while yi < 9 and not isinstance(value_of_cell[xi][yi], tuple):
            try:
                order_domain_values[xi][yi].remove(value)
            except:
                pass
            # print("Updating order domain value of :", (yi, yi), " ::: ", order_domain_values[(yi, yi)])
            yi = yi + 1

        xj = xj + 1
        while xj < 9 and not isinstance(value_of_cell[xj][yj], tuple):
            try:
                order_domain_values[xj][yj].remove(value)
            except:
                pass
            # print("Updating order domain value of :", (xj, yj), " ::: ", order_domain_values[(xj, yj)])
            xj = xj + 1

    else:
        yi = yi + 1
        while yi < 9 and not isinstance(value_of_cell[xi][yi], tuple):
            if value not in order_domain_values[xi][yi]:
                order_domain_values[xi][yi].append(value)
            # print("Updating order domain value of :", (yi, yi), " ::: ", order_domain_values[(yi, yi)])
            yi = yi + 1

        xj = xj + 1
        while xj < 9 and not isinstance(value_of_cell[xj][yj], tuple):
            if value not in order_domain_values[xj][yj]:
                order_domain_values[xj][yj].append(value)
            # print("Updating order domain value of :", (xj, yj), " ::: ", order_domain_values[(xj, yj)])
            xj = xj + 1

    return order_domain_values


def print_mp():
    global value_of_cell
    for i in range(9):
        for j in range(9):
            print(value_of_cell[i][j], end='\t')
        print()
    print(" ***************** ")


def get_next_unassigned_variable():
    global Game
    global value_of_cell
    constraint = 100
    index = -1
    for i in range(len(Game.data_fills)):
        pos = Game.data_fills[i]
        # print(order_domain_values[pos[0]][pos[1]])
        if value_of_cell[pos[0]][pos[1]] == 0:
            if constraint >= len(order_domain_values[pos[0]][pos[1]]):
                constraint = len(order_domain_values[pos[0]][pos[1]])
                index = i

    # print(index, constraint)

    return index