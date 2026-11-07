#unweighted directed graph for a course-prerequisite system

class Course:
    def __init__(self, name, code, credit_hrs, lvl):
        self.courseName=name
        self.courseCode=code
        self.creditHours=credit_hrs
        self.level=lvl

    def __str__(self):
        return f'Code: {self.courseCode} | Name: {self.courseName} | Credit Hours: {self.creditHours} | Level: {self.level}'

"""
WHY USE A CLASS?
A class is not the data structure itself.
The data structures are the dictionary and the lists.
The Graph class wraps them together with the methods that manage them:
- the graph's data and actions stay in one place
- outside code uses methods, so the checks in addEdge always run
- each Graph object has its own separate data, so the class is reusable

ABSTRACTION VS ENCAPSULATION
Abstraction   = shows WHAT the object can do and hides HOW it does it.
Encapsulation = keeps data and methods inside the class and marks
                internal parts, such as _adjacency, as not for outside use.
"""
class Graph:

    def __init__(self):
        #Graph has one attribute: _adjacency
        #adjacency means direct connections between vertices
        #the underscore marks it as internal to the class (encapsulation)

        #this empty dictionary holds the WHOLE graph
        #key   = a vertex
        #value = a list of the vertices that this vertex points to

        #no separate vertex attribute is needed
        #the dictionary keys already are the vertices
        #self.vertices would store the same information twice
        self._adjacency = {}

    #abstraction: the caller only asks to add a vertex
    #vertex can be any suitable object, such as a string or Course
    #Graph never uses Course attributes, so it stays generic and reusable
    def addVertex(self, vertex):
        #a dictionary key stores one value, but a vertex can have many neighbours
        #the list lets one value hold all of those neighbours
        if vertex not in self._adjacency:
            self._adjacency[vertex]=[]
            return True
        else:
            return False

    #abstraction: the caller only asks to connect two vertices
    #the checks and list update stay hidden inside this method
    def addEdge(self, from_vertex, to_vertex):
        if from_vertex not in self._adjacency or to_vertex not in self._adjacency:
            return False
        if to_vertex in self._adjacency[from_vertex]:
            return False
        else:
            self._adjacency[from_vertex].append(to_vertex)
            return True

    #incoming = every vertex that points to this vertex
    #course example: incoming vertices are the prerequisites
    #return a list instead of printing, so the menu controls the display
    #the search loop stays hidden from the caller (abstraction)
    def listIncomingAdjacentVertex(self, vertex):
        result=[]
        #time complexity: O(V + E)
        for v in self._adjacency:
            if vertex in self._adjacency[v]:
                result.append(v)
        return result

    #outgoing = every vertex that this vertex points to
    def listOutgoingAdjacentVertex(self, vertex):
        #this needs no full scan because outgoing edges are stored directly
        return list(self._adjacency[vertex])

    #hasPath answers one question: starting from start, can we reach goal by following the arrows?
    #used by feature (c) to stop a cycle before a new edge is added
    #generic: it only follows the dictionary, it never looks inside Course
    #method: depth-first search (DFS), time complexity O(V + E)
    def hasPath(self, start, goal):
        #stack holds the vertices still waiting to be checked
        #pop() takes the last one added, so the search goes deep along one path first
        stack = [start]
        #visited holds the vertices already checked
        #without it, the loop could check the same vertex again and again
        visited = set()

        while stack:
            current = stack.pop()
            #reached the goal -> a path exists
            if current is goal:
                return True
            if current not in visited:
                visited.add(current)
                #put every vertex that current points to on the stack, to check later
                stack.extend(self._adjacency[current])

        #stack is empty: every reachable vertex was checked and goal was never met
        return False

def showMenu(courses, graph):
    print(f'==== University Course Prerequisite System ====')
    print(f'1. View All Courses')
    print(f'2. View Course Details')
    print(f'3. View Prerequisites of a Course')
    print(f'4. View Courses Unlocked by a Course')
    print(f'5. Add a Prerequisite to a Course')
    print(f'6. Exit')

    while True:
        try:
            choice = int(input("Enter choice: "))
            if choice == 1:
                viewAllCourses(courses)
            elif choice == 2:
                viewCourseDetails(courses)
            elif choice == 3:
                viewCoursePrerequisites(graph, courses)
            elif choice == 4:
                viewAdvancedCourse(graph, courses)
            elif choice == 5:
                addPrerequisite(graph, courses)
            elif choice == 6:
                print(f'Exiting program. Goodbye!')
                break
            else:
                print(f'Invalid choice. Please enter a number. (1 - 6)')

        except ValueError:
            print(f'Invalid choice. Please enter a number. (1 - 6)')
            continue

#display a list of all courses
def viewAllCourses(courses):
    print("\nAvailable Courses:")
    #courses is a dictionary: key = course code, value = Course object
    #.values() gives the Course objects directly
    for index, course in enumerate(courses.values()):
        print(f'{index+1}. {course.courseCode} - {course.courseName}')

#create course objects and return them in a list
def _load_course():
    c1 = Course("Introduction to Programming", "CS101",10, "core")
    c2 = Course("Data Structures", "CS201", 10, "core")
    c3 = Course("Algorithms", "CS301", 15, "core")
    c4 = Course("Database Systems", "CS302", 15, "core")
    c5 = Course("Software Engineering", "CS401", 20, "elective")
    return [c1,c2,c3,c4,c5]

#prompt: the question shown to the user
#default is "Enter Course Code: ", feature (c) passes its own prompts to ask for two different courses
#returns the Course object, or None when the code does not exist
def _findCourse(courses, prompt="Enter Course Code: "):
    course_code = input(prompt).strip().upper()

    course = courses.get(course_code)
    if course is None:
        print("Course not found.")

    return course

def viewCourseDetails(courses):
    result = _findCourse(courses)
    if result:
        print(result)

def viewCoursePrerequisites(graph, courses):
    result = _findCourse(courses)
    #_findCourse returns None when the user types a code that does not exist (e.g. CS999)
    #without this stop, result.courseCode below crashes: None has no courseCode
    if result is None:
        return

    prerequisites = graph.listIncomingAdjacentVertex(result)
    print(f'Prerequisites for {result.courseCode} - {result.courseName}:')
    #the course exists but the list can still be empty
    #e.g. CS101 is the first course, so nothing points to it
    if not prerequisites:
        print(f'- None')
        return
    for p in prerequisites:
        print(f'- {p.courseCode} ({p.courseName})')

def viewAdvancedCourse(graph, courses):
    result = _findCourse(courses)
    #same stop as above: None is not a key in the graph, so the lookup would raise KeyError
    if result is None:
        return

    advanced = graph.listOutgoingAdjacentVertex(result)
    print(f'Courses unlocked by {result.courseCode} - {result.courseName}')
    #the course exists but may unlock nothing, e.g. CS401 is the last course
    if not advanced:
        print(f'- None')
        return
    for a in advanced:
        print(f'- {a.courseCode} ({a.courseName})')

#optional feature (c): course X adds course Y as a prerequisite on-demand
#this creates a new incoming edge Y -> X (Y must be passed before X)
#flow:
#1. ask for X (the course that gets a new prerequisite)
#2. ask for Y (the prerequisite)
#3. reject 3 invalid cases: Y is X, Y is already a prerequisite, the edge would make a cycle
#4. otherwise add the edge Y -> X
#the rules live here, not in Graph, because "no cycles" is a course rule
#Graph stays generic and can be reused for graphs where cycles are allowed
def addPrerequisite(graph, courses):
    #course: X, the Course object that will receive the new prerequisite
    course = _findCourse(courses, "Enter the course code that needs a new prerequisite: ")
    if course is None:
        return
    #prerequisite: Y, the Course object that must be passed first
    prerequisite = _findCourse(courses, "Enter the prerequisite course code: ")
    if prerequisite is None:
        return

    #case 1: a course cannot require itself
    if prerequisite is course:
        print(f'A course cannot be its own prerequisite.')
    #case 2: Y already points to X, the edge exists
    elif course in graph.listOutgoingAdjacentVertex(prerequisite):
        print(f'{prerequisite.courseCode} is already a prerequisite of {course.courseCode}.')
    #case 3: cycle check
    #if X can already reach Y, then X is needed (directly or indirectly) before Y
    #adding Y -> X would close a loop: X before Y before X, so no student could ever start
    #e.g. CS101 -> CS201 exists; making CS201 a prerequisite of CS101 gives CS101 -> CS201 -> CS101
    elif graph.hasPath(course, prerequisite):
        print(f'Cannot add: {course.courseCode} is already required before {prerequisite.courseCode}, this would create a cycle.')
    #all checks passed: create the incoming edge Y -> X
    elif graph.addEdge(prerequisite, course):
        print(f'{prerequisite.courseCode} ({prerequisite.courseName}) is now a prerequisite of {course.courseCode} ({course.courseName}).')

#return the requisite code pairs
#each pair is one row from table in (prerequisite, course)
def _load_prerequisites():
    return [
        ("CS101", "CS201"),
        ("CS101", "CS301"),
        ("CS201", "CS301"),
        ("CS201", "CS302"),
        ("CS301", "CS401"),
        ("CS302", "CS401")
    ]

#insert all courses, then adds all edges
def build_course_system():
    course_list = _load_course()
    prerequisite_list = _load_prerequisites()

    g=Graph()
    courses = {}
    for c in course_list:
        g.addVertex(c)
        courses[c.courseCode] = c

    #edge loop
    for prerequisite_code, course_code in prerequisite_list:
        prerequisite = courses[prerequisite_code]
        course = courses[course_code]
        g.addEdge(prerequisite, course)

    #g stores connection between courses
    #courses code to understand course object
    return g, courses

def main():
    graph, courses = build_course_system()
    showMenu(courses, graph)

if __name__ == '__main__':
    main()