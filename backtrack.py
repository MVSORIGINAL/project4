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
def simple_solve(game):
    """Solves a Kakuro puzzle using a simple backtracking algorithm."""

    # Initialize data structures for cells, constraints, and possible values
    cell_values = [[(0, 0) for _ in range(9)] for _ in range(9)]
    cell_constraints = [[[(-1, -1), (-1, -1)] for _ in range(9)] for _ in range(9)]
    cell_possible_values = [[[1, 2, 3, 4, 5, 6, 7, 8, 9] for _ in range(9)] for _ in range(9)]

    # Populate initial values and constraints based on game data
    for cell in game.data_totals:
        i, j = cell[2], cell[3]
        if cell[1] == 'v':
            cell_values[i][j] = (0, cell[0])
        else:
            cell_values[i][j] = (cell[0], 0)

    for cell in game.data_fills:
        x, y = cell[0], cell[1]
        left_constraint, up_constraint = get_left_consist(x, y), get_up_consist(x, y)
        cell_constraints[x][y] = [left_constraint, up_constraint]

    # Solve using backtracking
    if back_track(0):
        return game.data_filled
    else:
        return None  # Indicate no solution found
    
def back_track(current_cell_index, cell_values, cell_possible_values, game):
    """Recursively explores possible solutions using backtracking."""

    if current_cell_index == len(game.data_fills):
        return game.check_win()  # Return True if puzzle is solved

    row, col = game.data_fills[current_cell_index]
    for value in cell_possible_values[row][col]:
        cell_values[row][col] = value

        if update_filled_sum_value(row, col, cell_values):
            game.data_filled.append([row, col, value])
            update_order_domain_values(row, col, value, True, cell_possible_values)

            if back_track(current_cell_index + 1, cell_values, cell_possible_values, game):
                return True

            game.data_filled.pop()
            update_order_domain_values(row, col, value, False, cell_possible_values)

    cell_values[row][col] = 0  # Reset cell value if backtracking
    return False


def column_sum(i, j, cell_values):
    """Calculates the minimum and maximum possible sums for a column, starting from a given cell."""

    summ = 0
    cnt = 0
    while i < 9 and not isinstance(cell_values[i][j], tuple):
        summ += cell_values[i][j]
        cnt += 1 if cell_values[i][j] == 0 else 0  # Count only empty cells
        i += 1

    min_possible_sum = summ + (cnt * (cnt + 1)) // 2  # Precalculate to avoid repetition
    max_possible_sum = summ + 45 - ((9 - cnt) * (9 - cnt + 1)) // 2

    return min_possible_sum, max_possible_sum


def row_sum(i, j, cell_values):
    """Calculates the minimum and maximum possible sums for a row, starting from a given cell."""

    summ = 0
    cnt = 0
    while j < 9 and not isinstance(cell_values[i][j], tuple):
        summ += cell_values[i][j]
        cnt += 1 if cell_values[i][j] == 0 else 0  # Count only empty cells
        j += 1

    min_possible_sum = summ + (cnt * (cnt + 1)) // 2  # Precalculate to avoid repetition
    max_possible_sum = summ + 45 - ((9 - cnt) * (9 - cnt + 1)) // 2

    return min_possible_sum, max_possible_sum


def get_left_consist(i, j, cell_values):
    """Finds the coordinates of the leftmost constraint cell in the same row."""

    while j >= 0 and not isinstance(cell_values[i][j], tuple):
        j -= 1

    return i, j + 1  # Return coordinates of the cell to the right of the constraint



def get_up_consist(i, j, cell_values):
    """Finds the coordinates of the topmost constraint cell in the same column."""

    while i >= 0 and not isinstance(cell_values[i][j], tuple):
        i -= 1

    return i + 1, j  # Return coordinates of the cell below the constraint



def update_filled_sum_value(i, j, cell_values, cell_constraints, cell_possible_values):
    """Checks if the current value assignments satisfy row and column constraints."""

    row_constraint, col_constraint = cell_constraints[i][j]
    row_sum_min, row_sum_max = row_sum(row_constraint[0], row_constraint[1], cell_values)
    col_sum_min, col_sum_max = column_sum(col_constraint[0], col_constraint[1], cell_values)

    row_value = cell_values[row_constraint[0]][row_constraint[1]][0]
    col_value = cell_values[col_constraint[0]][col_constraint[1]][1]

    is_valid = (
        row_sum_max >= row_value >= row_sum_min
        and col_sum_max >= col_value >= col_sum_min
    )

    if not is_valid:
        # Remove invalid values from possible values
        cell_possible_values[row_constraint[0]][row_constraint[1]].remove(row_value)
        cell_possible_values[col_constraint[0]][col_constraint[1]].remove(col_value)

    return is_valid


def update_order_domain_values(i, j, value, remove, cell_possible_values):
    """Updates the possible values of cells in the same row or column after a value assignment."""

    row_constraint, col_constraint = cell_constraints[i][j]

    # Update row values
    for yi in range(row_constraint[1] + 1, 9):
        if not isinstance(cell_values[row_constraint[0]][yi], tuple):
            if remove:
                cell_possible_values[row_constraint[0]][yi].remove(value)
            else:
                cell_possible_values[row_constraint[0]][yi].append(value)

    # Update column values
    for xj in range(col_constraint[0] + 1, 9):
        if not isinstance(cell_values[xj][col_constraint[1]], tuple):
            if remove:
                cell_possible_values



def print_mp(cell_values):
    """Prints the puzzle grid in a clear and formatted way."""

    print("-" * 27)  # Visual separator for the grid
    for row in cell_values:
        print("| " + " | ".join(str(value) if value else " " * 2 for value in row) + " |")
    print("-" * 27)  # Visual separator for the grid

