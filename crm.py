import sqlite3
import datetime
import re
import argparse
import csv
class InvalidContactError(Exception):pass

def connection():
    conn=sqlite3.connect("dealbook.db")
    conn.row_factory=sqlite3.Row
    return conn
    
def create_table():
    with connection() as conn:
        conn.execute("""
                    CREATE TABLE IF NOT EXISTS dealbook(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    status TEXT DEFAULT 'new',
                    date TEXT)
""")

# Add Lead
def add(name,contact,status,date):
    # creates a class Lead object to validate before inserting to lead table
    lead = Lead(name,contact, status,date=None)
    date = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) #gives current date and time
    with connection() as conn:
        conn.execute (
            "INSERT INTO dealbook(name, contact, status,date) VALUES(?,?,?,?)",
            (lead.name.title(), lead.contact,lead.status,date)
        )

# Request Lead
def list_contact(status=None, verbose=False):
    with connection() as conn:
        if status:
            cursor = conn.execute("SELECT*FROM dealbook WHERE status=?",(status,))
        else:
            cursor = conn.execute("SELECT*FROM dealbook")
        rows = cursor.fetchall()
        print(f"\n📃 {len(rows)} listed")
        print(" ")
        if not rows:
            print(" ❌Lead not found")
            return False
        for row in rows:
            if verbose:
                print(f"ID: {row['id']} | Name: {row['name']} | Contact📞: {row['contact']} | Status: {row['status']} | Date: {row['date']}")
                print("-"*101)
            else:
                print(f"Name: {row['name']} | Status: {row['status']}")
                print("-"*56)
        return True
    return rows 
# Update Lead
def update(lead_id=None, name=None, contact=None, status=None, date=None):
    fields=[]
    values=[]
    if name is not None:
        fields.append("name=?")
        values.append(name.title())
    if contact is not None:
        fields.append("contact=?")
        values.append(contact)
    if status is not None:
        fields.append("status=?")
        values.append(status)
    if date is not None:
        fields.append("date=?")
        values.append(date)
    # checks if nothig at all was passed 
    if not fields:
        print("\n⚠️ Nothing to update. Please provide atleast one of this --name, --contact, --status, --date")
        return False
    values.append(lead_id)
    set_clause = ",".join(fields)
    request = f"UPDATE dealbook SET {set_clause} WHERE id=?"
    with connection() as conn:
        cursor = conn.execute(request,values)
        if cursor.rowcount == 0:
            print(f"❌ No lead found with ID {lead_id}")
            return False
        return True

# Delete Lead    
def delete(lead_id):
    if isinstance(lead_id,int):
        lead_id = [lead_id]
    count = len(lead_id) 
    ids_str = ", ".join(str(i) for i in lead_id)

    confirm = input(f"\n⚠️  Are you sure you want to Delete {count} contact(s) with ID(s) [{ids_str}]? [y/n]: ").strip().lower()
    if confirm != "y":
        print("❌ Delete cancelled")
        return False
    placeholders = ",".join("?"* count)
    with connection() as conn:
        cursor = conn.execute(f"DELETE FROM dealbook WHERE id=({placeholders})",lead_id)
        if cursor.rowcount == 0:
            print(f"❌ No leads found with those IDs")
            return False
        return True


def search(search_term,db_path="dealbook.db"):
    if not search_term:
        print("Please enter a search term")
        return False
    query_term = f"%{search_term}%"

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor=conn.execute("""SELECT id, name, contact, status, date FROM dealbook 
                         WHERE name LIKE ? OR contact LIKE ? OR status LIKE ? OR date LIKE ?""",
                         (query_term, query_term, query_term, query_term))
            
            searched = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"\n❌ Database Error: {e}")
        return False
    if not searched:
        print(f"\n❌ No leads found matching '{search_term}'. Try different search term.")
        return False 
    print(f"🔍 Found {len(searched)} matche(s):")
    print("-"*106)
    for row in searched:
        print(f"ID: {row['id']} | Name: {row['name']} | Contact📞: {row['contact']} | status{row['status']} saved on Date: {row['date']}")
    print("-"*106)
    return True

def export(export_path = "dealbook.csv"):
    with connection () as conn:
        cursor = conn.execute("SELECT * FROM dealbook")
        rows = cursor.fetchall()
    if not rows:
        print("❌ No leads to export")
        return False
    with open(export_path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames= ["id", "name","contact","status", "date"])
        writer.writeheader() # writes the csv"s columns
        for row in rows:
            writer.writerow(dict(row))
    print(f"✔ {len(rows)} lead(s) exported to {export_path}")
    return True
    
    
# OOP
class Lead:
    def __init__(self,name,contact,status,date):
        self.name=name
        self.contact=contact.lower()
        self.status=status
        self.date=date

    def __str__(self):
        return f"{self.name} | {self.contact} | {self.status} | {self.date}"
    

# Contact validation
    @property
    def contact(self):
        return self._contact
    
    @contact.setter
    def contact(self,contact):
        email_validation = r"^[a-z0-9_\-\.]+@[a-z0-9]+\.[a-z]{2,}$"
        phone_validation = r"^(\+254|0)[0-9]{9}$"
        if not (re.search(email_validation,contact) or re.search(phone_validation,contact)):
            raise InvalidContactError("Please re-enter your contact")
        self._contact=contact


def cli():
    parser = argparse.ArgumentParser(description="Lead CRM")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="Add new lead")
    p_add.add_argument("-n","--name", required=True) 
    p_add.add_argument("-c","--contact", required=True)
    p_add.add_argument("-s","--status", default="new")
    p_add.add_argument("-d","--date", help= "Current datetime")

    p_list = sub.add_parser("list", help="List all leads")
    p_list.add_argument("-s","--status",default=None,help="Filter by lead status")
    p_list.add_argument("-v","--verbose",action="store_true", help="List in full details")

    p_update = sub.add_parser("update")
    p_update.add_argument("--id", required=True, type=int,help="Lead ID to update")
    p_update.add_argument("-n","--name", help="Update lead's name")
    p_update.add_argument("-c","--contact",help="Update lead's contact info")
    p_update.add_argument("-s","--status", help= "Update lead's status")
    p_update.add_argument("-d","--date")

    p_delete = sub.add_parser("delete")
    p_delete.add_argument("--id", required=True, type=int)

    p_search = sub.add_parser("search", help="Search by name, status or id")
    p_search.add_argument("search", help= "Full search term or a partial hint of search term")

    p_export = sub.add_parser("export", help="Export leads to CSV")
    p_export.add_argument("-o","--output", default= "dealbook.csv", help="Output file names")

    args = parser.parse_args()
# DISPATCHER
    if args.command == "add":
        # validation from class Lead
        try:
           add(args.name, args.contact,args.status,args.date)
           print("✔ Lead succesfully added")
        except InvalidContactError as e:
            print(f"❌ Invalid lead contact: {e}")
    elif args.command == "list":
        if list_contact(status=args.status, verbose=args.verbose):
           print("              ☑       ")
           print("✔ Lead(s) succesfully retrived")
           
    elif args.command == "update":
        if update(args.id,name=args.name, contact=args.contact, status=args.status, date=args.date):
            print("✔ Lead(s) updated succesfully")
    elif args.command == "delete":
        if delete(args.id):
            print("✔ Lead(s) deleted succesfully")
    elif args.command == "search":
        if search(args.search):
            print("✔ Search done")
    elif args.command == "export":
        if export(args.output):
            print("✔ Leads exported")
    else:
        parser.print_help()


def main():
    create_table()
    print(" ") 
    cli()
    print("x"*100)
    print(" ")


if __name__ =="__main__":
    main()
