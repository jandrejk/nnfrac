
def main():

    a = Weight("a", ["a"], "tes1" )
    b = Weight("", [], "tes2" )
    c = Weight("b", [], "tes2" )

    d= (a + b)/ c
    print d.use



# class Weights():
#   def __init__(self, *args):

class Weight:

    def __init__(self, use, need, name=""):

        self.use = use
        self.need = need
        self.name = name

    def __add__(self, additional):

        new = useOperator("*", self.use, additional.use)

        return Weight( use =new, 
                       need = list( set(self.need + additional.need) ),
                       name =self.name )

    def __mul__(self, additional):

        new = useOperator("*", self.use, additional.use)

        return Weight( use =new, 
                       need = list( set(self.need + additional.need) ),
                       name =self.name )  

    def __div__(self, additional):

        new = useOperator("/", self.use, additional.use)

        return Weight( use =new, 
                       need = list( set(self.need + additional.need) ),
                       name =self.name )

      

def useOperator(operator, first, second):

    new= ""
    if first:
        new = first
    if new and second:
        new = "{0}{1}{2}".format(first, operator ,second)
    elif second:
        new = second

    return new


if __name__ == '__main__':
    main()