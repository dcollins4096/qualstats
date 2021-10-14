import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas
import pdb
import numpy as np
nar=np.array
from importlib import reload
import qual
reload(qual)

#The files.
these_files = ["2014-02.xlsx", "2015-01.xlsx", "2015-02.xlsx", "2016-01.xlsx", "2016-02.xlsx", "2017-01.xlsx",\
               "2017-02.xlsx", "2018-01.xlsx", "2018-02.xlsx", "2019-01.xlsx", "2019-02.xlsx", "2020-01.xlsx", "2020-02.xlsx", "2021-01.xlsx", "2021-02.xlsx"]

#All students, indexed by student id
all_students={}

#the head of the student ID column
Unnamed0 =    'Unnamed: 0' 
for fname in these_files:   

    year = fname.split('.')[0] #year and qual, e.g. 2015-01 and 2015-02

    all_data = pandas.read_excel(fname,sheet_name = 'Sheet1')
    all_dict_list = all_data.to_dict(orient='records')
    full_head = all_data.keys()

    for record in all_dict_list:
        student_id = record[ Unnamed0]
        #Read the student ID.  Sanitize, some have leading 1 and 2.
        try:
            student_id = int(student_id) 
            student_id = np.mod(student_id , 1e8)  #some of them have leading 1 and 2
            student_id = int(student_id)
        except:
            if student_id != 'FSUSN':
                print("ERROR: skipping funny record", student_id)
                raise
            continue
        this_student = all_students.get(student_id, qual.student(student_id) )
        this_student.add_record( year, record, full_head)
        all_students[ student_id ] = this_student

# Flatten dict into arrays that are easy to query.

Nsits=[]
Nsits_nonzero=[] #remove tests with zero score, they probably didn't show up.
Scores = []
THRESH_EXAMINE=6
THRESH_SUB = 6
Ntaken=[]
Ntaken_trad = []
ids = []
#How many real sits of the qual?
for student_id in all_students:
    this_student = all_students[student_id]

    #Skip students that took it in 2014-02 (may have earlier tries) or 2021-02 (Maybe not done yet)
    if '2014-02' in this_student.quals or '2021-02' in this_student.quals:
        if len( this_student.quals) <7: #Lets keep the one student that took it 7 times.
            continue
    Nsits.append( len(this_student.quals.keys()))
    Nsits_nonzero.append(0)
    for year in this_student.quals:
        grade = this_student.quals[year].grade()
        if grade>0:
            Nsits_nonzero[-1]+=1

    Scores.append( this_student.quals[ this_student.last_qual].grade())

    this_student.count_tests(THRESHOLD=THRESH_SUB)
    Ntaken.append( this_student.Ntaken)
    Ntaken_trad.append( this_student.Ntaken_trad)


#Make those lists numpy arrays.
Nsits=nar(Nsits)
Scores=nar(Scores)
Ntaken=nar(Ntaken)
Ntaken_trad=nar(Ntaken_trad)
ids = nar(ids)

#
# plots of things.
#


#histogram
plt.clf()
plt.hist(Nsits_nonzero,bins=np.arange(0.5,8.5,1),histtype='step', label='All (excl no-shows)')
plt.hist(Nsits[Scores >= THRESH_EXAMINE],bins=np.arange(0.5,8.5,1),histtype='step', label='Passed with >%.1f'%(10*THRESH_EXAMINE))
plt.legend(loc=1)
plt.xlabel('N quals')
plt.ylabel('N students')
plt.savefig('Nsits.pdf')


#Extra Work
plt.clf()
passing = Scores >= THRESH_EXAMINE
TheX = Ntaken_trad[passing]

TheY = Ntaken[passing]
TheY = TheY - TheX
TheX = TheX/5
plt.scatter( TheX, TheY)
for NT in np.unique(TheX):
    these = TheY[ TheX == NT]
    for NN in np.unique(these):
        NNN= (these==NN).sum()
        plt.text( NT+0.25, NN-0.25, "%s"%NNN)

all_hurts=0
all_helps=0
for NT in np.unique(TheX):
    these = nar(TheY[ TheX == NT])
    print(len(these))
    helps = (these < 0).sum()
    hurts = (these > 0).sum()
    all_helps+=helps
    all_hurts+=hurts
    plt.text( NT, 4,   "%s"%helps, color='g')
    plt.text( NT, 4.5, "%s"%hurts, color='r')
plt.text(7.5,4,"%s"%all_helps,color='g')
plt.text(7.5,4.5,"%s"%all_hurts,color='r')
plt.text(0.5,4,"helps",color='g')
plt.text(0.5,4.5,"hurts",color='r')
plt.plot( TheX, TheX*0,c=[0.5]*3)
plt.xlabel('N quals')
plt.ylabel('N new tests')
plt.ylim(-7,5)
plt.savefig('WorkSavings.pdf')

#
# A few other plots
#
#N vs N, all tests
plt.clf()
plt.scatter( Ntaken_trad, Ntaken)
for NT in np.unique(Ntaken_trad):
    these = Ntaken[ Ntaken_trad == NT]
    for NN in np.unique(these):
        NNN= (these==NN).sum()
        plt.text( NT+0.5, NN-0.25, "%s"%NNN)
plt.plot( range(5,36), range(5,36),c=[0.5]*3)
plt.xlabel('N tests old')
plt.ylabel('N tests new')
plt.savefig('Ntaken.pdf')

#N vs N, only passing scores
plt.clf()
passing = Scores >= THRESH_EXAMINE
TheX = Ntaken_trad[passing]
TheY = Ntaken[passing]
plt.scatter( TheX, TheY)
for NT in np.unique(TheX):
    these = TheY[ TheX == NT]
    for NN in np.unique(these):
        NNN= (these==NN).sum()
        plt.text( NT+0.5, NN-0.25, "%s"%NNN)
plt.plot( range(5,36), range(5,36),c=[0.5]*3)
plt.xlabel('N tests old')
plt.ylabel('N tests new')
plt.savefig('Ntaken_passed.pdf')



