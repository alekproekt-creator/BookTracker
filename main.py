
import json
from collections import deque
from dataclasses import dataclass, asdict, field
from typing import List

DB_PATH = "books.json"  # файл данных

# Модель: Book с инкапсуляцией через dataclass и валидацией в методах
@dataclass
class Book:
    title: str
    author: str
    genre: str
    pages: int
    _type: str = field(default="book", repr=False)

    def __post_init__(self):
        self.title = self.title.strip()
        self.author = self.author.strip()
        self.genre = self.genre.strip()
        try:
            self.pages = int(self.pages)
        except Exception:
            raise ValueError("Pages must be an integer")
        if not self.title:
            raise ValueError("Title cannot be empty")
        if not self.author:
            raise ValueError("Author cannot be empty")
        if not self.genre:
            raise ValueError("Genre cannot be empty")
        if self.pages <= 0:
            raise ValueError("Pages must be > 0")

    def to_dict(self):
        d = asdict(self)
        d["type"] = self._type
        d.pop("_type", None)
        return d

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get("title",""),
            author=data.get("author",""),
            genre=data.get("genre",""),
            pages=int(data.get("pages",0))
        )

# Хранилище JSON
def load_books(path=DB_PATH) -> List[Book]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []
    books = []
    for item in data:
        try:
            books.append(Book.from_dict(item))
        except Exception:
            # пропускаем некорректные записи
            continue
    return books

def save_books(books: List[Book], path=DB_PATH):
    data = [b.to_dict() for b in books]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# История действий (стек)
history = deque(maxlen=100)  # хранит словари действий

# Представление (консоль)
def print_menu():
    print("\nBook Tracker")
    print("1. Показать все книги")
    print("2. Добавить книгу")
    print("3. Редактировать книгу")
    print("4. Удалить книгу")
    print("5. Фильтрация")
    print("6. История")
    print("7. Сохранить")
    print("8. Загрузить")
    print("9. Выход")

def show_books(books: List[Book]):
    if not books:
        print("Список пуст.")
        return
    for i, b in enumerate(books, 1):
        print(f"{i}. {b.title} — {b.author} | {b.genre} | {b.pages} стр.")

# Контроллер (логика команд)
def input_nonempty(prompt):
    v = input(prompt).strip()
    if not v:
        raise ValueError("Поле не может быть пустым")
    return v

def input_positive_int(prompt):
    v = input(prompt).strip()
    try:
        n = int(v)
        if n <= 0:
            raise ValueError
        return n
    except:
        raise ValueError("Ожидается положительное целое число")

def add_book(books):
    try:
        title = input_nonempty("Title: ")
        author = input_nonempty("Author: ")
        genre = input_nonempty("Genre: ")
        pages = input_positive_int("Pages: ")
    except ValueError as e:
        print("Ошибка:", e)
        return
    b = Book(title, author, genre, pages)
    books.append(b)
    history.append({"action":"add","book":b.to_dict()})
    print("Добавлено.")

def edit_book(books):
    if not books:
        print("Нет книг.")
        return
    show_books(books)
    try:
        idx = int(input("Номер для редактирования: ").strip()) - 1
        if idx < 0 or idx >= len(books):
            print("Неверный номер.")
            return
    except:
        print("Неверный ввод.")
        return
    old = books[idx]
    print("Оставьте поле пустым, чтобы не менять.")
    title = input(f"Title [{old.title}]: ").strip() or old.title
    author = input(f"Author [{old.author}]: ").strip() or old.author
    genre = input(f"Genre [{old.genre}]: ").strip() or old.genre
    pages_raw = input(f"Pages [{old.pages}]: ").strip()
    if pages_raw:
        try:
            pages = int(pages_raw)
            if pages <= 0:
                raise ValueError
        except:
            print("Pages должно быть положительным целым. Отмена.")
            return
    else:
        pages = old.pages
    try:
        new = Book(title, author, genre, pages)
    except ValueError as e:
        print("Ошибка:", e)
        return
    books[idx] = new
    history.append({"action":"edit","old":old.to_dict(),"new":new.to_dict()})
    print("Обновлено.")

def delete_book(books):
    if not books:
        print("Нет книг.")
        return
    show_books(books)
    try:
        idx = int(input("Номер для удаления: ").strip()) - 1
        if idx < 0 or idx >= len(books):
            print("Неверный номер.")
            return
    except:
        print("Неверный ввод.")
        return
    removed = books.pop(idx)
    history.append({"action":"delete","book":removed.to_dict()})
    print("Удалено.")

def filter_menu(books):
    print("1. По жанру")
    print("2. По минимальному количеству страниц")
    c = input("Выбор: ").strip()
    if c == "1":
        g = input("Жанр: ").strip()
        res = [b for b in books if b.genre.lower() == g.lower()]
        show_books(res)
    elif c == "2":
        try:
            mn = int(input("Минимум страниц: ").strip())
        except:
            print("Неверное число.")
            return
        res = [b for b in books if b.pages >= mn]
        show_books(res)
    else:
        print("Неверный выбор.")

def show_history():
    if not history:
        print("История пуста.")
        return
    for i, h in enumerate(history, 1):
        print(f"{i}. {h}")

def main():
    books = load_books()
    while True:
        print_menu()
        cmd = input("Выберите пункт: ").strip()
        if cmd == "1":
            show_books(books)
        elif cmd == "2":
            add_book(books)
        elif cmd == "3":
            edit_book(books)
        elif cmd == "4":
            delete_book(books)
        elif cmd == "5":
            filter_menu(books)
        elif cmd == "6":
            show_history()
        elif cmd == "7":
            try:
                save_books(books)
                print("Сохранено в", DB_PATH)
            except Exception as e:
                print("Ошибка сохранения:", e)
        elif cmd == "8":
            books = load_books()
            print("Загружено.")
        elif cmd == "9":
            try:
                save_books(books)
            except:
                pass
            print("Выход.")
            break
        else:
            print("Неверная команда.")

if __name__ == "__main__":
    main()


