import string
   
"""  
#MyDict= { "AAA":"aaa" ,"BBB" :['bbb',"BBb"],"CCC":[] ,"DDD":["ddD"] ,"GGG" :['GgG',"ggg","Ggg'] }  
MyList = [["AAA" ,"aaa"] ,["BBB",'bbb'] ,["GGG","Ggg"],["CCC",None], ["BBB" ,"BBb"], ["DDD","ddD"],["GGG","GgG"],["GGG" ,"ggg"]]
        


if __name__ == "__main__":
    MyDict ={}
    for row in MyList:
        if row[0] in MyDict:
             MyDict[row[0]].extend( [row[1]] )
        else:
             MyDict.update({ row[0]: [row[1]] })  
        
    print  MyDict 
        

def f1 (c,*a):  
    print "c=" +str(c) 
    return a

g =["ggg","bbb"]

if __name__ == "__main__":
        print (f1( "aaa","bbb"))
        


def ret_status(status):
    if status =='UP':
        return {"status":"UP"}
    else :
        return {"status":"DOWN"}
    
if __name__ == "__main__":
     statuses ={}
     statuses.update(ret_status("UP"))
     print statuses
"""    
"""  
statuses =  {"DB2E":"UP","DF2E":"DOWN"}  
if __name__ == "__main__":
  for  daemon in   statuses :
      print daemon
     
"""    

q = '2345r2345'
print q[0]




    
     
     