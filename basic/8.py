import pytest

contacts: dict[str, str] = {}
phone_set: set[str] = set()


def add_contact(name: str, phone: str) -> None:
    if not name.strip() or not phone.strip():
        raise ValueError("Name/phone must not be empty")
    if phone in phone_set:
        raise ValueError(f"Phone {phone} already exists")
    if name in contacts:
        raise ValueError(f"Contact {name} already exists")
    contacts[name] = phone
    phone_set.add(phone)
    print(f"Added: {name} -> {phone}")


def test_add_contact() -> None:
    contacts.clear()
    phone_set.clear()

    assert add_contact("An", "0901111111") is None

    with pytest.raises(ValueError, match="Phone 0901111111 already exists"):
        add_contact("Cuong", "0901111111")

    with pytest.raises(ValueError, match="Name/phone must not be empty"):
        add_contact("", "0904444444")

    with pytest.raises(ValueError, match="Name/phone must not be empty"):
        add_contact("An", "")

    with pytest.raises(ValueError, match="Contact An already exists"):
        add_contact("An", "0909999999")


def view_contact(name: str) -> None:
    if name not in contacts:
        raise KeyError(f"Contact {name} not found")
    print(f"{name}: {contacts[name]}")


def test_view_contact() -> None:
    contacts.clear()
    phone_set.clear()

    add_contact("An", "0901111111")
    assert view_contact("An") is None

    with pytest.raises(KeyError, match="Contact Hung not found"):
        view_contact("Hung")


def update_contact(name: str, phone: str) -> None:
    if not name.strip() or not phone.strip():
        raise ValueError("Name/phone must not be empty")
    if name not in contacts:
        raise KeyError(f"Contact {name} not found")
    if phone in phone_set and contacts[name] != phone:
        raise ValueError(f"Phone {phone} already used")
    phone_set.discard(contacts[name])
    contacts[name] = phone
    phone_set.add(phone)
    print(f"Updated: {name} -> {phone}")


def test_update_contact() -> None:
    contacts.clear()
    phone_set.clear()

    add_contact("An", "0901111111")
    add_contact("Binh", "0902222222")

    assert update_contact("An", "0903333333") is None

    with pytest.raises(KeyError, match="Contact Hung not found"):
        update_contact("Hung", "0904444444")

    with pytest.raises(ValueError, match="Name/phone must not be empty"):
        update_contact("", "0904444444")

    with pytest.raises(ValueError, match="Phone 0902222222 already used"):
        update_contact("An", "0902222222")


def delete_contact(name: str) -> None:
    if name not in contacts:
        raise KeyError(f"Contact {name} not found")
    phone_set.discard(contacts.pop(name))
    print(f"Deleted: {name}")

def test_delete_contact() -> None:
    contacts.clear()
    phone_set.clear()
    add_contact("An", "0901111111")
    assert delete_contact("An") is None
    with pytest.raises(KeyError, match="Contact Hung not found"):
        delete_contact("Hung")


def list_contacts() -> None:
    if not contacts:
        raise KeyError("No contacts")
    for name, phone in contacts.items():
        print(f"- {name}: {phone}")


def test_list_contacts() -> None:
    contacts.clear()
    phone_set.clear()

    with pytest.raises(KeyError, match="No contacts"):
        list_contacts()

    add_contact("An", "0901111111")
    add_contact("Binh", "0902222222")
    assert list_contacts() is None


def demo_crud_four_types() -> None:
    print("\n=== Demo CRUD on 4 data types ===")

    try:
        names = ["An", "Binh"]
        names[1] = "Binh Updated"
        names.remove("An")
        print("list:", names)
        names.remove("NotExist")
    except ValueError as e:
        print(f"list error: {e}")

    try:
        phones = {"0901", "0902"}
        phones.discard("0901")
        phones.add("0903")
        print("set:", phones)
        phones.remove("9999")
    except KeyError as e:
        print(f"set error: {e}")

    try:
        book = {"An": "0901", "Hung": "0902"}
        book["An"] = "0909"
        del book["An"]
        print("dict:", book)
    except KeyError as e:
        print(f"dict error: key {e} not found")

if __name__ == "__main__":
    contacts.clear()
    phone_set.clear()

    for name, phone in [
        ("An", "0901111111"),
        ("Binh", "0902222222"),
        ("Cuong", "0901111111"),
        ("", "0904444444"),
    ]:
        try:
            add_contact(name, phone)
        except ValueError as e:
            print(f"Add failed: {e}")

    try:
        view_contact("An")
        view_contact("NoName")
    except KeyError as e:
        print(f"View failed: {e}")

    try:
        update_contact("An", "0903333333")
        update_contact("Ghost", "0900000000")
    except (KeyError, ValueError) as e:
        print(f"Update failed: {e}")

    try:
        list_contacts()
    except KeyError as e:
        print(f"List failed: {e}")

    for person in ("Binh", "Binh"):
        try:
            delete_contact(person)
        except KeyError as e:
            print(f"Delete failed: {e}")

    try:
        list_contacts()
    except KeyError as e:
        print(f"List failed: {e}")

    print("\nnames (list):", list(contacts.keys()))
    print("phones (tuple):", tuple(contacts.values()))
    print("unique phones (set):", phone_set)
    demo_crud_four_types()
