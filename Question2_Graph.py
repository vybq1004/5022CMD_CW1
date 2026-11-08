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
        #a vertex that is not in the graph has no outgoing edges
        #return an empty list instead of crashing with KeyError
        if vertex not in self._adjacency:
            return []
        #this needs no full scan because outgoing edges are stored directly
        return list(self._adjacency[vertex])

    #can we reach end_vertex from start_vertex by following the arrows?
    #used before adding a new edge, to stop a loop (cycle) being created
    #depth-first search: go as deep as possible along one path, then try the next
    #time complexity: O(V + E), every vertex and edge is visited at most once
    def hasPath(self, start_vertex, end_vertex):
        if start_vertex not in self._adjacency or end_vertex not in self._adjacency:
            return False
        #stack: vertices still waiting to be checked
        stack = [start_vertex]
        #visited: vertices already checked, so no vertex is checked twice
        visited = []
        while stack:
            current = stack.pop()
            if current == end_vertex:
                return True
            if current not in visited:
                visited.append(current)
                #add every vertex that current points to, so they are checked next
                for neighbour in self._adjacency[current]:
                    stack.append(neighbour)
        #every reachable vertex was checked and end_vertex was not found
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
    for index, course_name in enumerate(courses):
        print(f'{index+1}. {courses[course_name].courseCode} - {courses[course_name].courseName}')

#create course objects and return them in a list
def _load_course():
    c1 = Course("Introduction to Programming", "CS101",10, "core")
    c2 = Course("Data Structures", "CS201", 10, "core")
    c3 = Course("Algorithms", "CS301", 15, "core")
    c4 = Course("Database Systems", "CS302", 15, "core")
    c5 = Course("Software Engineering", "CS401", 20, "elective")
    return [c1,c2,c3,c4,c5]

#prompt: the question shown to the user, so the same function can ask for different courses
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
    #course code not found: "Course not found." already printed, go back to menu
    if result is None:
        return
    prerequisites = graph.listIncomingAdjacentVertex(result)
    print(f'Prerequisites for {result.courseCode} - {result.courseName}:')
    #no incoming edges -> entry-level course
    if not prerequisites:
        print(f'- None')
    for p in prerequisites:
        print(f'- {p.courseCode} ({p.courseName})')

def viewAdvancedCourse(graph, courses):
    result = _findCourse(courses)
    #course code not found: "Course not found." already printed, go back to menu
    if result is None:
        return
    advanced = graph.listOutgoingAdjacentVertex(result)
    print(f'Courses unlocked by {result.courseCode} - {result.courseName}')
    #no outgoing edges -> final course in the path
    if not advanced:
        print(f'- None')
    for a in advanced:
        print(f'- {a.courseCode} ({a.courseName})')

#advanced feature c: course X adds course Y as a prerequisite on demand
#this creates a new edge from Y to X (Y must be taken before X)
def addPrerequisite(graph, courses):
    course = _findCourse(courses, "Enter Course Code that needs the prerequisite: ")
    if course is None:
        return
    prerequisite = _findCourse(courses, "Enter Course Code of the prerequisite: ")
    if prerequisite is None:
        return

    #a course cannot be a prerequisite of itself
    if course is prerequisite:
        print(f'A course cannot be a prerequisite of itself.')
        return

    #if course already leads to prerequisite, adding prerequisite -> course makes a loop
    #e.g. CS101 leads to CS401, so CS401 cannot become a prerequisite of CS101
    #a loop would mean neither course could ever be taken first
    if graph.hasPath(course, prerequisite):
        print(f'Cannot add: {course.courseCode} is already required before {prerequisite.courseCode}, '
              f'this would create a loop.')
        return

    #addEdge returns False when the edge already exists
    if graph.addEdge(prerequisite, course):
        print(f'{prerequisite.courseCode} is now a prerequisite of {course.courseCode}.')
    else:
        print(f'{prerequisite.courseCode} is already a prerequisite of {course.courseCode}.')

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