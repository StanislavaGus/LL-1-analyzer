from collections import defaultdict
import random
# Новая грамматика
productions = [
    ("S", "TA", "Eurasia"),
    ("A", "+T", "Africa"),
    ("A", "", "North America"),
    ("T", "aB", "South America"),
    ("B", "[S]", "Australia"),
    ("B", "", "Antarctica")
]

# Преобразуем грамматику в подходящую структуру
grammar = defaultdict(list)
for lhs, rhs, _ in productions:
    grammar[lhs].append(list(rhs))

terminals = ['a', '+', '[', ']', 'ϵ', '$']
non_terminals = set(grammar.keys())

FIRST = {}
FOLLOW = {}
lookup_table = {nt: [-1] * len(terminals) for nt in non_terminals}


def compute_first(symbol):
    if symbol in FIRST:
        return FIRST[symbol]

    FIRST[symbol] = set()

    if symbol not in grammar:  # терминал
        FIRST[symbol].add(symbol)
    else:
        for production in grammar[symbol]:
            for token in production:
                result = compute_first(token)
                FIRST[symbol].update(result - {'ϵ'})
                if 'ϵ' not in result:
                    break
            else:
                FIRST[symbol].add('ϵ')

    return FIRST[symbol]


def compute_follow(symbol):
    if symbol not in FOLLOW:
        FOLLOW[symbol] = set()

    if symbol == 'S':
        FOLLOW[symbol].add('$')

    productions = {nt: prods for nt, prods in grammar.items() if any(symbol in prod for prod in prods)}

    for nt, prods in productions.items():
        for prod in prods:
            if symbol in prod:
                following_symbols = prod[prod.index(symbol) + 1:]
                if following_symbols:
                    first_of_following = set()
                    for next_symbol in following_symbols:
                        first_of_following.update(compute_first(next_symbol))
                        if 'ϵ' not in compute_first(next_symbol):
                            break
                    else:
                        FOLLOW[symbol].update(compute_follow(nt))
                    FOLLOW[symbol].update(first_of_following - {'ϵ'})
                else:
                    if nt != symbol:
                        FOLLOW[symbol].update(compute_follow(nt))

    return FOLLOW[symbol]


def build_lookup_table():
    for index, (lhs, rhs, _) in enumerate(productions):
        first_rhs = set()
        if rhs == '':
            first_rhs.add('ϵ')
        else:
            for symbol in rhs:
                first_rhs.update(compute_first(symbol))
                if 'ϵ' not in compute_first(symbol):
                    break
            else:
                first_rhs.add('ϵ')

        for terminal in first_rhs:
            if terminal != 'ϵ':
                terminal_index = terminals.index(terminal)
                lookup_table[lhs][terminal_index] = index

        if 'ϵ' in first_rhs:
            for terminal in compute_follow(lhs):
                terminal_index = terminals.index(terminal)
                lookup_table[lhs][terminal_index] = index


for nt in grammar:
    compute_first(nt)
    compute_follow(nt)

build_lookup_table()

print("FIRST:")
for nt in non_terminals:
    print(f"{nt}: {FIRST[nt]}")

print("\nFOLLOW:")
for nt in non_terminals:
    print(f"{nt}: {FOLLOW[nt]}")

print("\nLookup Table:")
for nt, rules in lookup_table.items():
    print(f"{nt}: {rules}")


# Функция для проверки принадлежности строки данной грамматике
def parse(input_string):
    alphabet = terminals[:-2]  # Исключаем 'ϵ' и '$'

    # Проверка, что все символы из алфавита
    for char in input_string:
        if char not in alphabet:
            return False, ["Symbol not from alphabet"]

    semantic_actions = []
    my_stack = ['S']  # Начальный символ грамматики
    i = 0

    input_string += '$'

    while my_stack:
        top = my_stack.pop()

        if top in terminals:
            if top == input_string[i]:
                i += 1
            else:
                return False, []
        elif top in non_terminals:
            index = terminals.index(input_string[i])
            production_index = lookup_table[top][index]
            if production_index == -1:
                return False, []
            _, rhs, action = productions[production_index]
            for symbol in reversed(rhs):
                if symbol:
                    my_stack.append(symbol)
            semantic_actions.append(action)
        else:
            return False, []

    if i == len(input_string) - 1:
        return True, semantic_actions
    else:
        return False, []

def generate_string(start_symbol):
    result = start_symbol

    def has_nonterminals(s):
        return any(c in lookup_table for c in s)

    while has_nonterminals(result):
        for i, char in enumerate(result):
            if char in lookup_table:
                # Доступные продукции для текущего нетерминала
                available_productions = [index for index in lookup_table[char] if index != -1]
                if not available_productions:
                    continue  # Если нет доступных продукций, пропускаем

                # Выбор случайной продукции
                production_index = random.choice(available_productions)
                production = productions[production_index][1]

                # Замена нетерминала на его продукцию
                result = result[:i] + production + result[i+1:]
                break  # Останавливаемся после первой замены

    return result


# Пример использования
test_strings = [
    "a",          # правильная строка
    "a+a",        # правильная строка
    "a+a[a]",     # правильная строка
    "a+a[a+a]",   # правильная строка
    "a[a]",       # правильная строка
    "a[a]+a",     # правильная строка
    "a[a+a]",     # правильная строка
    "a[a+a]+a",   # правильная строка
    "a[a]+a[a]",  # правильная строка
    "a[a]+a[a+a]",# правильная строка
    "b",          # неправильная строка: символ не из алфавита
    "a+b*c",      # неправильная строка: символ не из алфавита
    "a[a)b]",     # неправильная строка: символ не из алфавита
    "+",          # неправильная строка: нельзя начинать с '+'
    "aa",         # неправильная строка: два 'a' подряд
    "a++a",       # неправильная строка: два '+' подряд
    "a[a+a]+",    # неправильная строка: отсутствует закрывающая скобка ']'
    "a+[]",       # неправильная строка: пустой скобочный блок
    "a[+a]"       # неправильная строка: открытие скобок сразу с '+'
]

print("\n\n")

while True:
    print("0 - print grammar\n"+
          "1 - print FIRST\n" +
          "2 - print FOLLOW\n" +
          "3 - lookup table\n" +
          "4 - check sentence\n"+
          "5 - generate string\n"+
          "6 - print examples of checking\n" +
          "7 - print examples of generating\n" +
          "8 - exit\n")
    choice = input("Choose option: ")

    if choice == '0':
        print("Grammar:")
        for p in productions:
            print(p)
        print("\n")

    elif choice == '1':
        print("FIRST:")
        for nt in FIRST:
            print(f"{nt}: {FIRST[nt]}")
        print("\n")

    elif choice == '2':
        print("FOLLOW:")
        for nt in FOLLOW:
            print(f"{nt}: {FOLLOW[nt]}")
        print("\n")

    elif choice == '3':
        print("\nLookup table:")
        max_nt_length = max(len(nt) for nt in lookup_table.keys())
        max_terminal_length = max(len(t) for t in terminals)
        # Вывод шапки таблицы
        header = f"{'-' * (max_nt_length + 2)}+{'-' * ((max_terminal_length + 2) * len(terminals))}"
        print(header)
        print(f"|   {'' * (max_nt_length)}|{' |'.join(t.ljust(max_terminal_length) for t in terminals)}|")
        print(header)
        # Вывод данных таблицы
        for nt, rules in lookup_table.items():
            nt_padding = " " * (max_nt_length - len(nt))
            nt_row = f"| {nt}{nt_padding} |"
            for rule in rules:
                if rule != -1:
                    nt_row += f"{rule:^{max_terminal_length}}"
                else:
                    nt_row += " " * max_terminal_length
                nt_row += " |"
            print(nt_row)
        print(header)
        print("\n")

    elif choice == '4':
        user_input = input("Enter string: ")
        result, actions = parse(user_input)
        print(f"Result: {result}, Actions: {actions}")
        print("\n")

    elif choice == '5':
        generated_string = generate_string('S')
        print(f"Generated String: {generated_string}")
        print("\n")

    elif choice == '6':
        for input_string in test_strings:
            result, actions = parse(input_string)
            print(f"Input: {input_string}\nResult: {result}, Actions: {actions}\n")
        print("\n")

    elif choice == '7':
        # Пример использования функции генерации строки
        for _ in range(10):
            generated_string = generate_string('S')
            print(f"Generated String: {generated_string}")
        print("\n")

    elif choice == '8':
        print("See you later!")
        break

    else:
        print("Incorrect input, try another time.")
        print("\n")
