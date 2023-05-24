import re
import pickle
from collections import UserDict
from datetime import datetime, date


class Field:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __str__(self):
        return str(self._value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return Field.value.fget(self)

    @value.setter
    def value(self, value):
        if value is not None and not re.match(r'^\+?380\d{9}$', value):
            raise ValueError(
                "Phone number should be in the format +380XXXXXXXXX")
        Field.value.fset(self, value)


class Record:
    def __init__(self, name, phones, birthday=None):
        self.name = name
        self.phones = phones if phones is not None else []
        self.birthday = birthday

    def add_phone(self, phone):
        phone = Phone(phone)
        self.phones.append(phone)

    def edit_phone(self, index, phone):
        phone = Phone(phone)
        self.phones[index] = phone

    def delete_phone(self, index):
        del self.phones[index]

    def days_to_birthday(self):
        if self.birthday and self.birthday.value:
            today = date.today()
            next_birthday = date(today.year, self.birthday.value.month, self.birthday.value.day)

            if next_birthday < today:
                next_birthday = date(today.year + 1, self.birthday.value.month, self.birthday.value.day)

            return (next_birthday - today).days
        else:
            return None

    def __str__(self):
        phones = ", ".join(phone.value for phone in self.phones if phone.value)
        days_to_birthday = self.days_to_birthday()
        return f'Name: {self.name.value}, Phone: {phones}, Days to Birthday: {days_to_birthday}'



class AddressBook(UserDict):
    def __iter__(self):
        yield from self.data.values()

    def add_contact(self, record):
        self.data[record.name.value] = record

    def edit_contact(self, name, phone):
        record = self.data[name]
        record.edit_phone(0, phone)
        self.add_contact(record)

    def delete_contact(self, name):
        del self.data[name]

    def show_all(self):
        if self.data:
            return "\n".join(str(record) for record in self.data.values())
        else:
            return "No contacts found"

    def search(self, query):
        query = query.lower()
        results = []
        for record in self.data.values():
            if query in record.name.value.lower():
                results.append(record)
            else:
                for phone in record.phones:
                    if query in phone.phone_number.lower():
                        results.append(record)
                        break
        return results

    def save_to_file(self, filename):
        with open(filename, "wb") as file:
            pickle.dump(self.data, file)

    def load_from_file(self, filename):
        try:
            with open(filename, "rb") as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            pass


class Birthday(Field):
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value:
            try:
                self._value = datetime.strptime(value, '%d%m%Y').date()
                if self._value < date.today():
                    self._value = self._value.replace(
                        year=date.today().year + 1)
            except ValueError:
                raise ValueError("Invalid birthday date format. Use DDMMYYYY.")


def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except KeyError:
            return "Contact not found"
        except ValueError:
            return "Enter name and phone"
        except IndexError:
            return "Enter name and phone"
    return wrapper


@input_error
def add_contact(ab, name, phone):
    record = Record(Name(name), [Phone(phone)])
    ab.add_contact(record)
    return "Contact added"


@input_error
def change_phone(ab, name, phone):
    ab.edit_contact(name, phone)
    return "Phone number changed"


@input_error
def delete_contact(ab, name):
    ab.delete_contact(name)
    return "Contact deleted"

@input_error
def search(ab, name):
    results = ab.search(name)
    if results:
        return results
    else:
        raise IndexError("Enter name")



@input_error
def show_phone(ab, name):
    record = ab.data.get(name)
    if record:
        return record.phones[0].phone_number if record.phones else "No phone number"
    else:
        raise KeyError("Contact not found")


ab = AddressBook()


def main():
    ab.load_from_file("address_book.pkl")
    print("Hello!")

    while True:
        command = input().lower()

        if command == "hello":
            print("How can I help you?")

        elif command.startswith("add"):
            try:
                data = input(
                    "Enter name, phone, and birthday (optional): ").split()
                if len(data) < 2:
                    raise ValueError("Please add other information")
                name = data[0]
                phone = data[1]
                birthday = data[2] if len(data) > 2 else None
                record = Record(
                    Name(name), [Phone(phone)], birthday=Birthday(birthday))
                ab.add_contact(record)
                print("Contact added")
            except ValueError as e:
                print(str(e))

        elif command.startswith("change"):
            try:
                name, phone = input("Enter name and phone: ").split()
                result = change_phone(ab, name, phone)
            except ValueError:
                result = "Enter name and phone"
            print(result)

        elif command.startswith("phone"):
            try:
                name = command.split()[1]
                result = show_phone(ab, name)
            except IndexError:
                result = "Enter name"
            print(result)

        elif command.startswith("search"):
            try:
                query = command.split(maxsplit=1)[1]
                results = ab.search(query)
                print("Search results:")
                for record in results:
                    print(record)
                if not results:
                    print("No matching contacts found")
            except IndexError:
                print("Enter a query for the search")


        elif command == "show all":
            result = ab.show_all()
            print(result)

        elif command == "delete":
            try:
                name = input("Enter name: ")
                result = delete_contact(ab, name)
            except IndexError:
                result = "Not found"
            print(result)

        elif command == "save":
            ab.save_to_file("address_book.pkl")
            print("Address book saved")

        elif command == "load":
            ab.load_from_file("address_book.pkl")
            print("Address book loaded")

        elif command in ["good bye", "close", "exit"]:
            ab.save_to_file("address_book.pkl")
            print("Address book saved")
            print("Good bye!")
            break

        else:
            print("Unknown command")


main()
