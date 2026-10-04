import math
import sys

FIELD_SIZE = 100


def solve(str1, str2, str3):
    try:
        a = float(str1)
        b = float(str2)
        c = float(str3)
    except ValueError:
        return "", [(-2, -2), (-2, -2), (-2, -2)]

    if not (a > 0 and b > 0 and c > 0 and a + b > c and a + c > b and b + c > a):
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    x1 = (b ** 2 + a ** 2 - c ** 2) / (2 * a)
    y1 = math.sqrt(b ** 2 - x1 ** 2)
    min_x = min(x1, 0.0, a)
    scale = (FIELD_SIZE - 1) / max(max(x1, 0.0, a) - min_x, y1)

    if a == b == c:
        kind = "равносторонний"
    elif a == b or b == c or a == c:
        kind = "равнобедренный"
    else:
        kind = "разносторонний"

    coords = [
        (round(x1 * scale - min_x * scale), round(y1 * scale)),
        (round(0.0 - min_x * scale), 0),
        (round(a * scale - min_x * scale), 0),
    ]
    return kind, coords


if __name__ == "__main__":
    for s1, s2, s3 in [
        ("5", "5", "5"),
        ("6", "6", "10"),
        ("7", "8", "9"),
        ("1", "1", "3"),
        ("abc", "2", "3"),
    ]:
        print(s1, s2, s3, "->", solve(s1, s2, s3))