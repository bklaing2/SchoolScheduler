class schedule:

    def __init__(self, courses):
        self.courses = courses

    def __str__(self):
        string = ''
        for course in self.courses:
            string += '\n' + str(course) + '\n'

        return string

    def add_course(self, course):
        self.courses.append(course)
        self.courses.sort()

    def get_courses(self):
        return self.courses

    def is_valid(self):
        # TODO: Rest of function
        return True or False


class course:

    def __init__(self, subject, number):
        self.subject = subject.upper()
        self.number = int(number)
        self.sections = []

    def __str__(self):
        string = self.subject + ' ' + str(self.number) + ':'
        for section in self.sections:
            string += '\n  ' + str(section)

        return string

    def __lt__(self, other):
        return self.number < other.number if self.subject == other.subject else self.subject < other.subject

    def add_section(self, section):
        self.sections.append(section)
        self.sections.sort()


class section:

    def __init__(self, crn, number, seats_available):
        self.crn = int(crn)
        self.number = int(number)
        self.seats_available = int(seats_available)
        self.blocks = []

    def __str__(self):
        string = str(self.number) + ' ' + str(self.crn) + ':'
        for block in self.blocks:
            string += ' ' + str(block)

        return string

    def __lt__(self, other):
        return self.number < other.number

    def add_block(self, block):
        self.blocks.append(block)


class block:

    def __init__(self, start, end, days, location):
        self.start = start
        self.end = end
        self.days = days
        self.location = location
        # self.type = block_type

    def __str__(self):
        return str({'start': self.start, 'end': self.end, 'days': self.days, 'location': str(self.location)})

    def overlap(self, other):
        start = time_to_int(self.start)
        end = time_to_int(self.end)

        other_start = time_to_int(other.other_start)
        other_end = time_to_int(other.other_end)

        
        return True or False


class location:

    def __init__(self, building, room):
        self.building = building.upper()
        self.room = room
    
    def __str__(self):
        return str({'building': self.building, 'room': self.room})


def time_to_int(time):
    hour = int(time[0:2])
    minute = int(time[3:5]) / 60
    return hour + minute