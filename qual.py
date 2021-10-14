import numpy as np
import copy
import pdb
nar = np.array #this makes things numpy arrays, which is useful.



class qualon():
    """One test for one student.  All subject areas.
    Subject area is kept in an array self.head
    Scores are kept in an array self.scores.
    They are in the same order, so grading an individual subject area is easy"""
    def __init__(self, record, head):

        #The column for student ID becomes "Unnamed" in the sheet.
        Unnamed='Unnamed'

        #Sanitize the head row.  Pandas makes them say CM, CM.1, CM.2, QM.1, QM.2, etc.  I only want CM, QM.
        self.head = nar([hhh.split(".")[0] if not hhh.startswith('Unnamed') else Unnamed for hhh in head])
        self.head = self.head[ self.head != Unnamed]

        #take the scores out of the sheet.  Flag the ID columns with -1 so we can remove it.
        self.scores = nar( [ record[hhh] if not hhh.startswith('Unnamed') else -1 for hhh in head])

        #There are a lot of blanks, that get treated as NaNs by Pandas.  Blanks are zeros.
        iisnan = np.isnan(self.scores)
        self.scores[ iisnan] = 0

        self.scores = self.scores[ self.scores>=0]
        self.verbose=False

    def grade(self,flavor=None):
        """Grade the qualon.  If only one SubjectArea is required, use the *flavor* argument"""
        if flavor is not None:
            SL = self.head == flavor
            Nrecords = SL.sum()
        else:
            flavor = 'All'
            SL = slice(None)
            Nrecords = len(self.scores)
        grade = self.scores[SL].mean()
        if self.verbose:
            print("Grade %s %d %f"%(flavor,Nrecords, grade))
        return grade

class student():
    def __init__(self, student_id):
        self.student_id = student_id
        self.quals={}         #self.quals[year]=qualon
        self.passed={}        #self.passed[flavor]=year
        self.to_pass = None   #to be determined, will be a list
        self.Ntaken = 0       #counter for individual subject areas taken
        self.Ntaken_trad = 0  #counter for full tests.
        self.last_qual = None #the final qual taken
    def add_record(self,year,record,full_head):
        """add a test from the spreadsheet"""
        this_qualon = qualon( record, full_head)
        if self.to_pass is None:
            self.to_pass = set(this_qualon.head)
            self.all_flavors = set(this_qualon.head)
            self.last_qual = year
        self.last_qual = max([self.last_qual, year])
        self.quals[year]=this_qualon
    def grade_all(self):
        """Print the grades on each subject area for each test"""
        nf = len(self.all_flavors)
        output_string = "%6s"%" "+ "%4s"*nf%tuple(self.all_flavors) + "%4s\n"%'tot'
        years = sorted(self.quals.keys())
        for year in years:
            output_string += "%6s"%year
            for flavor in self.all_flavors:
                this_grade = self.quals[year].grade(flavor)
                output_string += "%4.1f"%this_grade
            this_grade = self.quals[year].grade()
            output_string += "%4.1f"%this_grade
            output_string += "\n"
        print(output_string)

    def count_tests(self, THRESHOLD=6, verbose=False):
        years = sorted(self.quals.keys())
        if verbose:
            pdb.set_trace()
        for year in years:
            self.Ntaken_trad += len(self.all_flavors)
            this_qualon = self.quals[year]
            passed = []
            for flavor in copy.copy(self.to_pass):
                self.Ntaken += 1
                this_grade = this_qualon.grade(flavor)
                if np.isnan(this_grade):
                    pdb.set_trace()
                if this_grade >= THRESHOLD:
                    self.to_pass.remove(flavor)

        self.Ntaken += len(self.to_pass)

