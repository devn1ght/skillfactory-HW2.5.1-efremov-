import random


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за пределы поля!"


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, bow, length, direction):
        self.bow = bow
        self.length = length
        self.direction = direction
        self.lives = length

    def dots(self):
        ship_dots = []
        for i in range(self.length):
            x, y = self.bow.x, self.bow.y

            if self.direction == 0:
                x += i
            elif self.direction == 1: 
                y += i

            ship_dots.append(Dot(x, y))

        return ship_dots


class Board:
    def __init__(self, hid=False):
        self.field = [["O"] * 6 for _ in range(6)]
        self.ships = []
        self.hid = hid
        self.live_ships = 7

    def add_ship(self, ship):
        for dot in ship.dots():
            if self.out(dot) or self.check_neighbours(dot):
                raise BoardOutException("Нельзя разместить корабль здесь")
        for dot in ship.dots():
            self.field[dot.y][dot.x] = "■"
            self.ships.append(dot)
            self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for dot in ship.dots():
            for dx, dy in near:
                cur = Dot(dot.x + dx, dot.y + dy)
                if not (self.out(cur)) and cur not in self.ships:
                    if verb:
                        self.field[cur.y][cur.x] = "."
                    self.ships.append(cur)

    def __str__(self):
        res = "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | {' | '.join(row)} |"
        return res

    def out(self, dot):
        return not ((0 <= dot.x < 6) and (0 <= dot.y < 6))

    def check_neighbours(self, dot):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for dx, dy in near:
            cur = Dot(dot.x + dx, dot.y + dy)
            if not self.out(cur) and self.field[cur.y][cur.x] == "■":
                return True

        return False

    def add_random_ship(self, length):
        direction = random.choice([0, 1])
        x = random.randint(0, 5)
        y = random.randint(0, 5)

        try:
            ship = Ship(Dot(x, y), length, direction)
            self.add_ship(ship)
            return True
        except BoardException:
            return False

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException("Выстрел за пределы поля!")

        if dot in self.ships:
            self.field[dot.y][dot.x] = "X"
            self.live_ships -= 1
            return True
        elif self.field[dot.y][dot.x] == "O":
            self.field[dot.y][dot.x] = "T"
            return False

        return None


class Player:
    def __init__(self, board):
        self.board = board

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                result = self.board.shot(target)
                if result is not None:
                    return result
            except BoardException as e:
                print(e)


class User(Player):
    def ask(self):
        while True:
            try:
                coords = input("Введите координаты выстрела (например, 1,1): ").split(',')
                if len(coords) != 2:
                    print("Введите две координаты через запятую!")
                    continue

                x, y = coords
                if not (x.isdigit() and y.isdigit()):
                    print("Введите числа!")
                    continue

                x, y = int(x), int(y)

                return Dot(x-1, y-1)
            except ValueError:
                print("Введите числа!")


class AI(Player):
    def ask(self):
        return Dot(random.randint(0, 5), random.randint(0, 5))


class Game:
    def __init__(self):
        self.human_board = Board()
        self.ai_board = Board(hid=True)
        self.human = User(self.ai_board)
        self.ai = AI(self.human_board)

    def random_board(self, board):
        ships = [
            Ship(Dot(0, 0), 3, 0),  
            ]

        for ship in ships:
            while True:
                try:
                    board.add_ship(ship)
                    break
                except BoardException:
                    pass

    def randomize_board(self, board):
        ships_lengths = [3, 2, 2, 1, 1, 1, 1]
        for length in ships_lengths:
            placed = False
            while not placed:
                placed = board.add_random_ship(length)

    def greet(self):
        print("-------------------")
        print("  Добро пожаловать  ")
        print("    в Морской Бой   ")
        print("-------------------")
        print("   Формат ввода:    ")
        print("  x, y (например, 1,1)")
        print("-------------------")

    def loop(self):
        num = 0
        while self.human_board.live_ships and self.ai_board.live_ships:
            print("-" * 20)
            print(f"Ход {num}")
            print("-" * 20)
            print("Доска игрока:")
            print(self.human_board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai_board)

            human_move_result = self.human.move()
            if human_move_result is not None:
                print(f"Игрок попал! Осталось живых кораблей: {self.ai_board.live_ships}")
            else:
                print("Игрок промахнулся!")

            if not self.ai_board.live_ships:
                break

            ai_move_result = self.ai.move()
            if ai_move_result is not None:
                print(f"Компьютер попал! Осталось живых кораблей: {self.human_board.live_ships}")
            else:
                print("Компьютер промахнулся!")

            num += 1

        if not self.human_board.live_ships:
            print("Компьютер победил!")
        else:
            print("Игрок победил!")

    def start(self):
        self.greet()
        self.randomize_board(self.human_board)
        self.randomize_board(self.ai_board)
        self.loop()


if __name__ == "__main__":
    game = Game()
    game.start()