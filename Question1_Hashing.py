#local storage system of a pharmacy retail outlet
import time

#entity class: one Product object = one pharmacy product
class Product:
    def __init__(self, id, name, price, stock):
        #id    -> int, unique product code, also the key used by the hash table
        #name  -> str, product name shown to the user
        #price -> float, price in RM, rounded to 2 decimal places
        #stock -> int, units in stock, a whole number because half a box cannot be sold
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

    def __str__(self):
        return f'ID: {self.id} | Name: {self.name} | Price: RM{self.price:.2f} | Stock: {self.stock}'

"""
DELETED is a tombstone: a marker placed in a slot after a product is deleted.
object() creates a brand-new object with its own unique memory address, so it
is point to the address to flag as 'object is deleted from the slot'.

Why not use None for a deleted slot?
- None already means "never used -> stop searching".
If delete set the slot to None, the probe path would break.
Keys that were pushed past this slot during insert could no longer be found (search would stop too early).

Marker Meaning:
None    -> never used, the walk STOPS here
DELETED -> was used, the walk MOVES ON to the next slot
"""
DELETED = object()

#how many times each search is repeated in the timing experiment
#one search takes less than a microsecond, too short for a clock to measure fairly
#repeating it and taking the average removes most of the timing noise
REPEATS = 10000

#size of the bigger test data used by the performance experiment (menu option 5)
#5 shop records are too few to show the difference between O(1) and O(n)
EXPERIMENT_RECORDS = 1000
#table is twice the number of records -> load factor 0.5, probe chains stay short
EXPERIMENT_TABLE_SIZE = 2000


#######################################
#input helpers (user typing, not table)#
#######################################

#keep asking until the user types a whole number
def read_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print(f'Please enter a valid whole number')

#product ID must be a whole number above 0
def read_id(prompt):
    while True:
        product_id = read_int(prompt)
        if product_id > 0:
            return product_id
        print(f'Product ID must be greater than 0')

#validate price: must be a number and not negative
#keep: current value, used by edit so that pressing Enter keeps the old price
def read_price(prompt, keep=None):
    while True:
        text = input(prompt)
        if text == '' and keep is not None:
            return keep
        try:
            price = round(float(text), 2)
        except ValueError:
            print(f'Please enter a valid number')
            continue
        if price < 0:
            print(f'Price cannot be negative')
            continue
        return price

#validate stock quantity: must be a whole number and not negative
def read_stock(prompt, keep=None):
    while True:
        text = input(prompt)
        if text == '' and keep is not None:
            return keep
        try:
            stock = int(text)
        except ValueError:
            print(f'Please enter a valid whole number')
            continue
        if stock < 0:
            print(f'Stock cannot be negative')
            continue
        return stock


"""
WHY A HASH TABLE?
The key is turned into a slot number directly (slot = key % size),
so insert / search / delete jump straight to (or near) the right slot -> O(1) on average.
A one-dimensional array has to check the records one by one -> O(n).

STRUCTURE OF THE SLOTS
self.table is a Python list with a fixed number of slots.
Each slot holds exactly one of three things:
None          -> never used
DELETED       -> tombstone, was used before
(key, value)  -> a stored record, e.g. (1041, <Product 1041>)

Why store (key, value) and not just the Product?
The table only ever reads the key, it never touches .id, .name, .price or .stock.
So the same HashTable can store any kind of record with a whole-number key (abstraction, reusable).

Collision resolution: Open Addressing with Linear Probing
If the slot is taken, try the next slot (index + 1), wrap to 0 at the end.
Every record stays inside the one list, no extra lists or pointers are needed.
"""
class HashTable:

    def __init__(self, size):
        #a table with 0 slots would make key % 0 crash
        if size <= 0:
            raise ValueError('Hash table size must be at least 1')
        self.size = size
        #initialize table, empty slots
        self.table = [None] * size

    ##########################
    #private helper functions#
    ##########################

    #encapsulation
    #division method: the remainder of key / size is always between 0 and size - 1,
    #so every whole-number key maps to a slot inside the table
    def _hash(self, key):
        return key % self.size

    #find hash index in hash table
    def _find_index(self, search_key):
        counter = 0
        #get slot number
        hash_index = self._hash(search_key)

        #efficiency: hash table starts from hash index, array starts from index 0
        #stop after checking every slot, so a full table without the key cannot loop forever
        while counter < self.size:
            #slot: what is stored at this position (None, DELETED or (key, value))
            slot = self.table[hash_index]
            #if the slot is empty, stop searching -> key is not in the table
            #key was insert in the FIRST empty slot it meets in probing
            #empty slot -> no key was ever pushed past this point
            #this check must come first, because None has no slot[0] and would crash the next check
            if slot is None:
                return None
            #is operator compare is two variable pointing to the exact same memory location
            elif slot is DELETED:
                hash_index = (hash_index + 1) % self.size
                counter += 1
            #slot[0] is the key of the stored record
            #if same, record was found
            elif slot[0] == search_key:
                return hash_index

            #when different key in the slot (slot is not empty and not the same key)
            #if the key was pushed to other slot due to collision, move to next slot to find
            else:
                hash_index = (hash_index + 1) % self.size
                counter += 1
        #loop ended because counter reached size: every slot was checked and the key was not found
        return None

    #########################
    #public functions       #
    #########################

    #the table does not print anything and does not ask for input
    #it only returns results, the menu decides what to show (abstraction)

    #public lookup: returns the stored value or None (keeps _find_index private)
    def find(self, search_key):
        index = self._find_index(search_key)
        if index is None:
            return None
        #slot is (key, value), [1] is the value
        return self.table[index][1]

    #returns the slot number used, or None when the key already exists or the table is full
    def insert(self, key, value):
        counter = 0
        hash_index = self._hash(key)
        #notebook: index of the FIRST tombstone seen on the trail (None = not seen yet)
        deleted_index = None

        #walk until a real None (never used) or every slot has been checked
        while self.table[hash_index] is not None and counter < self.size:
            if self.table[hash_index] is DELETED:
                #record only the first tombstone, later ones are ignored
                if deleted_index is None:
                    deleted_index = hash_index
                #always keep walking, a duplicate may be further along the trail
                hash_index = (hash_index + 1) % self.size
                counter += 1
            elif self.table[hash_index][0] != key:
                #collision: different key in this slot, move on
                hash_index = (hash_index + 1) % self.size
                counter += 1
            else:
                #duplicate key: refuse, the old record stays
                return None

        #walk finished with no duplicate, so reusing the tombstone is safe
        if deleted_index is not None:
            self.table[deleted_index] = (key, value)
            return deleted_index

        #no tombstone to reuse and every slot was occupied
        if counter >= self.size:
            return None

        #no tombstone: place at the real empty slot where the walk stopped
        self.table[hash_index] = (key, value)
        return hash_index

    #returns the removed value, or None when the key is not in the table
    def delete(self, search_key):
        index = self._find_index(search_key)
        if index is None:
            return None
        #keep the value before the slot is overwritten, so the caller can use it
        value = self.table[index][1]
        #tombstone, not None, so the probe path is not broken
        self.table[index] = DELETED
        return value


#######################################
#searching and timing                 #
#######################################

#array search start from index 0
def search_arr(arr, search_key):
    for p in arr:
        if p.id == search_key:
            return p
    return None

#same shape as search_arr, so both can be timed by the same function
def search_ht(ht, search_key):
    return ht.find(search_key)

#search_function: search_ht or search_arr
#container: the hash table or the array that search_function looks in
#runs the same search REPEATS times and returns (result, average time in ns)
def average_search_ns(search_function, container, search_key):
    #perf_counter_ns: highest resolution clock, whole nanoseconds, no float rounding
    #only the searches sit between start and end, prints come after
    start_time = time.perf_counter_ns()
    for _ in range(REPEATS):
        result = search_function(container, search_key)
    end_time = time.perf_counter_ns()
    #the for loop itself adds the same small cost to both structures, so the comparison stays fair
    return result, (end_time - start_time) / REPEATS

#search the same key in both structures and time only the lookup
def compare_search(ht, arr, search_key):
    hash_result, hash_ns = average_search_ns(search_ht, ht, search_key)
    #only the time is needed from the array search, the result is the same record
    _, arr_ns = average_search_ns(search_arr, arr, search_key)

    #time both found and not found searches
    if hash_result is None:
        print(f'Product not found.')
    else:
        print(f'Product found!')
        print(hash_result)
    print(f'Average search time over {REPEATS:,} runs:')
    print(f'Hash Table : {hash_ns:,.1f} ns')
    print(f'Array      : {arr_ns:,.1f} ns')

#performance experiment on bigger test data (menu option 5)
#same records go into both structures, then 4 cases are timed:
#first record  -> best case for the array (found at index 0)
#middle record -> average case for the array
#last record   -> worst case for the array (checks every record)
#not found     -> array checks every record and still finds nothing
#the hash table should stay about the same in all 4 cases -> O(1)
#the array time should grow with the position of the record -> O(n)
def run_experiment():
    ht = HashTable(EXPERIMENT_TABLE_SIZE)
    arr = []
    for i in range(1, EXPERIMENT_RECORDS + 1):
        p = Product(i, f'Test Product {i}', 1.00, 10)
        if ht.insert(p.id, p) is not None:
            arr.append(p)

    #(label, key) pairs, one row of the result table each
    cases = [
        ("First record", 1),
        ("Middle record", EXPERIMENT_RECORDS // 2),
        ("Last record", EXPERIMENT_RECORDS),
        ("Not found", EXPERIMENT_RECORDS * 10),
    ]

    print(f'\n==== Performance Experiment ({len(arr):,} records, {REPEATS:,} runs per search) ====')
    print(f'{"Case":<15}{"Key":>8}{"Hash Table (ns)":>18}{"Array (ns)":>15}')
    for label, key in cases:
        _, hash_ns = average_search_ns(search_ht, ht, key)
        _, arr_ns = average_search_ns(search_arr, arr, key)
        print(f'{label:<15}{key:>8}{hash_ns:>18,.1f}{arr_ns:>15,.1f}')
    print()


#predefined product records
def load_records():
    panadol = Product(1041, "Paracetamol 500mg", 5.90, 120)
    amoxicillin = Product(1051, "Amoxicillin 250mg", 12.50, 60)
    ibuprofen = Product(1042, "Ibuprofen 400mg", 8.90, 80)
    vitaminc = Product(2087, "Vitamin C 1000mg", 15.00, 45)
    cough_syrup = Product(3005, "Cough Syrup 100ml", 11.30, 30)
    return [panadol, amoxicillin, ibuprofen, vitaminc, cough_syrup]

#create the hash table and the array, both receive the same records
def build_storage():
    #create hash table object with 10 slots
    ht = HashTable(10)
    arr = []
    #insert predefined records into hash table and one-dimensional array
    for p in load_records():
        slot = ht.insert(p.id, p)
        #only append when the hash table accepted it, so both hold the same data
        if slot is not None:
            arr.append(p)
            print(f'Product {p.id} inserted successfully into slot [{slot}]')
        else:
            print(f'Product {p.id} could not be inserted (duplicate ID or table full)')
    return ht, arr


#######################################
#menu actions                         #
#######################################

def insert_product(ht, arr):
    #check the id first, ask for the rest only if the id is free
    product_id = read_id("Enter Product ID: ")
    if ht.find(product_id) is not None:
        print(f'This Product ID is used!')
        return
    name = input("Enter Product Name: ")
    price = read_price("Enter Product Price: ")
    stock = read_stock("Enter Stock Quantity: ")
    product = Product(product_id, name, price, stock)

    slot = ht.insert(product.id, product)
    #duplicate was already ruled out above, so None here can only mean the table is full
    if slot is None:
        print(f'Hash table is full.')
    else:
        #keep the array in sync with the hash table
        arr.append(product)
        print(f'Product inserted successfully into slot [{slot}]')

def search_product(ht, arr):
    search_key = read_id("Enter Product ID to search: ")
    compare_search(ht, arr, search_key)

def edit_product(ht):
    search_key = read_id("Enter Product ID to edit: ")
    product = ht.find(search_key)
    if product is None:
        print(f'Product not exist to be edited.\n')
        return

    print(f'Current: {product}')
    print(f'Press Enter to keep the current value.')

    #ID is not editable: the slot position was decided by the ID
    new_name = input(f'New Name [{product.name}]: ')
    if new_name != '':
        product.name = new_name

    #Enter keeps the old value, negative or invalid input asks again
    product.price = read_price(f'New Price [{product.price:.2f}]: ', product.price)
    product.stock = read_stock(f'New Stock [{product.stock}]: ', product.stock)

    #the table and the array hold the SAME Product object
    #so changing it here updates both, no second update is needed
    print(f'Product edited!\n')

def delete_product(ht, arr):
    search_key = read_id("Enter Product ID to delete: ")
    #delete returns the removed Product, or None if it was not there
    product = ht.delete(search_key)
    if product is None:
        print(f'Product not exist to be deleted.\n')
        return
    #remove from the array too, otherwise the two no longer match
    arr.remove(product)
    print(f'Product deleted!\n')


#Pharmacy Inventory System
def showMenu(ht, arr):
    choice = 0
    while choice != 6:
        print("==== Pharmacy Inventory System ====")
        print("1. Insert Product")
        print("2. Search Product")
        print("3. Edit Product")
        print("4. Delete Product")
        print("5. Performance Experiment")
        print("6. Exit")
        try:
            choice = int(input("Enter choice: "))
        except ValueError:
            print(f'Invalid input! Please enter a valid choice (1 - 6).')
            continue

        if choice == 1:
            insert_product(ht, arr)
        elif choice == 2:
            search_product(ht, arr)
        elif choice == 3:
            edit_product(ht)
        elif choice == 4:
            delete_product(ht, arr)
        elif choice == 5:
            run_experiment()
        elif choice == 6:
            print(f'Exiting Inventory System. Goodbye!')
        else:
            print("Please enter a valid choice (1 - 6).")


def main():
    ht, arr = build_storage()
    showMenu(ht, arr)

if __name__ == '__main__':
    main()