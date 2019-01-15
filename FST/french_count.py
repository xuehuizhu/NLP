import sys
from fst import FST
from fsmutils import composewords
from fsmutils import trace

kFRENCH_TRANS = {0: "zero", 1: "un", 2: "deux", 3: "trois", 4:
                 "quatre", 5: "cinq", 6: "six", 7: "sept", 8: "huit",
                 9: "neuf", 10: "dix", 11: "onze", 12: "douze", 13:
                 "treize", 14: "quatorze", 15: "quinze", 16: "seize",
                 20: "vingt", 30: "trente", 40: "quarante", 50:
                 "cinquante", 60: "soixante", 100: "cent"}

kFRENCH_AND = 'et'

def prepare_input(integer):
    assert isinstance(integer, int) and integer < 1000 and integer >= 0, \
      "Integer out of bounds"
    return list("%03i" % integer)

def french_count():
    f = FST('french')

    f.add_state('start')
    f.add_state('first_zero')
    f.add_state('zero1')
    f.add_state('zero2')
    f.add_state('0')
    f.add_state('second_zero')
    f.add_state('1')      #0~9
    f.add_state('one')
    f.add_state('2')      #10~16, 70~76
    f.add_state('3')      #17,18,19, 77,78,79
    f.add_state('two')
    f.add_state('4')      #20,30,40,50,60
    f.add_state('5')      #21,31,41,51,61
    f.add_state('6')      #all others in 20~69 
    f.add_state('trans1')
    f.add_state('seven')
    f.add_state('trans2')
    f.add_state('7')     #71
    f.add_state('eight')
    f.add_state('nine')
    f.add_state('100')

    f.initial_state = 'start'
    # set all final states
    f.set_final('1')
    f.set_final('2')
    f.set_final('3')
    f.set_final('4')
    f.set_final('5')
    f.set_final('6')
    f.set_final('7')
    f.set_final('0')

    # add all arcs
    f.add_arc('trans1', '5', [], [kFRENCH_TRANS[1]])
    f.add_arc('trans2', '7', [], [kFRENCH_TRANS[11]])
    f.add_arc('eight', 'second_zero', [], [kFRENCH_TRANS[20]])
    f.add_arc('nine', 'one', [], [kFRENCH_TRANS[20]])
    f.add_arc('100', 'first_zero', [], [kFRENCH_TRANS[100]])

    for ii in xrange(10):
        if ii == 0:
           
            f.add_arc('start', 'first_zero', ['0'],[])
            f.add_arc('first_zero', 'second_zero', ['0'], [])
            f.add_arc('two', '4', ['0'], [])
            f.add_arc('seven', '2', ['0'], [kFRENCH_TRANS[10]])
            f.add_arc('second_zero', '1', ['0'], [])
        if ii != 0:
            f.add_arc('second_zero', '1', [str(ii)], [kFRENCH_TRANS[ii]])
        if ii == 1:
            f.add_arc('first_zero', 'one', ['1'], [])
            # add 'et' in special numbers
            f.add_arc('two', 'trans1', ['1'], [kFRENCH_AND])
            f.add_arc('seven', 'trans2', ['1'], [kFRENCH_AND])
            f.add_arc('start', 'first_zero', ['1'], [kFRENCH_TRANS[100]])
        if ii in xrange(7):
            f.add_arc('one', '2', [str(ii)], [kFRENCH_TRANS[10+ii]])
        else:
            s = kFRENCH_TRANS[10] + ' ' + kFRENCH_TRANS[ii]
            f.add_arc('one', '3', [str(ii)], [s])
            f.add_arc('seven', '3', [str(ii)], [s])
        if ii in range(2, 7):
            f.add_arc('first_zero', 'two', [str(ii)], [kFRENCH_TRANS[10*ii]])
            f.add_arc('seven', '2', [str(ii)], [kFRENCH_TRANS[10+ii]])
        if ii in range(2, 10):
            f.add_arc('two', '6', [str(ii)], [kFRENCH_TRANS[ii]])
            f.add_arc('start', '100', [str(ii)], [kFRENCH_TRANS[ii]])
        if ii == 7:
            f.add_arc('first_zero', 'seven', [str(ii)], [kFRENCH_TRANS[60]])
        if ii == 8:
            f.add_arc('first_zero', 'eight', [str(ii)], [kFRENCH_TRANS[4]])
        if ii == 9:
            f.add_arc('first_zero', 'nine', [str(ii)], [kFRENCH_TRANS[4]])
    
    f.add_arc('start', 'zero1', '0', [])
    f.add_arc('zero1', 'zero2', '0', [])
    f.add_arc('zero2', '0', '0', [kFRENCH_TRANS[0]])        #deal with zero seperately

    return f

if __name__ == '__main__':
    string_input = raw_input()
    user_input = int(string_input)
    f = french_count()
    if string_input:
        print user_input, '-->',
        print " ".join(f.transduce(prepare_input(user_input)))
