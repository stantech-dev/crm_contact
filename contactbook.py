import argparse
import sqlite3
#1.SQL BLOCK
#CREATES A CONNECTION WITH THE FILE
def connection():
    conn = sqlite3.connect("contactbook.db")
    conn.row_factory=sqlite3.Row
    return conn

# CREATES A TABLE
def create_table():
    with connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS contactbook(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE CHECK(length(phone)>=10),
                    age INTEGER NOT NULL,
                    tag TEXT DEFAULT 'general')
                    """ )

# ADDS DATA TO FILE
def add(name, phone,age, tag):
    with connection() as conn:
        conn.execute(
            "INSERT INTO contactbook(name,phone,age,tag) VALUES(?,?,?,?)",
            (name.title(),phone,age,tag)
            )

# RETRIVES DATA QUERIES
def list_contacts(tag=None, verbose=False):
    with connection() as conn:
        if tag:
            cursor = conn.execute("SELECT * FROM contactbook WHERE tag=?", (tag,)) # filters by tag
        else:
            cursor = conn.execute("SELECT * FROM contactbook") # no filter.full list
        rows = cursor.fetchall() 
        print(f"\n📃 {len (rows)} listed")
        print("-"*56)
        for row in rows:
            if verbose:
                print(f"ID: {row['id']} | Name: {row['name']} | Phone📞: {row['phone']} | Age: {['age']} | Tag: [{row['tag']}]")
                print("-"*56)
            else:
                print(f"Name: {row['name']} | Tag: {row['tag']}")
        print("-"*56)
    return rows
    
# UPDATES COLUMNS IN THE TABLE
def update(contact_id, name=None,phone=None,age=None,tag=None):
    fields=[] # the columns the user will select(name,tag,phone)
    values=[] # the actual value of the columns
    if name is not None:
        fields.append("name=?")
        values.append(name.title())
    if phone is not None:
        fields.append("phone=?")
        values.append(phone)
    if age is not None:
        fields.append("age=?")
        values.append(age)
    if tag is not None:
        fields.append("tag=?")
        values.append(tag)
    if not fields:
        print("\n⚠️ Nothing to update. Provide atleast one of this --name, --phone, --age, --tag.")
        return
    values.append(contact_id) # Appends the id value to assign the value to the WHERE id=? 
    set_clauses = ",".join(fields)  # ",".join(fields) merges the fields lists elements and the "," acts as a separator between the fields
    query= f"UPDATE contactbook SET {set_clauses} WHERE id=?" 
    with connection() as conn:
        conn.execute(query,values)

#DELETES ROWS FROM THE TABLE
def delete(contact_id):
    # ENABLES SIMULTANEOUS DELETION AT ONCES
    if isinstance(contact_id,int): # CONFIRMS THE VARIABLE(contact_id) IS AN INTEGER
        contact_id=[contact_id]
    count = len(contact_id) 
    ids_str = ", ".join(str(i) for i in contact_id)

    #CONFRIMATION MESSAGE
    confirm = input(f"\n⚠️  Are you sure you want to Delete {count} contact(s) with ID(s) [{ids_str}]? [y/N]: ").strip().lower()

    if confirm != "y":
        print("❌ Delete cancelled.")
        return
    placeholders =",".join("?"* count)
    with connection() as conn:
        conn.execute(f"DELETE FROM contactbook WHERE id IN ({placeholders})", contact_id)


# FOR SEARCHING CONTACT
def search(search_term, db_path="contactbook.db"):
    if not search_term:
        print("\n⚠️ Please enter a search term.")
        return

    query_param = f"%{search_term}%"  

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor = cursor.execute("""
                SELECT id, name, phone, age, tag 
                FROM contactbook 
                WHERE name LIKE ? OR phone LIKE ? OR age LIKE ? OR tag LIKE ?
            """, (query_param, query_param, query_param, query_param))

            results = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"\n❌ Database error: {e}")
        return

    if not results:
        print(f"\n❌ No contacts found matching '{search_term}'.")
        return

    print(f"\n🔍 Found {len(results)} match(es):")
    print("-" * 50)
    for row in results:
        print(f"ID: {row['id']} | Name: {row['name']} | Phone📞: {row['phone']} | Age: {['age']} | Tag: [{row['tag']}]")
    print("-" * 50)


# 2.CLI BLOCK
def cli():
# . Main parser
    parser = argparse.ArgumentParser(
        description="Contacts CLI — manage your contacts from the terminal"
    )

# . Registers subcommands
    sub = parser.add_subparsers(dest="command")

# --- ADD ---
    p_add = sub.add_parser("add", help="Add a new contact")
    p_add.add_argument("-n", "--name",  required=True, help="Full name")
    p_add.add_argument("-p", "--phone", required=True, help="Phone number")
    p_add.add_argument("-a", "--age", required=True, help="Person's age")
    p_add.add_argument("-t", "--tag",   default="general",help="Category tag (default: general)")

# --- LIST ---
    p_list = sub.add_parser("list", help="List all contacts")
    p_list.add_argument("--tag", default=None, help="Filter by tag")
    p_list.add_argument("--verbose", action="store_true", help="Show full details for each contact")

# --- UPDATE ---
    p_update = sub.add_parser("update", help="Update an existing contact")
    p_update.add_argument("--id", required=True, type=int, help="Contact ID to update")
    p_update.add_argument("--name", help="New name")
    p_update.add_argument("--phone", help="New phone number")
    p_update.add_argument("--age",help="Person's new age")
    p_update.add_argument("--tag", default="general", help="New tag")

# --- DELETE ---
    p_delete = sub.add_parser("delete", help="Delete a contact from contactbook")
    p_delete.add_argument("--id", required=True, type=int,nargs="+", help="Contact ID to delete") # nargs ="+" allows passing more than two arguments and concantenates them

# --- SEARCH ---
    p_search = sub.add_parser("search", help="Search contacts by name, contact or tag")
    p_search.add_argument("search_term", help="Name or partial name to search") # search_term is a positional argument

# . Parse the input
    args = parser.parse_args()

# . Dispatch to the right function
    if args.command == "add":
        add(args.name, args.phone, args.age, args.tag)
        print("✔ Contact added succesfully")

    elif args.command == "list":
        list_contacts(tag=args.tag, verbose=args.verbose)
        print("✔ Contact retrived succesfully")

    elif args.command == "update":
        update(args.id, name=args.name, phone=args.phone, age=args.age, tag=args.tag)
        print("✔ Contact updated succesfully")

    elif args.command == "delete":
        delete(args.id)
        print("✔ Contact deleted succesfully")

    elif args.command == "search":
        search(args.search_term)
        print("Search Done✔")

    else:
        parser.print_help()

# CALLER
def main():
    create_table()
    cli()


if __name__ == "__main__":
    main()